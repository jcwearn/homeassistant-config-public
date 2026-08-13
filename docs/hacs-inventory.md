# HACS Frontend Resources Inventory

Resources installed via HACS and loaded via `.storage/lovelace_resources`.
HACS manages these independently of lovelace mode (storage vs YAML).

| Resource | Type | URL Path | Notes |
|----------|------|----------|-------|
| button-card | Module | `/hacsfiles/button-card/button-card.js` | Custom button cards |
| auto-entities | Module | `/hacsfiles/lovelace-auto-entities/auto-entities.js` | Auto-populate entity cards |
| card-mod | Module | `/hacsfiles/lovelace-card-mod/card-mod.js` | CSS styling for cards; used by Alarm dashboard |
| mini-graph-card | Module | `/hacsfiles/mini-graph-card/mini-graph-card-bundle.js` | Compact graph cards |
| mini-media-player | Module | `/hacsfiles/mini-media-player/mini-media-player-bundle.js` | Compact media player cards |
| light-entity-card | Module | `/hacsfiles/light-entity-card/light-entity-card.js` | Light control cards |
| simple-weather-card | Module | `/hacsfiles/simple-weather-card/simple-weather-card-bundle.js` | Minimal weather card |
| my-cards | Module | `/hacsfiles/my-cards/my-cards.js` | Card bundle (slider-card, etc.) |

## Notes

- All 8 resources are JavaScript modules loaded as `type: module`
- Exported from `.storage/lovelace_resources` on 2026-03-05; saved to `.export/lovelace_resources.json`
- UI Lovelace Minimalist integration is installed but unused (no resources registered); remove post-deploy
