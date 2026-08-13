# Progress: Zigbee2MQTT v1.42 → v2.9.1 Migration

## Current Status: In Progress

| Phase | Status | Updated | Notes |
|-------|--------|---------|-------|
| 1. Z2M Config as Code | Complete | 2026-03-11 | PR #65; `configuration.yaml` (plaintext + placeholders) + `secrets.sops.yaml` (all fields encrypted). Deploy uses `sops decrypt --output-type dotenv` + `envsubst` (PR #66 fixed broken `sops exec-env` — removed in SOPS 3.8). |
| 2. Pre-upgrade Code Changes | Complete | 2026-03-11 | PR #65; all 6 illuminance renames done; v2 opt-in flags + `legacy_action_sensor: true` added to `configuration.yaml`. |
| 3. Pre-flight Checks | Complete | 2026-03-11 | Manual steps completed before upgrade. |
| 4. Upgrade Z2M Add-on | Complete | 2026-03-11 | Upgraded to 2.9.1-1; devices reconnected. |
| 5. Migrate Buttons to MQTT Device Triggers | In Progress | 2026-03-11 | PR #69 open; awaiting deploy + test. |

## Handoff Notes

### What's done
- PR #65 merged (or ready to merge) with Phases 1 & 2.
- `zigbee2mqtt/secrets.sops.yaml` was created with placeholder values for `z2m_mqtt_server`, `z2m_mqtt_user`, `z2m_mqtt_password` (`CHANGE_ME`) and real values for `z2m_pan_id` and `z2m_network_key`.
- **Before deploying**: fill in real MQTT credentials:
  ```bash
  SOPS_AGE_KEY_FILE=~/.age/homeassistant.key sops edit zigbee2mqtt/secrets.sops.yaml
  ```
  Values are in `config/secrets.sops.yaml` as `mqtt_user` / `mqtt_password`. The server URL is the local MQTT broker address.

### Config management approach
- `zigbee2mqtt/configuration.yaml` — plaintext, `${z2m_*}` placeholders, committed to repo
- `zigbee2mqtt/secrets.sops.yaml` — flat SOPS file, all fields encrypted
- Deploy: `sops decrypt --output-type dotenv secrets.sops.yaml` → source into env → `envsubst < configuration.yaml > configuration.rendered.yaml` → rsync single file to remote as `configuration.yaml`
- `devices.yaml` and `groups.yaml` on the server are **never touched** by deploy

### Phase 5 button migration
7 button automation files need rewriting after upgrade. Device IDs must be collected from HA UI after each button is pressed once in v2:
- `button_master_bathroom.yaml` — single, hold
- `button_master_bedroom.yaml` — single, double, hold
- `button_kitchen.yaml` — single
- `button_living_room_fan.yaml` — 1_single–4_single
- `button_living_room_lights.yaml` — 1_single, 1_double, 2_single–4_single
- `button_living_room_modes.yaml` — 1_single–4_single

New trigger format:
```yaml
trigger:
  - trigger: device
    domain: mqtt
    device_id: <ha_device_id>
    type: action
    subtype: single
```
Also remove `legacy_action_sensor: true` from `configuration.yaml` in the same PR.
