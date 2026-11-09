# Lyric Video Studio

A working lyric-video production environment built 2026-10-25 in
`~/workspace/lyric-video-studio/`, reusing the pipeline already proven on the
Qarara Rasha project (Demucs + MMS_FA word sync → PIL kinetic renderer).
Total size ≈ 81 MB. Nothing outside this folder was modified.

## What actually works today
- **Word sync**: song.mp3 + lyrics.txt → Demucs vocal separation → torchaudio
  MMS_FA forced alignment → `assets/words.json` (`{line, w, s, e}`), with a
  timing table that flags low-confidence lines instead of hiding them.
- **Rendering**: `engine/render_kinetic.py` — deterministic PIL frame renderer
  (24 fps, word pop + progress underline from real timings, intro/interlude/
  outro cards, project.json-driven titles/credits/subtitles). Outputs
  1080×1920, 1920×1080, or any WxH via CLI. HyperFrames skills are installed
  for HTML compositions, but browser capture is blocked in this sandbox
  (see LIMITATIONS.md) — on the user's machine they are the primary path.
- **Design system**: 10 verified design stills (`assets/previews/`), 12 style
  presets (`presets/*.json`, schema in `presets/SCHEMA.md`), 8 transition +
  6 easing data presets, 7 OFL fonts.
- **Search**: describe a design in words, get ranked assets.
- **UI**: `app/index.html` — offline library page (search + category filters +
  preset gallery; real registry data embedded; fonts load via @font-face).

## Quickstart
```sh
cd ~/workspace/lyric-video-studio

# 1. verify everything
.venv/bin/python tests/run_tests.py

# 2. search the library
python3 scripts/search_assets.py "romantic golden fireflies handwritten lyrics soft glow"

# 3. new project: create projects/<name>/ with lyrics.txt + assets/song.mp3
#    (copy projects/sample/ as the template), then:
scripts/sync.sh  projects/<name>                       # -> assets/words.json
scripts/render.sh projects/<name> 1080 1920 0 12 renders/out.mp4

# 4. browse the library
#    open app/index.html in any browser (works offline, file:// is fine)
```

Verified search result for the example query above — Warm Fireflies ranks first,
then the handwritten script fonts it pairs with:

```
 19  [design] Warm Fireflies — dark amber, glowing gold fireflies, romantic warm
  7  [font] Great Vibes — script handwritten calligraphy
  5  [font] Kaushan Script — handwritten brush script
  4  [font] Cormorant Garamond — serif delicate literary
```

## Sample project
`projects/sample/` is a synthetic 12-second end-to-end proof (tone+click audio,
3 lyric lines, hand-written timings). Its render is `renders/sample-test-9x16.mp4`
(1080×1920, 24 fps, AAC, exactly 12.00 s — ffprobe-verified) and
`thumbnails/sample-contact-sheet.jpg` shows title / verse / hook frames.

## Docs
- `docs/ENVIRONMENT.md` — measured machine facts
- `docs/SKILLS.md` — skill installs, exact commands and outcomes
- `docs/INSTALL.md` — layout, two-venv arrangement, pinned versions
- `docs/MANIFEST.md` — every component: version, license, honest status
- `docs/LIMITATIONS.md` — blockers + the user's own-machine command list
