# Phase 1: Core YAML Configuration

**Goal**: Migrate helpers, groups, alarm panel, and system config from UI/storage to YAML packages.

> Track task-level progress in [progress.md](progress.md). Update it as you complete items.

## Checklist

- [ ] Run `scripts/export-from-ha.sh` to pull .storage data
- [ ] Create `packages/helpers.yaml` — all 11 helpers with exact entity IDs
- [ ] Create `packages/groups.yaml` — all 7 groups with exact entity members
- [ ] Create `packages/alarm.yaml` — manual alarm control panel
- [ ] Create `packages/system.yaml` — logger, recorder, history config
- [ ] Deploy YAML versions, verify entities exist
- [ ] Delete UI-managed helpers/groups (only after YAML versions confirmed working)
- [ ] Verify no duplicate entities
- [ ] Verify Node-RED flows still fire correctly
- [ ] CI `check_config` passes

## Helpers to Migrate (11)

### input_boolean (6)
| Entity ID | Name |
|-----------|------|
| `input_boolean.guest_override` | Guest Override |
| `input_boolean.party_mode` | Party Mode |
| `input_boolean.privacy_mode` | Privacy Mode |
| `input_boolean.theater_mode` | Theater Mode |
| `input_boolean.vacation_mode` | Vacation Mode |
| `input_boolean.vacuum_delay` | Vacuum Delay |

### input_datetime (2)
| Entity ID | Name |
|-----------|------|
| `input_datetime.guest_mode_schedule` | Guest Mode Schedule |
| `input_datetime.guest_mode_schedule_end` | Guest Mode Schedule End |

### input_number (1)
| Entity ID | Name |
|-----------|------|
| `input_number.basement_lux_threshold` | Basement Lux Threshold |

### input_text (1)
| Entity ID | Name |
|-----------|------|
| `input_text.alarm_disarm_source` | Alarm Disarm Source |

### timer (1)
| Entity ID | Name |
|-----------|------|
| `timer.tv_lights_timer` | TV Lights Timer |

**Note**: Detailed configs (min/max/step, has_date/has_time, duration) need to be read from `.storage/` exports.

## Groups to Migrate (7)

| Entity ID | Name |
|-----------|------|
| `group.kitchen_lights` | Kitchen Lights |
| `group.living_room_lights` | Living Room Lights |
| `group.living_room_media` | Living Room Media |
| `group.main_floor_lights` | Main Floor Lights |
| `group.master_bedroom_lights` | Master Bedroom Lights |
| `group.master_bedroom_motion` | Master Bedroom Motion |
| `group.office_devices` | Office Devices |

**Note**: Member entity IDs need to be read from `.storage/` exports or HA API.

## Critical Constraint

Entity IDs MUST be preserved exactly. All 40+ Node-RED flows reference these IDs.

## Migration Order

1. Deploy YAML packages → restart HA
2. Verify entities exist in Developer Tools > States
3. Delete UI-managed versions
4. Restart again → verify no duplicates
