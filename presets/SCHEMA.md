# Preset schema

Every file `presets/<id>.json` follows this shape (all keys required unless noted):

```json
{
  "id": "kinetic-typography",
  "name": "Kinetic Typography — Kinetic Red",
  "palette":  { "bg": "#F5EFE4", "ink": "#181614", "accent": "#B22234", "sub": "#60584E" },
  "fonts":    { "display": "Montserrat.ttf", "script": "Amiri.ttf", "body": "Montserrat.ttf" },
  "background": { "type": "flat + diagonal band", "description": "…" },
  "layout":   { "style": "…", "mid_y": 0.44, "safe_top_px": 250, "safe_bottom_px": 420, "credit_strip": true },
  "transitions": { "in": "beat-cut", "out": "beat-cut", "duration_s": 0.0 },
  "animation": { "word_in": "pop", "word_pop": 0.20, "blur_px": 0, "underline": true },
  "renderer": { "name": "engine/render_kinetic.py", "support": "verified-video" },
  "sampler_base": "08 Kinetic Red",          // optional: design_sampler.py design it maps to
  "preview": "assets/previews/design08-hook.jpg", // optional: verified still (absent = not rendered yet)
  "notes": "…"
}
```

`renderer.support` values:
- `verified-video` — a full video has been rendered with this preset by the named engine.
- `verified-stills` — still frames verified via `engine/design_sampler.py`; video render = port the
  sampler palette/layout into the PIL engine (or a HyperFrames composition on a machine with Chrome).
- `data-only` — preset defined as data only; no renderer support yet. Never present these as working.

New presets must be added as new JSON files following this schema — the engine and registry
do not need code changes. Transition presets live in `presets/transitions/<id>.json`
(`{id, type, duration_s, easing, params}`); easing curves in `presets/transitions/easings.json`.
