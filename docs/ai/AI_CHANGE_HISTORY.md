# AI Change History

## Version 0.0.7
- Goal: integrations discovery quality cleanup without architecture changes.
- Key changes: normalize dotted component names to main integration (`mqtt.sensor` -> `mqtt`), add simple `kind` classification (`user_integration` / `core_component`), keep core components visible, and prioritize user integrations in `top_items`.
- Result: smaller, clearer, and more AI-usable integration view with transparent read-only semantics.
- Next focus: continue Discovery Quality phase (areas/devices/dashboard robustness).

## Version 0.0.6
- Goal: replace integrations placeholder with first useful read-only integrations discovery.
- Key changes: direct integrations from `config.components`, cautious derived fallbacks from services/states, compact `items`/`top_items`, and semantic status (`available`/`partial`/`unavailable`).
- Result: `integrations` category can now return real discovered items when readable.
- Next focus: improve coverage quality while keeping compact semantics.

## Version 0.0.5
- Goal: improve discovery semantics and robustness.
- Key changes: explicit proxy API base, longer timeout, partial semantics for key categories.
- Result: more consistent export status evaluation and diagnostics.
- Next focus: ongoing discovery coverage and quality improvements.
