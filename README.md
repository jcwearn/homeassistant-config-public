# homeassistant-config

GitOps-managed [Home Assistant](https://www.home-assistant.io/) configuration for
HA OS running on Home Assistant Yellow.

> **This is a read-only published snapshot.** Development happens in a private
> repo; a CI job mirrors the filtered tree here on every merge. Issues and pull
> requests opened here won't sync back upstream, and commits here will be
> overwritten by the next sync. Feel free to read, fork, and steal ideas.

## Layout

| Path | Contents |
|---|---|
| `config/` | Maps to HA's `/config/` |
| `config/packages/` | HA packages — helpers, groups, per-domain config |
| `config/automations/` | Automations, grouped by domain |
| `config/scripts/` | Reusable scripts |
| `config/dashboards/` | YAML-mode Lovelace dashboards |
| `config/secrets.sops.yaml` | Secrets, encrypted with [SOPS](https://github.com/getsops/sops) + age |
| `zigbee2mqtt/` | Zigbee2MQTT add-on config |
| `scripts/` | Deploy and export helpers |
| `docs/plans/` | Migration plans and progress notes |

## How it works

- **Secrets** are encrypted at rest with SOPS + age and referenced as `!secret`.
  The encrypted files are committed; the decrypted `secrets.yaml` never is.
- **Validation** runs on every PR: `yamllint` plus a real `homeassistant
  --script check_config` inside the official Docker image, with mock secrets
  substituted.
- **Deploys** happen on merge to `main` — SOPS decrypts, then rsync over SSH
  across a Tailscale link.

## Notes

Entity IDs are load-bearing: a large set of automations reference them directly,
so they're preserved verbatim across refactors. Integration config entries, Hue
scenes, and `switch_as_x` helpers stay UI-managed — they can't be expressed in
YAML.
