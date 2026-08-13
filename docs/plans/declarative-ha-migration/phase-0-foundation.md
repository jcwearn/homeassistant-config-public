# Phase 0: Repository Foundation & GitOps Infrastructure

**Goal**: Working repo structure and deployment pipeline that can push a minimal config to HA without breaking anything.

> Track task-level progress in [progress.md](progress.md). Update it as you complete items.

## Checklist

- [x] Initialize git repo, push to GitHub (private)
- [x] Create `.gitignore`
- [x] Generate dedicated age keypair (`~/.age/homeassistant.key`)
- [x] Create `.sops.yaml` with creation rules
- [x] Create minimal `config/configuration.yaml`
- [x] Create `config/secrets.sops.yaml` (encrypted, round-trip verified)
- [x] Create `scripts/export-from-ha.sh`
- [x] Create `scripts/deploy.sh`
- [x] Create empty package/directory structure
- [x] Create `docs/plans/` with phase documentation
- [x] Create `.github/workflows/validate.yaml` (PR: yamllint + check_config)
- [x] Create `.github/workflows/deploy.yaml` (merge to main: Tailscale → decrypt → rsync → reload)
- [x] Configure GitHub secrets (age private key, Tailscale auth key, HA SSH key)
- [x] Take full HA backup via Google Drive Backup before first deployment
- [x] First deploy: minimal config, verify HA restarts cleanly (fix PRs #3–#6)

## Configuration Files

| File | Purpose |
|------|---------|
| `.sops.yaml` | SOPS creation rules, age public key |
| `config/configuration.yaml` | Main HA config: homeassistant block, default_config, packages include |
| `config/secrets.sops.yaml` | Encrypted secrets (lat/long/elevation/timezone/alarm_pin) |
| `scripts/deploy.sh` | Manual deploy: decrypt → rsync → check → restart |
| `scripts/export-from-ha.sh` | Pull .storage/ data from HA for migration reference |

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `HA_SSH_HOST` | homeassistant.local | HA SSH host |
| `HA_SSH_USER` | root | HA SSH user |
| `HA_CONFIG_DIR` | /config | HA config path |
| `SOPS_AGE_KEY_FILE` | ~/.age/homeassistant.key | Age private key |

## Notes

- CI/CD workflows implemented in PR #2: `validate.yaml` (yamllint + HA config check) and `deploy.yaml` (Tailscale + SSH deploy)
- `configuration.yaml` uses `!include_dir_named packages` — each file in `packages/` becomes a domain
- `automation:` uses `!include_dir_merge_list` — each file returns a list
- `script:` uses `!include_dir_merge_named` — each file returns a dict
- Empty `automations/` and `scripts/` dirs have `.gitkeep` files; HA ignores non-YAML files
