# Plan: Node-RED Automation Migration

## Context

All 40+ home automations currently run in Node-RED (1,296 nodes, 21 subflows, 6 tabs, 246 entity references). This plan migrates them to native HA YAML automations and scripts for maintainability, GitOps integration, and elimination of the Node-RED dependency.

Prerequisite: Phases 0-2 of the [declarative HA migration](../declarative-ha-migration/plan.md) are complete (repo, packages, dashboards).

## Phases

### Phase 1: Catalog & Triage

- Parse `legacy-config/flows.json`, create full inventory of all flows organized by tab
- Assign triage decision to every automation group: MIGRATE, SCRIPT, CONSOLIDATE, SKIP, or DROP
- Identify disabled automations, scratchpad/test flows, and duplicates
- Document in [catalog.md](catalog.md)
- **Files involved**: `docs/plans/node-red-automation-migration/catalog.md`
- **Acceptance criteria**: Every automation group and subflow has a triage tag; catalog matches flows.json exactly

### Phase 2: Scripts (Subflows)

- Convert 15 active subflows to HA scripts in `config/scripts/`
- Drop 3 unused subflows (Handle Media Player, Enable Thermostat Home, Idle Google Nest Mini Group)
- Scripts are shared dependencies used across multiple automations — must be converted first
- Key subflows: Lock Down, Enable Home/Away Mode, Arm/Disarm, Open/Close Blinds, thermostat presets
- **Files involved**: `config/scripts/*.yaml`
- **Acceptance criteria**: All active subflows have equivalent HA scripts; scripts callable from Developer Tools > Services

### Phase 3+4: Zigbee Input Devices (combined)

- Migrate entire Zigbee Input Devices Node-RED tab in a single phase
- Motion-activated lighting (~25 automations): motion on → light on, motion clear → light off (with conditions for time, occupancy, lux)
- Contact sensor lights: pantry, closets, utility room (door open → light on, door close → light off)
- Smart buttons: master bathroom (shade toggle), master bedroom (single/double/hold), kitchen (cooking mode + timer)
- Guest mode door sensor, morning blinds opener, Zigbee battery/plug notifications
- Dropped: Cubes (unused), Door Open TTS (removed from NR), Master Bathroom Humidity (removed from NR)
- Consolidated: 5 "Turn Off Lights" catch-all groups covered by per-room turn-offs + contact sensor close actions
- **Files involved**: `config/automations/lights_*.yaml`, `config/automations/button_*.yaml`, `config/automations/guest_mode_door.yaml`, `config/automations/blinds_open_morning.yaml`, `config/automations/notifications_zigbee_battery.yaml`
- **Acceptance criteria**: All motion, contact sensor, button, and miscellaneous Zigbee automations work; entire NR tab can be disabled at once

### Phase 5: Security

- Alarm state automations (triggered, disarmed, arming, pending, armed home, armed away)
- Lock automations (door unlocked by Jackson, lock batteries low)
- Camera motion detection (person-only, alarm-triggered, guarding/away)
- Door/window monitoring (exterior/interior sensors, door left open, garage)
- Noonlight integration
- Bed occupancy sensors
- **Files involved**: `config/automations/security_*.yaml`, `config/packages/alarm.yaml`
- **Acceptance criteria**: Full alarm lifecycle works; Noonlight triggers correctly; all door/motion alerts fire

### Phase 6: Geofencing & Presence

- Garage BLE presence detection (MQTT monitor)
- Geofence arrive/leave automations
- Bluetooth scan trigger on garage door open
- Prius presence guard
- **Files involved**: `config/automations/presence_*.yaml`
- **Acceptance criteria**: Arrive/leave correctly triggers home/away mode; presence detection works

### Phase 7: Scheduled Tasks

- Nightly lockdown (9:30 PM if away)
- Nightly close blinds
- Morning thermostat resume
- Daily vacuum run
- Vacation open blinds
- Open curtains after first alarm
- healthchecks.io ping
- **Files involved**: `config/automations/schedule_*.yaml`
- **Acceptance criteria**: All time-based automations trigger at correct times with correct conditions

### Phase 8: Miscellaneous

- Guest mode notification
- Backup staleness check
- Actionable notification event handler
- Peloton automations
- Prevent Google Nest wake sound
- Apple TV automations
- Nightstand smart charger
- Vacuum lighting
- Pixel Watch battery notification
- Updates check, disk utilization
- Siri Shortcut (Spooky Time)
- **Files involved**: `config/automations/misc_*.yaml`
- **Acceptance criteria**: All miscellaneous automations work; notifications deliver correctly

### Phase 9: Cleanup & Retirement

- Archive final Node-RED flows to `docs/archive/node-red-flows-final.json`
- Disable Node-RED add-on
- Monitor for 30 days
- Uninstall Node-RED + Node-RED Companion after 30 days stable
- **Acceptance criteria**: 30 days with no issues; Node-RED add-on removed

## Phase Ordering Rationale

1. **Scripts first** — Subflows are shared dependencies called by automations in later phases
2. **Zigbee combined** — Entire NR tab in one phase; lets user disable whole tab during parallel testing
3. **Security** — Complex but self-contained; depends on alarm scripts from Phase 2
4. **Geofencing** — Depends on home/away mode scripts from Phase 2
5. **Scheduled** — Simple time triggers but depend on scripts (lockdown, blinds, thermostat)
6. **Miscellaneous** — Lowest priority, most independent
7. **Cleanup last** — Only after all automations are verified

## Migration Strategy Per Automation

1. Write YAML automation equivalent
2. Deploy and test manually with Developer Tools
3. Run in parallel with Node-RED flow for 24-48h
4. Disable Node-RED flow
5. Monitor for 1 week before archiving

## Workflow

Each phase gets its own branch and PR so work can be reviewed and merged incrementally. Do not combine multiple phases into a single PR.

## Key Constraints

- Entity IDs MUST be preserved exactly (Node-RED flows reference them during parallel run)
- `config/automations/` uses `!include_dir_merge_list` — each file returns a list
- `config/scripts/` uses `!include_dir_merge_named` — each file returns a dict
- Subflows used inside other subflows must be converted before their parent
