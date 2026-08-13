# Node-RED Automation Catalog

Source: `legacy-config/flows.json` — 1,296 nodes, 6 tabs, 21 subflows, 246 unique entity references.

## Triage Tags

| Tag | Meaning |
|-----|---------|
| MIGRATE | Convert to HA YAML automation |
| SCRIPT | Convert to HA script (reusable) |
| CONSOLIDATE | Merge duplicates into a single automation |
| SKIP | Do not migrate (test/dev only) |
| DROP | Remove (unused, obsolete, or superseded) |

---

## Tab: Geofencing (47 nodes, 4 groups)

Presence detection via BLE (MQTT monitor on Raspberry Pi) and HA geofence zones. Controls home/away mode transitions.

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Garage Presence Detection | 28 | MIGRATE | 6 | MQTT listener for `monitor/garage/jackson_pixel_3`; triggers home mode. 1 disabled node |
| Bluetooth scan trigger | 19 | MIGRATE | 6 | Garage door open -> MQTT `monitor/scan/arrive`; triggers BLE scan. 1 disabled node |
| GeoFence leaving home | 12 | MIGRATE | 6 | Lock up house + MQTT depart scan |
| GeoFence Arriving Home | 22 | MIGRATE | 6 | MQTT listener -> enable home mode + disarm. 1 disabled node |

**Duplicates**: Prius Presence detection also appears here via subflow (see Subflows section).

---

## Tab: Security (287 nodes, ~27 groups)

Alarm lifecycle, locks, cameras, door/window monitoring, and Noonlight emergency dispatch.

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Alarm Triggered | 53 | MIGRATE | 5 | Notifications, lights flash, camera snapshots |
| Alarm Disarmed | 24 | MIGRATE | 5 | Reset notifications, restore lights |
| Alarm Arming | 12 | MIGRATE | 5 | Warning beeps/notifications |
| Alarm Pending | 24 | MIGRATE | 5 | Countdown notifications |
| Alarm Armed Away | 16 | MIGRATE | 5 | Confirm notifications, enable cameras |
| Alarm Armed Home | 14 | MIGRATE | 5 | Night mode setup |
| Noonlight | 38 | MIGRATE | 5 | HTTP requests to Noonlight API for emergency dispatch |
| Exterior Door Sensors | 30 | MIGRATE | 5 | Door open/close monitoring while armed |
| Interior Door Sensors | 48 | MIGRATE | 5 | 5 disabled nodes |
| Door Left Open | 32 | MIGRATE | 5 | Timer-based alerts. 5 disabled nodes |
| Garage Opened While Away | 31 | MIGRATE | 5 | Alert + camera snapshot when away |
| Garage Opened 5 Minutes | 34 | MIGRATE | 5 | Alert if garage left open |
| Garage Door Change While Alarm Triggered | 31 | MIGRATE | 5 | Alert during active alarm |
| Doorbell Ring | 22 | MIGRATE | 5 | Notifications + camera snapshot |
| Door unlocked by Jackson | 17 | MIGRATE | 5 | Disarm alarm on specific lock code |
| Camera Motion Detected - Alarm Triggered | 34 | MIGRATE | 5 | While guarding/away |
| Camera Motion Detected (Person Only) | 33 | MIGRATE | 5 | While guarding/away; person detection only |
| Inside House Motion Detected | 17 | MIGRATE | 5 | While guarding/away |
| Garage Motion Detected | 25 | CONSOLIDATE | 5 | Duplicate: appears 2x (25 + 14 nodes). While guarding/away |
| Garage Motion Detected | 14 | CONSOLIDATE | 5 | Duplicate of above |
| Front Motion Detected | 23 | CONSOLIDATE | 5 | Duplicate: appears 2x (23 + 14 nodes). While guarding/away |
| Front Motion Detected | 14 | CONSOLIDATE | 5 | Duplicate of above |
| Outside Garage Motion Detected | 21 | CONSOLIDATE | 5 | Duplicate: appears 2x (21 + 14 nodes). While guarding/away |
| Outside Garage Motion Detected | 14 | CONSOLIDATE | 5 | Duplicate of above |
| Lock Down Button | 19 | MIGRATE | 5 | Physical button triggers Lock Down subflow |
| Lock Batteries Low | 7 | MIGRATE | 5 | Battery level notifications |
| Bed Occupancy Sensors | 31 | MIGRATE | 5 | Bed sensor state changes. 1 disabled node |

