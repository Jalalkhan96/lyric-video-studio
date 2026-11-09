# Environment inspection — 2026-10-25

Inspected live on the machine where this studio was built (the Muse Linux sandbox).

| Item | Result |
|---|---|
| OS | Ubuntu 24.04.5 LTS, kernel 7.0.0-39-generic, x86_64 |
| CPU | 2 cores allocated (host: AMD EPYC 9D25) |
| RAM | Host-reported figures describe the shared host, not this sandbox — not used for planning |
| Disk | 100 GB volume, 66 GB free at inspection; studio total ≈ 81 MB |
| GPU | None (`/dev/nvidia*` absent, no `nvidia-smi`) — all rendering/alignment is CPU |
| Node.js | v24.22.1 |
| npm | 10.9.4 (works through the proxy; installs verified) |
| Python | 3.12.3 (system), pip 24.0 |
| Pillow | 10.2.0 (system site-packages) |
| FFmpeg | 8.1.2 |
| Git | 2.43.0 — **git-lfs NOT installed** (`git: 'lfs' is not a git command`) |
| Chrome/Chromium | No usable browser: Chromium/Playwright cannot reach the public web from this sandbox (proxy tunnel fails, verified previously) |

Network: egress via an authenticating HTTP proxy. `curl`, `pip` and `npm` work;
browser automation does not. See `LIMITATIONS.md` for what this blocks.
