#!/usr/bin/env python3
"""Search the studio asset registry with a natural-language description.

Scoring: word overlap between the query and each entry's name/tags/style/category
(name hits weigh 3, tags 2, style/category 1). Prints ranked matches.

Usage: python3 scripts/search_assets.py "romantic golden fireflies handwritten lyrics soft glow"
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def words(s): return set(re.findall(r"[a-z0-9]+", str(s).lower()))

def main():
    if len(sys.argv) < 2:
        print("usage: search_assets.py \"<description>\""); return 1
    q = words(" ".join(sys.argv[1:]))
    reg = json.loads((ROOT / "assets" / "registry.json").read_text())
    scored = []
    for e in reg["entries"]:
        score = (3 * len(q & words(e["name"])) + 2 * len(q & words(" ".join(e.get("tags", []))))
                 + len(q & words(e.get("style", ""))) + len(q & words(e["category"])))
        if score: scored.append((score, e))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        print("no matches"); return 0
    for score, e in scored:
        print(f"{score:3d}  [{e['category']}] {e['name']} — {e.get('style', '')}")
        print(f"      id={e['id']}  preview={e.get('preview')}  renderer={e.get('renderer')}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