---

## Tab: Scheduled Tasks (55 nodes, ~7 groups)

Time-based automations using inject (cron) nodes. Most call subflows for the heavy lifting.

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Nightly Lockdown | 10 | MIGRATE | 7 | 9:30 PM if person.jackson is away. Calls Lock Down subflow. 2 disabled nodes |
| Nightly Close Blinds | 14 | MIGRATE | 7 | Calls Close Blinds subflow. 2 disabled nodes |
| Morning Resume Thermostat Schedule | 15 | MIGRATE | 7 | Calls Resume Thermostat Programming subflow. 2 disabled nodes |
| Daily Vacuum Run | 20 | MIGRATE | 7 | Checks Vacuum Not Run Recently subflow, runs vacuum |
| Vacation Open Blinds | 20 | MIGRATE | 7 | Only when vacation mode on. Calls Open Blinds + Is Somebody Home subflows |
| Open Curtains - 15 minutes after first alarm | 9 | MIGRATE | 7 | Alarm clock trigger -> delay -> open blinds |
| healthchecks.io | 11 | MIGRATE | 7 | Periodic HTTP ping to healthchecks.io. 1 disabled node |

---

## Tab: Miscellaneous (115 nodes, ~12 groups)

Grab bag: guest mode, media, system monitoring, device management.

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Actionable Notification Event Handler | 15 | MIGRATE | 8 | Handles iOS actionable notification responses |
| Backup Staleness Check | 10 | MIGRATE | 8 | Alert if backup is too old |
| Pelaton Automations | 17 | MIGRATE | 8 | Peloton workout -> adjust lights/fans |
| Prevent Google Nest Wake Sound | 16 | MIGRATE | 8 | Mute Nest speakers at startup. 1 disabled node |
| Apple TV Automations | 29 | MIGRATE | 8 | Media state -> adjust lights. 2 disabled nodes |
| Nightstand Smart Charger | 9 | MIGRATE | 8 | Battery-based charging control |
| Guest Mode Notification | 16 | MIGRATE | 8 | Notify when guest mode enabled/disabled |
| Vacuum - Lighting | 20 | MIGRATE | 8 | Turn on lights when vacuum runs in dark rooms |
| Pixel Watch - Battery Notification | 20 | MIGRATE | 8 | Low battery alerts |
| Updates Check | 10 | MIGRATE | 8 | HA update available notifications |
| Disk Utilization | 9 | MIGRATE | 8 | Storage space alerts |
| Siri Shortcut - Spooky Time | 14 | MIGRATE | 8 | iOS shortcut -> Halloween lighting scene |

---

## Tab: Zigbee Input Devices (386 nodes, ~42 groups)

Largest tab. Motion sensors, buttons, cubes, door sensors, and contact sensor lights.

### Motion Sensors (~20 automations)

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Turn on Office Light - Motion | 32 | MIGRATE | 3 | |
| Turn off Office Light - Motion | 46 | MIGRATE | 3 | |
| Fix Office Light State | 12 | DROP | — | Not found in cleaned-up flows; workaround no longer needed |
| Turn on Master Bedroom Light - Motion | 41 | MIGRATE | 3 | |
| Turn off Master Bedroom Light - Motion | 45 | MIGRATE | 3 | |
| Turn on Master Closet Light - Motion | 41 | MIGRATE | 3 | |
| Turn off Master Closet Light - Motion | 42 | MIGRATE | 3 | 1 disabled node |
| Turn on Main Floor Bathroom Light/Fan | 46 | MIGRATE | 3 | 1 disabled node |
| Turn off Main Floor Bathroom Light/Fan | 46 | CONSOLIDATE | 3 | Duplicate: appears 2x (46 + 30 nodes). 1 disabled each |
| Turn off Main Floor Bathroom Light/Fan | 30 | CONSOLIDATE | 3 | Duplicate of above |
| Turn On Basement Lights - Motion | 50 | MIGRATE | 3 | |
| Turn On Upstairs Lights - Motion | 14 | CONSOLIDATE | 3 | Duplicate: appears 2x (14 + 47 nodes) |
| Turn On Upstairs Lights - Motion | 47 | CONSOLIDATE | 3 | Duplicate of above |
| Turn on Guest Bedroom Light - Motion | 18 | MIGRATE | 3 | |
| Turn off Guest Bedroom Light - Motion | 26 | MIGRATE | 3 | |
| Turn on Guest Bathroom Light - Motion | 12 | MIGRATE | 3 | |
| Turn off Guest Bathroom Light - Motion | 16 | MIGRATE | 3 | |
| Turn on Office Bathroom Light - Motion | 27 | MIGRATE | 3 | |
| Turn off Office Bathroom Light - Motion | 27 | MIGRATE | 3 | |

