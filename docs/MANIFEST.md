# Component manifest — status is honest: installed / data-only / blocked / not installed

| Component | Version | License | Status | Evidence |
|---|---|---|---|---|
| PIL render engine (`engine/render_kinetic.py`) | studio copy of Qarara renderer | user's own work | **Installed, verified-video** | sample render + 3 full Qarara videos rendered with this code |
| Design sampler (`engine/design_sampler.py`) | studio copy | user's own work | **Installed, verified-stills** | 20 stills in `assets/previews/` |
| Alignment (`engine/align_words.py`, Demucs + MMS_FA) | demucs 4.1.0, torch 2.14.1+cpu, torchaudio 2.11.0+cpu | MIT / BSD-style | **Installed (referenced venv), verified** | Qarara `words.json`: 187 words / 32 lines, cross-checked vs vocal-energy map |
| FFmpeg | 8.1.2 (system) | LGPL/GPL | **Installed, verified** | probes throughout this build |
| Node.js / npm | v24.22.1 / 10.9.4 (system) | MIT | **Installed, verified** | npm installs below |
| gsap / roughjs / lottie-web / vivus | 3.15.0 / 4.6.6 / 5.13.0 / 0.4.6 | GSAP free license / BSD / MIT / MIT | **Installed** in `templates/_template-project/` | `package.json` versions read back |
| HyperFrames agent skills (14) | from heygen-com/hyperframes | per repo; GSAP assets inside blocks carry `GSAP-NOTICE.txt` | **Installed** | `skills-lock.json` + `SKILL.md` files |
| GSAP agent skills (8) | from greensock/gsap-skills | per repo | **Installed** | `skills-lock.json` (22 total) |
| HyperFrames renderer (HTML→video) | — | — | **BLOCKED in this sandbox** | needs headless Chrome capture; Chromium cannot traverse the sandbox proxy (verified). Works on the user's machine |
| Remotion | — | company license terms | **Not installed** | same Chrome dependency as HyperFrames + a second React render pipeline; `remotion-to-hyperframes` skill present if ever needed. No benefit here |
| Motion Canvas | — | MIT | **Not installed** | browser-based editor/renderer; same blocker class |
| Three.js / p5.js | — | MIT | **Not installed** | WebGL/browser libraries; no browser runtime in the sandbox. Add to the template project on the user's machine if shader/3D scenes are wanted |
| Whisper / WhisperX / stable-ts | — | MIT | **Not installed — deliberate** | The verified pipeline already does word-level forced alignment (MMS_FA) for Roman Pashto/Urdu/English from a known `lyrics.txt`. WhisperX would re-download large models to do the same job; stable-ts wraps Whisper (transcription, not alignment). Revisit only if lyrics-free transcription becomes a requirement |
| Audacity | — | GPL | **Not installed — deliberate** | GUI application; no display in the sandbox. FFmpeg covers trim/fade/normalize/analysis headlessly |
| Git LFS | — | MIT | **Not installed** | git 2.43 present without it; nothing in the studio needs LFS yet |
| Style presets | 12 in `presets/` | user's own work | **7 verified-stills, 1 verified-video, 4 data-only** | per-preset `renderer.support` field |
| Asset registry | 31 entries | — | **Verified** | `tests/run_tests.py` checks every referenced file exists |

## Prioritized next integrations
1. **On the user's Mac/Windows**: HyperFrames init + doctor + first HTML render
   (commands in LIMITATIONS.md) — unlocks the browser render path and the GSAP
   template project.
2. Port sampler palettes 02–07, 09, 10 into `render_kinetic.py`-style PIL scene
   functions so "verified-stills" presets become "verified-video".
3. Audio-reactive layer (RMS-driven particles/waveform) for the particle-visualizer
   preset; beat-grid detection for beat-cut transitions.
4. Review-then-install candidate skill collections: `iart-ai/motion-skills`,
   `remotion-dev/skills` (read manifests first; skills execute with agent permissions).
5. LRC/subtitle import-export in the sync module; manual timestamp-correction UI
   in `app/`.
