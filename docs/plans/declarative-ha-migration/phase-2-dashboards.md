# Phase 2: Dashboard & Frontend

**Goal**: Version-control Lovelace dashboards and HACS resource declarations.

> Track task-level progress in [progress.md](progress.md). Update it as you complete items.

## Checklist

- [ ] Export current dashboard (Edit Dashboard → Raw Editor → copy YAML)
- [ ] Set up `lovelace:` in configuration.yaml with `mode: yaml`
- [ ] Declare HACS frontend resources in YAML
- [ ] Create `dashboards/main.yaml`
- [ ] Document HACS inventory in `docs/hacs-inventory.md`
- [ ] Add theme config if customized
- [ ] Verify dashboard renders correctly
- [ ] Verify no JS console errors from missing resources
- [ ] Verify theme applies correctly

## HACS Frontend Resources to Declare

- auto-entities
- browser_mod
- button-card
- card-mod
- mini-graph-card
- mini-media-player
- light-entity-card
- simple-weather-card
- my-cards-bundle

## Trade-off

YAML dashboards cannot be edited via the UI visual editor. All dashboard changes go through git. This is intentional for the GitOps workflow but means quick UI tweaks require a commit+deploy cycle.
