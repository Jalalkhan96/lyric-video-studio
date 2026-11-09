# Lyric Video Studio

A lyric-video production toolkit: word-level sync (Demucs + MMS forced
alignment) feeding a deterministic PIL kinetic renderer, plus a design
library of 12 style presets, 8 transitions, 7 open fonts and 10 design
stills. Built 2026-10-25, reusing the pipeline proven on the Qarara Rasha
project (Demucs + MMS_FA word sync → PIL kinetic renderer).

This repo is the runnable core of the studio. The full local studio also
holds third-party skill packs, real-song project data and render outputs
that are not shipped here — see "What is not in this repo" below.

## What actually works
- **Word sync** — `engine/align_words.py`: song vocals + `lyrics.txt` →
  torchaudio MMS_FA forced alignment → `assets/words.json`
  (`{line, w, s, e}`), with a timing table that flags low-confidence lines
  instead of hiding them. (Needs the sync venv with torch/torchaudio —
  see `docs/INSTALL.md`.)
- **Rendering** — `engine/render_kinetic.py`: deterministic PIL frame
  renderer (24 fps, word pop + progress underline from real timings,
  intro/interlude/outro cards, `project.json`-driven titles/credits/
  subtitles). Outputs 1080×1920, 1920×1080, or any WxH via CLI.
  ```sh
  LVS_PROJECT=projects/sample python3 engine/render_kinetic.py frame 0 1080 1920 /tmp/frame.png
  ```
- **Design sampler** — `engine/design_sampler.py`: renders the same two
  real moments in 10 designs (1080×1920 stills in `assets/previews/`).
- **Design system** — 12 style presets (`presets/*.json`, schema in
  `presets/SCHEMA.md`), 8 transition + easing data presets
  (`presets/transitions/`), 7 SIL OFL fonts (`assets/fonts/`).
- **Search** — `scripts/search_assets.py`: describe a design in words,
  get ranked assets from `assets/registry.json`.
  ```sh
  python3 scripts/search_assets.py "romantic golden fireflies handwritten lyrics soft glow"
  ```
  Warm Fireflies ranks first, then the handwritten script fonts it pairs
  with (Great Vibes, Kaushan Script).
- **UI** — `app/index.html`: offline library page (search + category
  filters + preset gallery; real registry data embedded; fonts load via
  `@font-face`). Open it in any browser — `file://` works.

## Quickstart
```sh
# 1. verify the snapshot (see "Verifying" — the skill-pack check is
#    expected to fail here; it needs the full local studio)
python3 tests/run_tests.py

# 2. search the library
python3 scripts/search_assets.py "romantic golden fireflies handwritten lyrics soft glow"

# 3. new project: copy projects/sample/ to projects/<name>/, add your
#    lyrics.txt + assets/song.mp3, then:
scripts/sync.sh  projects/<name>                       # -> assets/words.json
scripts/render.sh projects/<name> 1080 1920 0 12 renders/out.mp4

# 4. browse the library — open app/index.html in any browser
```

## Sample project
`projects/sample/` is a synthetic 12-second end-to-end proof (3 lyric
lines, hand-written timings, no real song). Its render is
`renders/sample-test-9x16.mp4` (1080×1920, 24 fps, AAC, exactly 12.00 s).

## Verifying
`tests/run_tests.py` checks registry integrity, fonts, preset schema,
sample timestamps, skill discovery and the sample export. In this
snapshot 5 of 6 checks pass; the skill-discovery check fails because the
third-party skill packs live only in the full local studio (see below).
`scripts/sync.sh` is written for the author's local machine (it points at
a venv outside this repo) — on another machine, run `engine/align_words.py`
with your own torch/torchaudio environment instead.

## What is not in this repo
- `.agents/skills/` — third-party skill packs (HyperFrames, GSAP, …),
  installed locally only.
- Real-song project data (`projects/` beyond the synthetic sample) and
  render outputs beyond the sample test mp4.
- `work/`, `.venv/` — local build artefacts and virtual environments.

## Docs
- `docs/INSTALL.md` — layout, two-venv arrangement, pinned versions
- `docs/ENVIRONMENT.md` — measured machine facts
- `docs/LIMITATIONS.md` — blockers + the author's own-machine command list
- `docs/MANIFEST.md` — every component: version, license, honest status
- `docs/SKILLS.md` — skill installs, exact commands and outcomes

## License
MIT — see `LICENSE`. Fonts in `assets/fonts/` are SIL OFL 1.1 (see
`assets/registry.json` for each font's source and license).