### Contact Sensor Lights

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Turn On Pantry Light - Sensor | 40 | MIGRATE | 4 | Door sensor -> light on/off |
| Turn On Closet Light - Sensor | 19 | MIGRATE | 4 | Door sensor -> light on/off |
| Turn on Office Closet Light | 16 | MIGRATE | 4 | |
| Turn on Garage Light | 24 | MIGRATE | 3 | Moved from Phase 4; has motion + contact triggers |
| Turn Off Garage Lights | 12 | MIGRATE | 3 | Moved from Phase 4; timer-based off |
| Turn on Laundry Room Light | 14 | MIGRATE | 3 | Moved from Phase 4; has motion + contact triggers |
| Turn on Ulitity Room Light | 6 | MIGRATE | 4 | (sic — typo in Node-RED) |
| Turn Off Lights | varies | CONSOLIDATE | 4 | 5 instances (12+7+7+59+12 nodes). Consolidate into per-room off timers. 1 disabled node in 59-node instance |

### Buttons

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Master Bathroom Button | 26 | MIGRATE | 4 | Multi-press actions |
| Master Bedroom Button | 28 | MIGRATE | 4 | Multi-press actions |
| Kitchen Button | 15 | MIGRATE | 4 | Multi-press actions (renamed from "Living Room Button" in Node-RED) |
| Living Room 4-Button Fan Control | 8 | MIGRATE | 4 | `sensor.living_room_4_button_fan_control_action` — fan speed/off |
| Living Room 4-Button Light Control | 11 | MIGRATE | 4 | `sensor.living_room_4_button_slim_light_control_action` — scenes + timer |
| Living Room 4-Button Mode Control | 16 | MIGRATE | 4 | `sensor.living_room_4_button_light_control_action` — toggle guest/party/privacy modes with TTS |
| Pico Fan Remotes | 32 | MIGRATE | 4 | Lutron Caseta `lutron_caseta_button_event` — 3 pico remotes for living room, office, basement fans |

### Cubes

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Cube - Basement | 11 | DROP | — | No longer in use |
| Cube - Basement | 12 | DROP | — | Duplicate; no longer in use |
| Cube - Living Room | 25 | DROP | — | No longer in use |

### Door Sensors & Other

| Group | Nodes | Triage | Phase | Notes |
|-------|-------|--------|-------|-------|
| Door Open TTS | 33 | MIGRATE | 4 | Door open -> TTS announcement. 1 disabled node |
| Turn On Guest Mode - Door Sensor | 14 | MIGRATE | 4 | Guest bedroom door -> enable guest mode |
| Master Bathroom Humidity | 18 | MIGRATE | 4 | Humidity threshold -> fan control |
| Open Blinds in Morning | 15 | MIGRATE | 4 | Calls Open Blinds subflow |
| Power and Connectivity Notifications | 14 | MIGRATE | 4 | Zigbee device offline alerts |

### Disabled Automations

| Group | Notes |
|-------|-------|
| Bathroom Door Opened | 1 disabled `server-state-changed` node; not connected to any active flow |

---

## Tab: Scratchpad (191 nodes)

**Triage: SKIP** — All nodes are test/development. No production automations. Contains inject->debug chains, API test calls, MQTT experiments, and history queries. Will not be migrated.

---

## Subflows (21 total)

