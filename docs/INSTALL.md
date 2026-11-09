# Installation / layout

## Two-venv arrangement (deliberate)
- **Studio venv** — `~/workspace/lyric-video-studio/.venv`, created with
  `python3 -m venv --system-site-packages .venv`. It inherits system Pillow 10.2.0
  and runs the renderer, sampler, search and tests. Light (~15 MB), no torch.
- **Sync venv (referenced, not duplicated)** — `~/workspace/qarara-rasha-lyric-video/work/venv`
  holds the heavy, already-verified alignment stack. Reinstalling torch (~800 MB)
  into the studio would duplicate it for zero benefit, so `scripts/sync.sh` calls
  that venv's python. Pinned versions, verified by import on 2026-10-25:
  torch **2.14.1+cpu**, torchaudio **2.11.0+cpu**, demucs **4.1.0**, soundfile **0.14.0**,
  numpy 2.5.4. If the Qarara project is ever moved, recreate with:
  `pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.1 torchaudio==2.11.0`
  then `pip install demucs==4.1.0 soundfile==0.14.0`, and pre-fetch the Demucs +
  MMS_FA weights with `curl` into `~/.cache/torch/hub/checkpoints/` (torch's own
  downloader hangs through this proxy — verified on the Qarara build).

## Directory structure
The spec's structure was created as-is, with these adaptations:
- `assets/previews/` **added** — the 20 verified sampler stills the registry points at.
- Skills landed at the repo root (`.agents/skills/`, `.claude/skills/`, `skills/`,
  `agent/skills/`) because that is where the `skills` CLI installs them; the spec's
  `skills/` folder is one of its targets, not a folder we stock by hand.
- `adapters/` is reserved for Remotion / Motion Canvas backends (not installed — see
  MANIFEST.md). `app/` holds the offline library UI. Category folders under
  `assets/` and `presets/` exist and fill incrementally; empty ≠ broken.

## Fonts
`assets/fonts/` — 7 Google Fonts TTFs copied from the verified Qarara project set
(Cinzel, Great Vibes, Kaushan Script, Playfair Display, Cormorant Garamond,
Montserrat variable, Amiri). License: SIL OFL 1.1. The user's specified trio
(Kaushan Script, Playfair Display, Great Vibes) is included.

## Verify the install
```sh
cd ~/workspace/lyric-video-studio
.venv/bin/python tests/run_tests.py     # expect 8/8 PASS
```
