#!/usr/bin/env python3
"""Lyric Video Studio QA — run: python3 tests/run_tests.py
Checks registry integrity, fonts, preset schema, timestamp validity, skill
discovery, and the sample export. Prints a pass/fail table; exit 1 on failure."""
import json, subprocess, sys
from pathlib import Path
from PIL import ImageFont

ROOT = Path(__file__).resolve().parent.parent
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))

# 1. registry valid + referenced files exist
try:
    reg = json.loads((ROOT / "assets" / "registry.json").read_text())
    missing = []
    for e in reg["entries"]:
        for ref in [e.get("preview"), (e.get("params") or {}).get("file"),
                    (e.get("params") or {}).get("verse_preview"), (e.get("params") or {}).get("hook_preview")]:
            if ref and not (ROOT / ref).exists(): missing.append(f"{e['id']}:{ref}")
    check("registry JSON valid", True, f"{len(reg['entries'])} entries")
    check("registry referenced files exist", not missing, "; ".join(missing) or "all present")
except Exception as ex:
    check("registry JSON valid", False, str(ex))

# 2. fonts present + loadable
try:
    fonts = sorted((ROOT / "assets" / "fonts").glob("*.ttf"))
    bad = []
    for f in fonts:
        try: ImageFont.truetype(str(f), 40).getmask("Ag").getbbox()
        except Exception: bad.append(f.name)
    check("fonts loadable via PIL", len(fonts) == 7 and not bad, f"{len(fonts)} TTFs" + (f" bad={bad}" if bad else ""))
except Exception as ex:
    check("fonts loadable via PIL", False, str(ex))

# 3. preset schema
REQ = {"id", "name", "palette", "fonts", "background", "layout", "transitions", "animation", "renderer"}
try:
    presets = sorted((ROOT / "presets").glob("*.json"))
    bad = [p.name for p in presets if not REQ <= set(json.loads(p.read_text()))]
    check("preset schema (12 presets)", len(presets) == 12 and not bad, f"{len(presets)} files" + (f" bad={bad}" if bad else ""))
    trans = list((ROOT / "presets" / "transitions").glob("*.json"))
    check("transition/easing data files", len(trans) == 9, f"{len(trans)} files (8 transitions + easings)")
except Exception as ex:
    check("preset schema", False, str(ex))

# 4. timestamp validation on sample words.json
try:
    words = json.loads((ROOT / "projects" / "sample" / "assets" / "words.json").read_text())
    ok = all(w["s"] < w["e"] for w in words)
    mono = all(words[i]["s"] <= words[i + 1]["s"] for i in range(len(words) - 1))
    overlap = any(words[i]["e"] > words[i + 1]["s"] + 1e-9 for i in range(len(words) - 1))
    check("sample words.json timestamps", ok and mono and not overlap,
          f"{len(words)} words, monotonic={mono}, overlap={overlap}")
except Exception as ex:
    check("sample words.json timestamps", False, str(ex))

# 5. skill discovery
skills = list((ROOT / ".agents" / "skills").glob("*/SKILL.md"))
check("skills discoverable (SKILL.md)", len(skills) == 22, f"{len(skills)} skills in .agents/skills")

# 6. sample export probe
try:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height,r_frame_rate", "-show_entries", "format=duration",
                          "-of", "json", str(ROOT / "renders" / "sample-test-9x16.mp4")],
                         capture_output=True, text=True).stdout
    info = json.loads(out)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"]["duration"])
    ok = (v["width"], v["height"]) == (1080, 1920) and v["r_frame_rate"] == "24/1" and a is not None and abs(dur - 12) < 0.5
    check("sample export probe", ok, f"{v['width']}x{v['height']} @ {v['r_frame_rate']}, audio={'yes' if a else 'NO'}, {dur:.2f}s")
except Exception as ex:
    check("sample export probe", False, str(ex))

w = max(len(n) for n, _, _ in results)
fails = 0
print(f"{'TEST':<{w}}  RESULT  DETAIL")
for n, ok, d in results:
    print(f"{n:<{w}}  {'PASS' if ok else 'FAIL':<6}  {d}")
    fails += 0 if ok else 1
print(f"\n{len(results) - fails}/{len(results)} passed")
sys.exit(1 if fails else 0)
