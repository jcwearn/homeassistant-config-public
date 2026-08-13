# Plan: Zigbee2MQTT v1.42 → v2.9.1 Migration + Config Management

## Context

Running Zigbee2MQTT v1.42.0-2 (HA add-on) with ~51 Zigbee devices via a ConBee II USB adapter. A previous v2 upgrade attempt broke things. Now that all automations are in YAML, we can safely plan the upgrade. The plan also establishes Z2M config as a first-class repo citizen with secrets handling and safe deployment (without clobbering Z2M-managed files like `devices.yaml`).

---

## Z2M File Ownership

| File | Owned by | In repo | Deploy? |
|------|----------|---------|---------|
| `zigbee2mqtt/configuration.yaml` | **User** | Yes (plaintext with `${var}` placeholders) | ✅ Yes — rendered via envsubst before rsync |
| `zigbee2mqtt/secrets.sops.yaml` | **User** | Yes (SOPS-encrypted) | ✅ Used at deploy time only |
| `zigbee2mqtt/devices.yaml` | **Z2M** (updated when pairing via UI) | No | ❌ Never overwrite |
| `zigbee2mqtt/groups.yaml` | **Z2M** (updated when groups created) | No | ❌ Never overwrite |
| `zigbee2mqtt/database.db` | Z2M runtime | No (gitignored) | ❌ |
| `zigbee2mqtt/state.json` | Z2M runtime | No (gitignored) | ❌ |
| `zigbee2mqtt/coordinator_backup.json` | Z2M runtime | No (gitignored) | ❌ |

---

## Breaking Changes Affecting This Config

### 1. `illuminance_lux` entity renamed → `illuminance`

In v2, `sensor.*_illuminance_lux` is removed; `sensor.*_illuminance` becomes the canonical lux entity. 6 files updated in Phase 2.

### 2. Action sensors disabled by default → migrate to MQTT device triggers (Phase 5)

In v2, `sensor.*_action` entities are off by default. 7 button automation files will migrate to `trigger: device, domain: mqtt` triggers. `legacy_action_sensor: true` is a temporary bridge until Phase 5 is complete.

**Affected files:**
- `config/automations/buttons/button_master_bathroom.yaml` — `single`, `hold`
- `config/automations/buttons/button_master_bedroom.yaml` — `single`, `double`, `hold`
- `config/automations/buttons/button_kitchen.yaml` — `single`
- `config/automations/buttons/button_living_room_fan.yaml` — `1_single`–`4_single`
- `config/automations/buttons/button_living_room_lights.yaml` — `1_single`, `1_double`, `2_single`–`4_single`
- `config/automations/buttons/button_living_room_modes.yaml` — `1_single`–`4_single`

**New trigger format** (device IDs known only post-upgrade):
```yaml
trigger:
  - trigger: device
    domain: mqtt
    device_id: <ha_device_id>   # HA Settings → Devices → device URL
    type: action
    subtype: single              # exact action string
```

`choose` conditions currently checking `trigger.to_state.state == 'X'` will be replaced with `condition: trigger` + trigger IDs.

---

## Phases

### Phase 1: Z2M Config as Code
- **Files involved**: `zigbee2mqtt/configuration.yaml`, `zigbee2mqtt/secrets.sops.yaml`, `.sops.yaml`, `.gitignore`, `scripts/deploy.sh`
- `configuration.yaml` committed in plaintext with `${z2m_*}` placeholders
- `secrets.sops.yaml` is a flat SOPS file (all fields encrypted): `z2m_mqtt_server`, `z2m_mqtt_user`, `z2m_mqtt_password`, `z2m_pan_id`, `z2m_network_key`
- Deploy uses `sops exec-env` + `envsubst` to render config, then rsyncs single file to remote
- **Acceptance criteria**: `deploy.sh --dry-run` shows only `configuration.yaml` being synced to `zigbee2mqtt/`; `devices.yaml` on server is untouched

### Phase 2: Pre-upgrade Code Changes
- **Files involved**: 6 light automation YAML files, `zigbee2mqtt/configuration.yaml`
- Rename `_illuminance_lux` → `_illuminance` in all `condition: numeric_state` entries:
  - `lights_office.yaml:18` — `sensor.office_sensor_motion_illuminance_lux`
  - `lights_main_floor.yaml:40` — `sensor.main_floor_stairwell_sensor_motion_02_illuminance_lux`
  - `lights_upstairs_hallway.yaml:9` — `sensor.roof_stairwell_sensor_motion_01_illuminance_lux`
  - `lights_guest_bedroom.yaml:16` — `sensor.guest_bedroom_sensor_motion_illuminance_lux`
  - `lights_master_bedroom.yaml:22` — `sensor.master_bedroom_sensor_motion_illuminance_lux`
  - `lights_basement.yaml:16,30` — `sensor.basement_stairwell_sensor_motion_01_illuminance_lux`
- Add v2 opt-in settings to `configuration.yaml`:
  - `homeassistant_legacy_entity_attributes: false`
  - `homeassistant_legacy_triggers: false`
  - `legacy_api: false`
  - `legacy_availability_payload: false`
  - `device_options.legacy: false`
  - `device_options.legacy_action_sensor: true` (temporary bridge)
- **Acceptance criteria**: `ha core check` passes after deploy

### Phase 3: Pre-flight Checks (manual, on HA server)
- Verify HA MQTT integration status topic is `homeassistant/status`
  (HA → Settings → Integrations → MQTT → Configure → Birth/Will message topic)
- Take a full HA backup (Supervisor → Backups)
- Note current Z2M device list for post-upgrade comparison
- **Acceptance criteria**: Backup exists; MQTT status topic confirmed

### Phase 4: Upgrade Z2M Add-on
1. HA → Add-on Store → Zigbee2MQTT → update to 2.9.1-1
2. Watch startup logs; confirm devices reconnect
3. Review `/config/zigbee2mqtt/migration-1-to-2.log`
4. Verify illuminance sensors appear as `sensor.*_illuminance` (no `_lux`) in HA Dev Tools
5. Test one motion-triggered light to confirm illuminance condition works
6. Confirm button automations still fire via legacy action sensors
- **Acceptance criteria**:
  - `ha_get_state("sensor.office_sensor_motion_illuminance")` → valid lux reading
  - `ha_get_state("sensor.office_sensor_motion_illuminance_lux")` → entity not found
  - One motion light triggers normally

### Phase 5: Migrate Buttons to MQTT Device Triggers
1. Press each of the 6 button devices once to register MQTT device triggers in HA
2. Find each button's `device_id` (HA → Settings → Devices → button → URL contains ID)
3. Rewrite 7 button automation files to use `trigger: device, domain: mqtt`
4. Remove `legacy_action_sensor: true` from `configuration.yaml`
5. Deploy and test all buttons
- **Files involved**: 7 button automation files, `zigbee2mqtt/configuration.yaml`
- **Acceptance criteria**: All buttons fire automations; `ha_get_logbook` confirms actions
