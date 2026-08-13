# Progress: Node-RED Automation Migration

## Current Status: In Progress

| Phase | Status | Updated | Notes |
|-------|--------|---------|-------|
| 1. Catalog & Triage | Complete | 2026-03-05 | See [catalog.md](catalog.md) |
| 2. Scripts (Subflows) | Complete | 2026-03-06 | 12 scripts + 5 sensors, PR #16 merged |
| 3+4. Zigbee Input Devices | Complete | 2026-03-06 | 26 files, 43 automations, PR #17 + follow-up PR |
| 5. Security | In Progress | 2026-03-09 | PR #53 open; post-review fixes in progress |
| 6. Geofencing & Presence | Complete | 2026-03-08 | 3 files, 5 automations, PR pending |
| 7. Scheduled Tasks | Complete | 2026-03-07 | 7 files, 9 automations, PR #27 |
| 8. Miscellaneous | Complete | 2026-03-08 | 10 automation files + 1 package, PR #41 |
| 9. Cleanup & Retirement | Not Started | — | — |

## Handoff Notes

Phases 3+4 (entire Zigbee Input Devices NR tab) implementation complete, PR #17.

### What was done (Phase 3 — motion sensors)
- 12 automation files, 25 automations for motion-activated lighting
- Files use `lights_*.yaml` naming (grouped by room/lights controlled)
- Every turn-off automation has both motion-off AND timer triggers

### What was done (Phase 4 — added to same PR)
- 10 new automation files, 12 automations:
  - `lights_pantry.yaml`: contact → scene on open, match kitchen light on close
  - `lights_main_floor_closet.yaml`: contact → scene on open, match hallway light on close
  - `lights_office_closet.yaml`: contact → light on/off
  - `lights_utility_room.yaml`: contact → light on/off
  - `button_master_bathroom.yaml`: single (open/close master shades), hold (toggle bathroom shade)
  - `button_master_bedroom.yaml`: single (toggle nightstands, turn off ceiling/closet), double (ruby glow), hold (nighttime scene)
  - `button_kitchen.yaml`: single (cooking scene or start 1h timer), timer expired (turn off main floor lights)
  - `guest_mode_door.yaml`: door close → guest_override on, door open → off (skipped in party_mode)
  - `blinds_open_morning.yaml`: stairwell motion + first trigger today + sun up + privacy off → open blinds script
  - `notifications_zigbee_battery.yaml`: battery < 20% on 18 sensors + smart plug unavailable on 3 switches
- Modified `lights_garage.yaml`: added `light.outside_garage_light` to turn-off action
- Modified `lights_main_floor_bathroom.yaml`: added door-open trigger, changed door condition from "off" to "on"
- Dropped from Phase 4: Cubes (unused), Door Open TTS (removed from NR), Master Bathroom Humidity (removed from NR)
- "Turn Off Lights" catch-alls covered by per-room turn-offs + contact sensor close actions

### What was done (Phase 3+4 follow-up — missed automations)
- 4 new automation files, 6 automations missed from initial PR #17:
  - `button_living_room_fan.yaml`: 4-button fan control (100%/50%/33%/off)
  - `button_living_room_lights.yaml`: 4-button light control (scenes + tv_lights_timer)
  - `button_living_room_modes.yaml`: 4-button mode control (toggle guest/party/privacy + TTS)
  - `pico_fan_remotes.yaml`: 3 Lutron Caseta pico remotes (living room, office, basement fans)
- Added 4 missed groups to catalog.md

### Totals
- 26 automation files, 43 automations across entire Zigbee Input Devices tab

### What was done (Phase 7 — Scheduled Tasks)
- 7 new automation files, 9 automations migrated from Node-RED Scheduled Tasks tab
- New package: `config/packages/healthcheck.yaml` (rest_command for healthchecks.io)
- New encrypted secret: `healthcheck_ping_url` in `config/secrets.sops.yaml`
- Vacuum automation uses `choose` for person-aware notifications with `vacuum_delay` boolean pattern
- Open curtains uses `last_triggered` date check + weekday condition + 15min delay
- Excluded "Turn On Master Bedroom Lights" at 9 PM (dead code in NR)

