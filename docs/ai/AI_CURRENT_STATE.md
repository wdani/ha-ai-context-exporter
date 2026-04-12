# AI Current State

## Current version
`0.0.6`

## Export status currently observed
- `system = partial`
- `entities = available`
- `logic = available`

## Known limitations
- Integrations discovery now uses a first read-only implementation based on `config.components` with cautious fallbacks from services/states.
- Areas/devices discovery can be incomplete depending on proxy readability and environment.
- Dashboard metadata can be limited depending on endpoint readability.