| Subflow | Nodes | Used | Triage | Phase | Notes |
|---------|-------|------|--------|-------|-------|
| Lock Down | 50 | 6x | SCRIPT | 2 | Locks, covers, cameras, lights, alarm. Used by Security, Miscellaneous, Scheduled Tasks |
| Open Blinds | 14 | 7x | SCRIPT | 2 | Checks room occupancy before opening. Used by Security, Scheduled Tasks, Zigbee |
| Close Blinds | 1 | 1x | SCRIPT | 2 | Calls `scene.close_all` |
| Enable Home Mode | 27 | 3x | SCRIPT | 2 | Disarm, lights, thermostat, fans. Used by Security, Geofencing |
| Enable Away Mode | 21 | 2x | SCRIPT | 2 | Arm, vacuum, notifications. Used by Security, Geofencing |
| Disarm | 12 | 5x | SCRIPT | 2 | Disarm alarm + notifications. Used by Security, Miscellaneous |
| Arm Away | 1 | 1x | SCRIPT | 2 | Simple `alarm_control_panel.alarm_arm_away` call |
| Arm Home | 1 | 2x | SCRIPT | 2 | Simple `alarm_control_panel.alarm_arm_home` call |
| Enable Thermostat Away | 2 | 1x | SCRIPT | 2 | Set both thermostats to away preset |
| Enable Thermostat Sleep | 2 | 2x | SCRIPT | 2 | Set both thermostats to sleep preset |
| Resume Thermostat Programming | 3 | 3x | SCRIPT | 2 | Resume schedule unless guest override is on |
| Door Left Open | 6 | 1x | SCRIPT | 2 | Timer-based door open alert |
| Trigger | 2 | 1x | SCRIPT | 2 | Trigger alarm |
| Someone Has Been Home | 6 | 1x | SCRIPT | 2 | Inlined as variable in enable_home_mode (not a standalone entity) |
| Prius Presence Guard | 3 | 1x | SCRIPT | 2 | Check if Prius is at home zone |
| Vacuum Not Run Recently | 3 | 3x | SCRIPT | 2 | Check vacuum last run date |
| Is Somebody Home | 4 | 3x | SCRIPT | 2 | Check zone.home person count |
| Idle Google Nest Mini | 5 | 2x | DROP | — | Only used by Prevent Google Nest Wake Sound; inline in Phase 8 if needed |
| Enable Thermostat Home | 2 | 0x | DROP | — | Unused — never called by any flow |
| Handle Media Player | 12 | 0x | DROP | — | Unused — never called by any flow |
| Idle Google Nest Mini Group | 5 | 0x | DROP | — | Unused — never called by any flow |

**Active subflows**: 17 → converted to 12 scripts + 5 sensors + 1 deferred (Prius → Phase 6). Someone Has Been Home inlined as a variable.

---

## Cross-Tab Duplicates

These automation groups appear in multiple locations or multiple times within the same tab:

| Name | Locations | Action |
|------|-----------|--------|
| Garage Motion Detected | Security (2x: 25 + 14 nodes) | CONSOLIDATE into 1 |
| Front Motion Detected | Security (2x: 23 + 14 nodes) | CONSOLIDATE into 1 |
| Outside Garage Motion Detected | Security (2x: 21 + 14 nodes) | CONSOLIDATE into 1 |
| Turn Off Lights | Zigbee (5x: 12+7+7+59+12 nodes) | CONSOLIDATE per-room |
| Turn On Upstairs Lights - Motion | Zigbee (2x: 14 + 47 nodes) | CONSOLIDATE into 1 |
| Turn off Main Floor Bathroom Light/Fan | Zigbee (2x: 46 + 30 nodes) | CONSOLIDATE into 1 |
| Cube - Basement | Zigbee (2x: 11 + 12 nodes) | DROP — no longer in use |

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total nodes | 1,296 |
| Tabs (active) | 5 (Scratchpad excluded) |
| Automation groups | ~92 |
| Groups to migrate | ~76 |
| Groups to consolidate | ~16 (into ~7) |
| Groups to skip/drop | Scratchpad (191 nodes) |
| Active subflows | 17 |
| Unused subflows (DROP) | 4 |
| Disabled automations | 1 (Bathroom Door Opened) |
| Unique entity references | 246 |
