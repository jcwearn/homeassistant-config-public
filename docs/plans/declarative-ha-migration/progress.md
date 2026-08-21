# Migration Progress Tracker

> **For agents**: Update this file as you complete work. Mark items done with dates,
> add notes about decisions or issues, and update "Current Focus" so the next agent
> knows exactly where to pick up.

## Current Focus

**Phase**: 2 — Dashboard & Frontend Migration
**Status**: YAML lovelace config created, Alarm dashboard exported, PR open.
**Next action**: Merge PR, deploy, then follow post-deploy verification and cleanup steps in PR description.

## Phase Progress

### Phase 0: Repository Foundation

| Task | Status | Date | PR |
|------|--------|------|----|
| Initialize git repo + push to GitHub (private) | Done | 2026-02-24 | [#1](https://github.com/jcwearn/homeassistant-config/pull/1) |
| Create `.gitignore` | Done | 2026-02-24 | #1 |
| Generate dedicated age keypair (`~/.age/homeassistant.key`) | Done | 2026-02-24 | #1 |
| Create `.sops.yaml` with creation rules | Done | 2026-02-24 | #1 |
| Create minimal `config/configuration.yaml` | Done | 2026-02-24 | #1 |
| Create `config/secrets.sops.yaml` (encrypted, verified) | Done | 2026-02-24 | #1 |
| Create `scripts/deploy.sh` | Done | 2026-02-24 | #1 |
| Create `scripts/export-from-ha.sh` | Done | 2026-02-24 | #1 |
| Create empty package/directory structure | Done | 2026-02-24 | #1 |
| Create `docs/plans/` with phase docs | Done | 2026-02-24 | #1 |
| Create `.github/workflows/validate.yaml` | Done | 2026-03-05 | #2 |
| Create `.github/workflows/deploy.yaml` | Done | 2026-03-05 | #2 |
| Port live `configuration.yaml` (all integrations) | Done | 2026-03-05 | #2 |
| Fix secrets encryption (alarm_pin, mqtt_*) | Done | 2026-03-05 | #2 |
| Add `legacy-config/` to `.gitignore` | Done | 2026-03-05 | #2 |
| Create `config/themes/.gitkeep` | Done | 2026-03-05 | #2 |
| Configure GitHub secrets | Done | 2026-03-05 | Manual (see PR #2 description) |
| Take full HA backup before first deploy | Done | 2026-03-05 | Google Drive Backup |
| First deploy: verify HA restarts cleanly | Done | 2026-03-05 | Fix PRs #3–#6 |

### Phase 1: Core YAML Configuration

| Task | Status | Date | PR |
|------|--------|------|----|
| Run `export-from-ha.sh` to pull .storage data | Done | 2026-03-05 | — |
| Create `packages/helpers.yaml` (11 input/timer helpers) | Done | 2026-03-05 | #8 |
| Create `packages/groups.yaml` (19 platform + 7 legacy) | Done | 2026-03-05 | #8 |
| Create `packages/alarm.yaml` | Done | 2026-03-05 | #8 |
| Create `packages/presence.yaml` (mqtt_room sensor) | Removed | 2026-03-05 | #8 |
| Create `packages/system.yaml` | Removed | 2026-03-05 | #8 |
| Slim down `configuration.yaml` | Done | 2026-03-05 | #8 |
| Extract homekit to `packages/homekit.yaml` | Done | 2026-03-05 | #8 |
| Create `packages/scenes.yaml` (3 legacy scenes) | Done | 2026-03-05 | #9 |
| Deploy + verify entities exist | Not started | | |
| Delete UI-managed helpers | Not started | | |
| Verify no duplicate entities | Not started | | |
| Verify Node-RED flows still work | Not started | | |

### Phase 2: Dashboard & Frontend

| Task | Status | Date | PR |
|------|--------|------|----|
| Export dashboard YAML + storage files | Done | 2026-03-05 | — |
| Set up `lovelace:` in configuration.yaml | Done | 2026-03-05 | #10 |
| Create `ui-lovelace.yaml` (default dashboard) | Done | 2026-03-05 | #10 |
| Create `dashboards/alarm.yaml` | Done | 2026-03-05 | #10 |
| Document HACS inventory | Done | 2026-03-05 | #10 |
| Deploy + verify dashboards render | Not started | | |
| Delete unused UI dashboards | Not started | | |
| Remove UI Lovelace Minimalist | Not started | | |

### Phase 3: Service Migration to k3s

**Status: Dropped** — k3s downtime shouldn't affect HA availability. Services stay as HA add-ons.

### Phase 4: Automation Migration from Node-RED

**Status: Moved** — Broken out into its own dedicated plan at [`docs/plans/node-red-automation-migration/`](../node-red-automation-migration/plan.md).

## Tech Debt / Follow-ups

Revisit between phases or when convenient. Sorted by priority.

### High — Security

| Item | Source | Notes |
|------|--------|-------|
| Rotate AWS credentials exposed in `flows.json` | Agent notes 2026-02-24 | Node-RED export contains plaintext AWS creds; file is gitignored and was never committed, but credentials are still active |
| Revoke HA API token from planning session | Agent notes 2026-02-24 | Profile > Security > Long-Lived Access Tokens |
| Confirm the pre-rotation `tailscale_webhook_id` no longer resolves | Agent notes 2026-08-13 | Rotated in `9844af4`, but the old value sits in git history in plaintext. Verify in the Tailscale admin console that it is dead |

### Medium — Correctness / Reliability

| Item | Source | Notes |
|------|--------|-------|
| Add `unique_id` to platform groups | Agent notes 2026-03-05 | Groups defined via `group:` in configuration.yaml lack unique_id; may cause issues with UI editing or entity registry |
| Validate workflow push trigger redundancy | PR #2 review | Validate runs on push to main redundantly with deploy; consider removing or making deploy `needs: validate` |
| Pin SOPS binary checksum in deploy workflow | Agent notes 2026-03-05 | Download integrity not verified beyond HTTPS |

### Low — Hardening / Polish

| Item | Source | Notes |
|------|--------|-------|
| SSH `known_hosts` pinning | PR #2 review | Currently using `ssh-keyscan` (TOCTOU); acceptable on Tailscale but could pre-populate from a pinned host key |
| Deploy script path quoting | PR #2 review | `$BACKUP_DIR` unquoted in SSH command; harmless with current timestamp format but fragile |
| Deploy script backup pruning | PR #2 review | Replace `ls \| tail \| xargs rm -rf` with `find`-based approach; add `xargs -r` to skip empty input |
| `yamllint` line-length reduction | PR #2 review | Consider reducing from 256 to 120 |
| Document `--backup-dir` relative path | PR #2 review | rsync `--backup-dir` is relative to destination dir, not CWD; worth a comment in `deploy.sh` |

## Agent Notes

> Add notes here about decisions made, issues encountered, or context that future
> agents need. Prefix each entry with a date.

### 2026-08-21 (dropped the mock-secrets action)

- Renovate flagged `golles/mock-yaml-secrets-action` as abandoned. The repo is
  actually still maintained (last commit 2026-08-02), but `abandonments:recommended`
  — inherited via `config:best-practices` in the shared `jcwearn/renovate-config`
  preset — uses a 1-year threshold against the latest *release*, and v1.1.2 is from
  2024-10-18. No maintained alternative action exists.
- Replaced it with `.github/scripts/mock-secrets.py`, a local reimplementation.
  Output was diffed against the pinned upstream bundle running on this config:
  identical. Two deliberate differences — the script overwrites rather than appends
  (so local re-runs don't duplicate keys) and emits keys sorted rather than in
  directory-walk order.
- **Closes the "mock secrets JSON regex ordering" follow-up**: upstream `applyRules`
  returns on the first matching rule, so it is first-match-wins and the existing
  ordering in `mock-secrets-config.json` (specific literals before the generic
  `.*password.*` / `.*token.*` regexes) is correct. The local script preserves that
  ordering via Python dict insertion order.

### 2026-08-13 (secret scrub ahead of public publishing)
- **The alarm PIN was rotated.** The previous value had been recorded in plaintext in this file (in the 2026-03-05 note about moving the code to `!secret alarm_pin`) and is therefore in git history across most commits. Treat the old code as burned. Never write a secret's value into these notes — record only that it changed and where it lives.
- Redacted the Zigbee PAN ID from the z2m migration notes. It is not urgent on its own: `pan_id` plus `channel` cannot join a network without `z2m_network_key`, which is SOPS-encrypted and was never exposed. **No re-pairing needed.**
- Replaced hardcoded LAN addresses in `.mcp.json`, `scripts/deploy.sh`, `scripts/export-from-ha.sh`, and `scripts/ha-mcp-server.py` with the `homeassistant.local` mDNS default. All four still honor `HA_SSH_HOST` / `HA_HOST`, so set those if mDNS doesn't resolve.
- This repo **stays private and canonical**. A filtered snapshot publishes to a public counterpart repo via CI — see `.github/workflows/publish.yaml` and `.publicignore`. Anything committed here reaches that public tree unless `.publicignore` excludes it.
- `config/.storage/core.device_registry` (1,356 devices, MACs, serials, area layout) was committed on `chore/bootstrap-device-registry` and remains reachable through the closed PR refs for #79 and #77. That is survivable only because this repo stays private — it is why publishing in place was rejected.

### 2026-08-08 (http YAML deprecation)
- Removed the `http:` block from `configuration.yaml`. HA 2026.8 imported it into a UI config entry and deprecated the YAML form (ignored from 2027.2.0). Settings > System > Network > HTTP server holds the settings now — verified Trust X-Forwarded-For on and all four Envoy proxy IPs (stored as `/32`) present before removing.
- **The reverse-proxy config is no longer in git.** It lives in `.storage/core.config_entries` on the HA host, outside this repo's GitOps flow. A rebuild-from-scratch restores it only from an HA backup — otherwise external access via `home.wearn.dev` breaks with "Received X-Forwarded-For header from untrusted proxy" until the four IPs are re-entered by hand in the UI. If the Envoy gateway pod IPs ever change, they must be updated in the UI, not here.
- The **Home Assistant URL** card on the same page is still locked by YAML — that's `external_url` under the `homeassistant:` key, unrelated to this deprecation, and it stays in `configuration.yaml`.
- The HTTP server card can fail to render on a stale frontend cache; a hard refresh brings it back.

### 2026-03-05 (Phase 2 — dashboards)
- Switched lovelace to `mode: yaml` with Alarm as a YAML-declared sub-dashboard at `dashboards/alarm.yaml`.
- Created `ui-lovelace.yaml` as the required default dashboard (minimal placeholder).
- Alarm dashboard exported from `.storage/lovelace.dashboard_alarm` JSON and converted to YAML. Uses `card_mod` (HACS) for full-viewport kiosk-style alarm panel with enlarged keypad buttons.
- `kiosk_mode` in the Alarm view config requires the `kiosk-mode` HACS integration or card — verify it still works post-deploy. If not, it can be removed (it hides header/sidebar for a dedicated alarm panel).
- HACS resources (8 total) remain managed via `.storage/lovelace_resources` — no explicit `resources:` section needed in lovelace config. HACS writes to storage independently of lovelace mode.
- Plan originally listed 9 HACS resources including browser_mod, but the actual `.storage/lovelace_resources` export only contains 8. browser_mod may be installed as an integration but not registered as a frontend resource.
- Post-deploy cleanup: delete 7 unused UI dashboards (Remote, Cameras, home, Map, Mobile, Areas, Alarm Testing), delete old storage-based Alarm dashboard (replaced by YAML), remove UI Lovelace Minimalist from HACS.
- Rollback: remove `lovelace:` block from configuration.yaml and restart. `.storage/` is untouched by deploys, so UI dashboards are preserved.

### 2026-03-05 (Phase 1 — scenes fix)
- Restored 3 manually-created scenes that were dropped in Phase 0 when `scene: !include scenes.yaml` was removed from `configuration.yaml`. The scenes were incorrectly categorized as UI-only, but they were legacy YAML scenes needed by automations.
- Scene `id:` fields preserved — they match `unique_id` in the entity registry (critical for `scene.dining_room_board_games` which was renamed in UI and doesn't match the scene name).
- Used `color_temp_kelvin` instead of deprecated mireds-based `color_temp`. Stripped all runtime metadata.

### 2026-03-05 (Phase 1)
- Created 3 package files: helpers.yaml (11 helpers from .export/ data), groups.yaml (9 light + 3 cover + 7 binary_sensor platform groups + 7 legacy groups), alarm.yaml. Removed presence.yaml (ESPresense mqtt_room sensor — integration no longer in use).
- Removed system.yaml (logger/recorder/history) — it introduced net-new behavior (recorder/history exclusions for call_service events and sensor.sun_*) that wasn't in the original config. Migration goal is to extract existing config, not add new settings.
- Removed alarm_control_panel, sensor, light, cover, binary_sensor, and group blocks from configuration.yaml. It's now a thin shell: core settings, homekit bridge, and include directives.
- Helper names in YAML use human-readable format (e.g., "Guest Override") vs .storage slugs (e.g., "guest_override"). Entity IDs are unchanged since they derive from YAML keys.
- Post-merge: deploy, verify entities, delete UI helpers via Settings > Helpers, restart, verify no `_2` duplicates, smoke-test Node-RED.
- 12 switch_as_x helpers (10 light, 2 fan) are config-entry-only and stay UI-managed. Not counted in the 11 YAML helpers.
- Extracted homekit bridge config (97 lines) from configuration.yaml into packages/homekit.yaml. Pure cut-and-paste, no content changes. Uses `!secret alarm_pin` which resolves globally from packages. configuration.yaml is now 43 lines.
- Post-deploy cleanup: delete orphan `/config/groups.yaml` on HA server (`ssh "$HA_SSH_USER@$HA_SSH_HOST" "rm /config/groups.yaml"`). rsync won't remove it since deploy runs without `--delete`.

### 2026-03-05
- Ported full live `configuration.yaml` from `legacy-config/`: tts, frontend themes, http trusted_proxies, homekit bridge (full entity filter), alarm_control_panel, light/cover/binary_sensor groups, mqtt_room sensor, zone, and groups.
- Dropped `spotcast:` and `sensor: platform: peloton` (no longer used). Dropped `scene: !include scenes.yaml` (UI-generated, lives in `.storage/`).
- Replaced the hardcoded alarm code in homekit entity_config with `!secret alarm_pin`. Replaced hardcoded lat/long in zone with `!secret` refs.
- Inlined groups from `groups.yaml` directly into `configuration.yaml` as `group:` entries. Phase 1 will refactor into packages.
- Fixed `.sops.yaml` `encrypted_regex` to include `alarm_pin`, `mqtt_user`, `mqtt_password`. Re-encrypted `secrets.sops.yaml` with corrected values (elevation=300, lat/long as floats matching live config).
- Added `legacy-config/` to `.gitignore` (contains flows.json with AWS creds and live config files).
- Created `config/themes/.gitkeep` for `!include_dir_merge_named themes` directive.
- Updated mock-secrets-config.json with `alarm_pin`, `mqtt_user`, `mqtt_password` for CI.
- Added `.github/workflows/mock-secrets-config.json` to validate workflow paths filter.
- GitHub Actions not triggering for new pushes — likely because workflow file doesn't exist on `main` yet. Previous run (6eb94fb) passed. Local yamllint passes. CI should work once PR is merged and workflow exists on main.
- Created CI/CD workflows in PR #2: `validate.yaml` (yamllint + HA config check on PRs) and `deploy.yaml` (Tailscale + SSH deploy on push to main).
- Added `.yamllint.yaml` tuned for HA conventions (truthy on/off, 256 char line length, no document-start).
- `secrets.sops.yaml` excluded from yamllint (SOPS-generated indentation can't be controlled).
- Mock secrets config at `.github/workflows/mock-secrets-config.json` generates fake `secrets.yaml` for CI config checks.
- PR #2 review fixes: removed 3 duplicate HomeKit fan entities, fixed `main_floor_bathroom_light` → `main_floor_bathroom_lights` typo in group.
- Enhanced `deploy.sh` with rsync `--backup`/`--backup-dir` to `.deploy-backup/<timestamp>/` instead of permanently deleting files. Added `--no-backup` flag and auto-pruning (keeps last 5).
- Advisory items moved to Tech Debt / Follow-ups section.
- Remaining manual steps (Tailscale ACL + OAuth client, SSH key, GitHub secrets) completed 2026-03-05.

### 2026-02-24
- Repo initialized on `feat/phase-0-foundation` branch, PR #1 opened.
- Age keypair for this repo is at `~/.age/homeassistant.key`. The key in `~/.config/sops/age/keys.txt` belongs to k3s-cluster — do NOT use it for this repo. Always set `SOPS_AGE_KEY_FILE=~/.age/homeassistant.key` when running sops commands.
- `flows.json` in repo root is a Node-RED export containing plaintext AWS credentials. Gitignored. Tracked in Tech Debt (High).
- HA API token from planning session should be revoked. Tracked in Tech Debt (High).
- CI/CD workflows deferred to a follow-up session. Manual deploy via `scripts/deploy.sh` is ready.
- HA SSH access is `root@` the host in `HA_SSH_HOST` (via Tailscale or LAN). The SSH add-on is Terminal & SSH v10.0.1.

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Dedicated age keypair separate from k3s-cluster | Keeps HA secrets isolated; different lifecycle and access patterns |
| 2026-02-24 | Manual deploy script before CI/CD | Get basic deploy working first, add GH Actions later |
| 2026-02-24 | `!include_dir_named packages` pattern | Groups related config (automations + helpers + scripts) per domain |
| 2026-02-24 | Hue scenes stay on bridge | 80 scenes are bridge-native, auto-discovered, cannot be YAML-managed |
| 2026-02-24 | Zigbee2MQTT stays as HA add-on | Yellow's built-in radio requires local USB access |
| 2026-03-05 | Phase 3 (k3s services) dropped | k3s downtime shouldn't affect HA; services stay as HA add-ons |
| 2026-03-05 | Phase 4 (automations) moved to own plan | Too large for a sub-phase; needs dedicated catalog + 9-phase plan |
| 2026-08-08 | `http` config becomes UI-managed | YAML form deprecated upstream in 2026.8, ignored from 2027.2.0; no way to keep it declarative. Trusted proxies now depend on HA backups, not git |