### What was done (Phase 6 — Geofencing & Presence)
- 3 new automation files, 5 automations in `config/automations/presence/`
  - `presence_arrive.yaml`: vacation_mode off → garage unlock → personalized notification (w/ action buttons) → enable_home_mode (gated on alarm not disarmed); 5-min cooldown via `last_triggered` condition
  - `presence_leave.yaml`: 3 automations:
    - `presence_leave_nobody_home`: last person out (no guest/party mode) → `enable_away_mode`
    - `presence_leave_someone_still_home`: someone still home → 30s delay → re-check → personalized goodbye + "[Person] left" notifications
    - `presence_leave_guest_mode`: last person out with guest/party mode → LOCK_DOWN actionable notification (Node-RED handles response for now)
  - `presence_prius.yaml`: prius disappears (not already armed_away, no guest/party mode) → `enable_away_mode` with source: prius
- Skipped: BLE/MQTT Garage Presence Detection and Bluetooth scan trigger (GPS sufficient)
- `enable_home_mode` / `enable_away_mode` scripts from Phase 2 reused unchanged

### What was done (Phase 8 — Miscellaneous)
- 4 new automation files in new `config/automations/misc/` dir
- 1 new automation file in new `config/automations/media/` dir
- 2 new automation files added to existing `config/automations/notifications/` dir
- 1 new automation file added to existing `config/automations/schedules/` dir
- 1 new automation file added to existing `config/automations/vacuum/` dir
- New package: `config/packages/ntfy.yaml` (rest_command for Ntfy)
- New encrypted secret: `ntfy_url` in `config/secrets.sops.yaml`; `.sops.yaml` updated with regex
- Dropped: Pelaton automations, Prevent Google Nest Wake Sound, LG TV reload, Poll Apple TV State
- `script.trigger_noonlight` in actionable handler is a stub — Noonlight integration deferred

### What was done (Phase 5 — Security)
- 11 new automation files, ~17 automations migrated from Node-RED Security tab (287 nodes)
- Noonlight dispatch API integration deferred (no package, scripts, helpers, or secrets added)
- Security automations in `config/automations/security/`:
  - `alarm-state.yaml`: 6 automations (pending, arming, armed_home, armed_away, triggered, disarmed)
  - `exterior-doors.yaml`: see post-review refactor notes below
  - `door-unlocked.yaml`: lock unlocked → enable_home_mode
  - `interior-motion.yaml`: office/dining motion while armed_away/triggered → notify
  - `garage-away.yaml`: garage open while away → snapshot + notify; 5min → close + notify
- Notifications in `config/automations/notifications/`:
  - `notifications_door_left_open.yaml`: door open 5min → notify
  - `notifications_lock_battery.yaml`: battery < 21% → notify
- Presence in `config/automations/presence/`:
  - `presence_bed_occupancy.yaml`: bed occupied at night → scene + optional arm_home/lockdown
- Misc in `config/automations/misc/`:
  - `misc_doorbell_ring.yaml`: doorbell → snapshot → notify with unlock action
  - `misc_interior_door.yaml`: master bedroom door → fan/alarm/curtain logic (refactored to nested if/else)

### Post-review fixes on branch (PR #53, 2026-03-09)
- `exterior-doors.yaml` refactored from `choose` to nested if/else:
  - Front door light now runs independently of party mode and alarm state (front_door + nighttime only)
  - `party_mode` gate moved to wrap only alarm/chime/greeting logic (not front door light)
  - Added missing open chime (plays for `armed_home` or `disarmed`)
  - Greeting now fires for any door (not just front door) when disarmed
  - `armed_home`: triggers alarm AND plays open chime
  - `armed_away`: triggers alarm only
- `misc_interior_door.yaml`: restructured to nested if/else
- `alarm-state.yaml` (disarmed): scoped TTS and media stop to specific action branches
- `alarm-state.yaml` (armed_home): gated `enable_thermostat_sleep` on door closed + last person in bed

### Lock reliability fix (PR #93, 2026-07-10)
- August locks intermittently time out over WiFi; raw `TimeoutError` aborted the calling sequence (`continue_on_error` only suppresses `HomeAssistantError`)
- New fire-and-forget helper `script.set_lock` (`config/scripts/locks.yaml`), invoked via `script.turn_on`
- All `lock.lock`/`lock.unlock` calls routed through it: `presence_arrive.yaml`, `lockdown.yaml` (+ bounded `wait_template` before status notification), `misc_actionable.yaml`

### Next steps
1. Merge PR #53 after review
2. Deploy config via `scripts/deploy.sh`
3. Verify all new automations appear in Settings → Automations & Scenes
4. Test alarm lifecycle via Developer Tools (state changes on alarm panel)
5. Test door/motion/camera triggers via entity state changes
6. Run in parallel with Node-RED Security tab for 24-48h, then disable NR flows
7. Phase 9 (Cleanup & Retirement) remains
