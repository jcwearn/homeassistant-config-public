#!/usr/bin/env bash
set -euo pipefail

# Export current HA configuration data for migration reference
# Usage: ./scripts/export-from-ha.sh
#
# Pulls .storage files from HA to help migrate helpers, groups, and
# other UI-managed config to YAML packages.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HA_HOST="${HA_SSH_HOST:-homeassistant.local}"
HA_USER="${HA_SSH_USER:-root}"
HA_CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
EXPORT_DIR="$REPO_ROOT/.export"

mkdir -p "$EXPORT_DIR"

echo "==> Exporting .storage data from ${HA_USER}@${HA_HOST}..."

# Files needed for migration
STORAGE_FILES=(
  "core.config_entries"
  "core.entity_registry"
  "core.device_registry"
  "core.area_registry"
  "core.config"
  "input_boolean"
  "input_datetime"
  "input_number"
  "input_text"
  "timer"
  "group"
  "lovelace"
  "lovelace.dashboards"
)

for file in "${STORAGE_FILES[@]}"; do
  echo "  Fetching .storage/${file}..."
  scp "${HA_USER}@${HA_HOST}:${HA_CONFIG_DIR}/.storage/${file}" \
    "$EXPORT_DIR/${file}.json" 2>/dev/null || \
    echo "  Warning: ${file} not found, skipping"
done

echo ""
echo "==> Export complete. Files saved to: $EXPORT_DIR/"
echo ""
echo "These files contain your current HA configuration data."
echo "Use them as reference when building YAML packages in Phase 1."
echo ""
echo "NOTE: .export/ is gitignored. Do not commit these files."
