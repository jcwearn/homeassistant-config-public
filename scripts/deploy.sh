#!/usr/bin/env bash
set -euo pipefail

# Deploy Home Assistant config via SSH
# Usage: ./scripts/deploy.sh [--dry-run] [--no-backup]
#
# Requires:
#   - SOPS age key at ~/.age/homeassistant.key
#   - SSH access to HA (via Tailscale or LAN)

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
trap 'rm -f "$REPO_ROOT/config/secrets.yaml" "$REPO_ROOT/zigbee2mqtt/configuration.rendered.yaml"' EXIT
HA_HOST="${HA_SSH_HOST:-homeassistant.local}"
HA_USER="${HA_SSH_USER:-root}"
HA_CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
SOPS_KEY="${SOPS_AGE_KEY_FILE:-$HOME/.age/homeassistant.key}"
DRY_RUN=false
BACKUP=true
KEEP_BACKUPS=5

for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY_RUN=true ;;
    --no-backup)  BACKUP=false ;;
    *) echo "Unknown argument: $arg"; exit 1 ;;
  esac
done

echo "==> Decrypting secrets..."
SOPS_AGE_KEY_FILE="$SOPS_KEY" sops decrypt \
  "$REPO_ROOT/config/secrets.sops.yaml" > "$REPO_ROOT/config/secrets.yaml"

echo "==> Rendering Z2M config..."
_z2m_env="$(mktemp)"
SOPS_AGE_KEY_FILE="$SOPS_KEY" sops decrypt \
  --output-type dotenv \
  "$REPO_ROOT/zigbee2mqtt/secrets.sops.yaml" > "$_z2m_env"
while IFS= read -r _line; do export "$_line"; done < "$_z2m_env"
rm -f "$_z2m_env"
envsubst < "$REPO_ROOT/zigbee2mqtt/configuration.yaml" > "$REPO_ROOT/zigbee2mqtt/configuration.rendered.yaml"

RSYNC_OPTS=(
  -avz
  --delete
  --filter='+ /automations/***'
  --filter='+ /packages/***'
  --filter='+ /scripts/***'
  --filter='+ /dashboards/***'
  --filter='+ /themes/***'
  --filter='+ /configuration.yaml'
  --filter='+ /ui-lovelace.yaml'
  --filter='+ /secrets.yaml'
  --filter='- *'
)

if $BACKUP && ! $DRY_RUN; then
  BACKUP_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
  BACKUP_DIR=".deploy-backup/$BACKUP_TIMESTAMP"
  echo "==> Creating backup dir: ${HA_CONFIG_DIR}/${BACKUP_DIR}"
  ssh "${HA_USER}@${HA_HOST}" "mkdir -p ${HA_CONFIG_DIR}/${BACKUP_DIR}"
  RSYNC_OPTS+=(--backup "--backup-dir=$BACKUP_DIR")
fi

if $DRY_RUN; then
  RSYNC_OPTS+=(--dry-run)
  echo "==> DRY RUN: showing what would be synced..."
fi

echo "==> Ensuring rsync is available on remote..."
ssh "${HA_USER}@${HA_HOST}" "command -v rsync >/dev/null 2>&1 || apk add --no-cache rsync"

echo "==> Syncing config to ${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/"
rsync "${RSYNC_OPTS[@]}" \
  "$REPO_ROOT/config/" \
  "${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/"

echo "==> Syncing Z2M config to ${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/zigbee2mqtt/"
Z2M_RSYNC_OPTS=(-avz)
if $DRY_RUN; then
  Z2M_RSYNC_OPTS+=(--dry-run)
fi
rsync "${Z2M_RSYNC_OPTS[@]}" \
  "$REPO_ROOT/zigbee2mqtt/configuration.rendered.yaml" \
  "${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/zigbee2mqtt/configuration.yaml"

if ! $DRY_RUN; then
  if $BACKUP; then
    echo "==> Pruning old backups (keeping last ${KEEP_BACKUPS})..."
    ssh "${HA_USER}@${HA_HOST}" \
      "cd ${HA_CONFIG_DIR}/.deploy-backup && ls -dt */ 2>/dev/null | tail -n +\$((${KEEP_BACKUPS}+1)) | xargs rm -rf"
  fi

  echo "==> Ensuring required directories exist..."
  ssh "${HA_USER}@${HA_HOST}" "mkdir -p ${HA_CONFIG_DIR}/snapshots"

  echo "==> Checking configuration..."
  ssh "${HA_USER}@${HA_HOST}" "ha core check"

  echo "==> Restarting Home Assistant..."
  ssh "${HA_USER}@${HA_HOST}" "ha core restart"

  echo "==> Deploy complete!"
else
  echo "==> Dry run complete. No changes applied."
fi
