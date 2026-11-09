# Skill installation log — exact outcomes (2026-10-25)

All installs ran inside `~/workspace/lyric-video-studio/` with the `skills` CLI via `npx`.
A skill counts as installed only because its files are verified on disk (44 `SKILL.md`
files found; `skills-lock.json` records source + content hash per skill).

## 1. HyperFrames skills — INSTALLED ✅
Command: `npx -y skills add heygen-com/hyperframes --all --full-depth`
- The first invocation outlasted the 300 s tool window, but the install completed;
  verified afterwards on disk and in `skills-lock.json`. 14 skills:
  `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `figma`,
  `slideshow`, `remotion-to-hyperframes`, `canopy-part-title`, `code-slice-hero`,
  `cuboid-carousel`, `frost-sequence-camera-orbit`, `glass-shard-title`, `orbit-card`,
  `wireframe-portal-title`.
- The CLI fanned copies into `.agents/skills/`, `.claude/skills/`, `skills/` and
  `agent/skills/` (its multi-agent layout). Canonical read location used by the QA
  tests: `.agents/skills/`.
- Note: these are agent guidance skills (render contracts, CLI usage, registry blocks).
  The HyperFrames *renderer* itself needs headless Chrome — blocked in this sandbox
  (see LIMITATIONS.md). The skills are fully usable on the user's own machine.

## 2. GSAP skills — INSTALLED ✅ (second attempt)
- Attempt 1: `npx -y skills add greensock/gsap-skills` (no flags) → the CLI opened an
  **interactive multi-select prompt** (8 skills listed) and waited for keyboard input;
  killed by `timeout 100` (exit 124). Nothing installed. Non-interactive shells must
  pass `--all`.
- Attempt 2: `npx -y skills add greensock/gsap-skills --all` → exit 0 in ~7 s.
  8 skills: `gsap-core`, `gsap-frameworks`, `gsap-performance`, `gsap-plugins`,
  `gsap-react`, `gsap-scrolltrigger`, `gsap-timeline`, `gsap-utils`.
- `skills-lock.json` now records **22 skills** total, each with source repo and hash.

## 3. npm animation libraries — INSTALLED ✅
In `templates/_template-project/` (`npm init -y` + `npm install gsap roughjs lottie-web vivus`,
"added 8 packages in 8s", exit 0). Verified versions by reading each `package.json`:
gsap **3.15.0**, roughjs **4.6.6**, lottie-web **5.13.0**, vivus **0.4.6**.
These are browser-side libraries for HyperFrames/HTML compositions — usable wherever
a browser runs; they are not used by the PIL engine.

## Not attempted
- `npx hyperframes init` / `doctor`: pointless in this sandbox — project scaffolding
  would work, but every render path it sets up needs Chrome capture, which is blocked
  here. Run it on the user's machine (commands in LIMITATIONS.md).
- Additional skill collections from the spec (iart-ai/motion-skills, remotion-dev/skills,
  GitHub skill searches): not installed — the two requested collections already cover
  lyric sync guidance, kinetic type, GSAP timelines and registry blocks; adding more
  unverified third-party skills has real permission surface (skills run with agent
  permissions, as the CLI itself warns). Candidates are listed in MANIFEST.md as
  next integrations instead.
