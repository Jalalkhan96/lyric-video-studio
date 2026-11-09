# Known limitations

1. **This studio lives in the Linux sandbox, not on the user's computer.**
   Nothing here installs software on his Mac/Windows machine. The commands for his
   own machine are at the bottom of this file.
2. **Browser rendering is blocked here.** HyperFrames, Remotion and Motion Canvas
   all render by driving headless Chrome. In this sandbox, Chromium/Playwright
   cannot open any public page (`net::ERR_TUNNEL_CONNECTION_FAILED` through the
   authenticating proxy — verified, including for example.com). HTML compositions
   and their skills are installed and editable here, but final capture must happen
   on a machine with a working browser. The PIL engine is the working renderer
   in-sandbox and produced every video referenced by this studio.
3. **CPU only, 2 cores.** A 12 s 1080×1920 sample renders in ~11 s. A 4:31 song at
   24 fps takes minutes per format, not seconds. No GPU acceleration is available.
4. **Two-venv dependency.** Sync uses the Qarara project's venv by path
   (`scripts/sync.sh`). Moving/deleting that project breaks sync until the venv is
   recreated per `docs/INSTALL.md`.
5. **Data-only presets.** Romantic Pink, Anime Cinematic, Particle Visualizer and
   Minimalist Cards are defined as data (palette/fonts/layout) but have no PIL
   scene renderer yet; the registry and UI label them `data-only` rather than
   pretending otherwise.
6. **Alignment quality varies by language/material.** MMS_FA confidence was low
   (0.02–0.33) on repeated hook lines of the Qarara song even though spacing and
   the vocal-energy map confirmed the timings. The pipeline flags low-confidence
   lines in `work/timing-table.md`; always review flags before rendering.
7. **git-lfs is absent** and no uninstall script is provided beyond deleting the
   studio folder (nothing outside `~/workspace/lyric-video-studio/` was modified,
   except the `skills` CLI's own cache in the npm/npx store).

## On the user's own machine (Mac / Windows) — run these there
```sh
# macOS (Homebrew)                     # Windows (winget)
brew install node@22 ffmpeg python@3.11 git git-lfs
winget install OpenJS.NodeJS.LTS Gyan.FFmpeg Python.Python.3.11 Git.Git GitHub.GitLFS Google.Chrome

cd lyric-video-studio
npx skills add heygen-com/hyperframes --all --full-depth
npx skills add greensock/gsap-skills --all     # --all matters: without it the CLI waits at an interactive prompt
npx hyperframes init test-video
npx hyperframes doctor                          # fix what it reports, then render the test project
python3 -m venv .venv && .venv/bin/pip install torch torchaudio demucs soundfile pillow
```
