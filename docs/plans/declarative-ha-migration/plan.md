# Plan: Home Assistant GitOps Migration

## Context

HA OS on Yellow hardware (v2026.2.3) — migrating from 100% UI-managed to declarative YAML with CI/CD.

## Progress Tracker

See **[progress.md](progress.md)** for detailed task-level status, agent notes, and decisions log.
Agents should update progress.md as they complete work.

## Phase Status

| Phase | Description | Status | Details |
|-------|-------------|--------|---------|
| 0 | Repository Foundation & GitOps Infrastructure | Complete | [phase-0-foundation.md](phase-0-foundation.md) |
| 1 | Core YAML Configuration (helpers, groups, alarm, system) | Complete | [phase-1-core-yaml.md](phase-1-core-yaml.md) |
| 2 | Dashboard & Frontend | In Progress | [phase-2-dashboards.md](phase-2-dashboards.md) |
| 3 | Service Migration to k3s (Mosquitto, ESPHome) | Dropped | k3s downtime shouldn't affect HA |
| 4 | Automation Migration from Node-RED (40+ flows) | Moved | See [node-red-automation-migration](../node-red-automation-migration/plan.md) |

## Phase Dependencies

```
Phase 0 (Foundation) -> Phase 1 (Core YAML) -> Phase 2 (Dashboards)
```

Phase 3 was dropped — k3s downtime shouldn't affect HA availability.
Phase 4 was moved to its own dedicated plan at `docs/plans/node-red-automation-migration/`.

## What Stays UI-Managed

- Integration config entries (Hue, Lutron, UniFi, Ecobee, August, Bond, Spotify, HomeKit, MQTT, etc.)
- Hue scenes (80, bridge-native, auto-discovered)
- Zigbee2MQTT add-on (Yellow's built-in radio requires local USB — config version-controlled only)

## Key Details

- **Secrets**: SOPS + age (dedicated keypair at `~/.age/homeassistant.key`)
- **Deployment**: rsync via SSH (CI/CD via GitHub Actions + Tailscale planned)
- **HA address**: LAN address in `HA_SSH_HOST` (Tailscale for remote), https://home.wearn.dev (external)
- **Entities**: 3,559 across 24 areas, 5 persons
