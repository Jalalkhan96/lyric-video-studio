#!/usr/bin/env python3
"""DESIGN 08 — KINETIC RED full renderer for Qarara Rasha.
Bold Montserrat type on cream, red diagonal band, per-word pop from the real
words.json timings. Modes:
  frame T W H out.png
  video W H T0 T1 out.mp4 [--audio-start S]
  thumb out.jpg
  all   -> renders/ (9:16 full, 16:9 full, 43s viral cut 9:16)"""
import json, math, os, subprocess, sys
from bisect import bisect_right
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Studio adaptation (2026-10-25): project data (lyrics.txt, assets/words.json,
# assets/song.mp3, optional project.json) resolves under LVS_PROJECT
# (default: the studio root). Fonts stay shared in the studio assets/fonts/.
# All Qarara-specific strings/timings are overridable via project.json.
ROOT = Path(__file__).resolve().parent.parent
PROJ = Path(os.environ.get("LVS_PROJECT", str(ROOT)))
FONTS = ROOT / "assets" / "fonts"
WORDS = json.loads((PROJ / "assets" / "words.json").read_text())
LINES_TXT = [l.rstrip("\n") for l in open(PROJ / "lyrics.txt") if l.strip()]
CFG = {}
_cf = PROJ / "project.json"
if _cf.exists(): CFG = json.loads(_cf.read_text())
BY_LINE = {}
for w in WORDS: BY_LINE.setdefault(w["line"], []).append(w)
STARTS = [BY_LINE[i][0]["s"] for i in range(len(BY_LINE))]
FIRST = STARTS[0]
TOTAL = float(CFG.get("total", 270.83))
FPS = 24
RED = (178, 34, 52)
CREAM = (245, 239, 228)
INK = (24, 22, 20)
EN = {0: "turn me into rain, so i may fall upon the beautiful face",
      1: "then make me a beloved — i walk with a burnt face",
      2: "i would sacrifice myself for the colour of her lips",
      3: "friends, help me reach my beloved — here i suffocate",
      8: "sorrows vanished when her beautiful face appeared",
      9: "then sorrow returned when her starry face disappeared",
      10: "make me yours, and i will build a palace of dreams",
      11: "make me a stranger, and i will break real palaces",
      16: "indeed i am ghani, yearning for the cup of her lips",
      17: "indeed i am maftoon, mad in the name of the beloved",
      18: "indeed i am khatir — i love purely",
      19: "indeed i am ismail — i love with my blood"}
HOOK_LINE = CFG.get("hook_line", "o qarara rasha")
for i in range(len(LINES_TXT)):
    if LINES_TXT[i].strip() == HOOK_LINE: EN[i] = "oh peace, come to me"
for i in (24, 25, 26, 27):
    if i < len(LINES_TXT) and (i - 24) in EN: EN[i] = EN[i - 24]
if "en" in CFG: EN.update({int(k): v for k, v in CFG["en"].items()})
TITLE1 = CFG.get("title_line1", "O QARARA"); TITLE2 = CFG.get("title_line2", "RASHA")
AMIRI_TXT = CFG.get("amiri_text", "قراره راشه")
ARTIST_LINE = CFG.get("artist_line", "ISMAIL & JUNAID")
SUBCREDIT = CFG.get("subcredit", "lyrics ismail khan  ·  rubab farhan bogra  ·  guitar junaid javed")
CREDIT_STRIP = CFG.get("credit_strip", "ISMAIL & JUNAID — QARAR")
HEADER_WORD = CFG.get("header_word", "QARAR")
WM_WORD = CFG.get("watermark_word", "QARAR")
HOOK_AMIRI = CFG.get("hook_amiri", "قراره راشه")
OUTRO_TITLE = CFG.get("outro_title", "O Qarara Rasha")
OUTRO_SUB = CFG.get("outro_sub", "pashto lyric video")

def F(name, size, wght=None):
    f = ImageFont.truetype(str(FONTS / name), max(8, int(size)))
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

def blend(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def active_line(t):
    i = bisect_right(STARTS, t) - 1
    return max(i, 0)
def fade(t, a, b): return max(0.0, min(1.0, (t - a) / max(b - a, 0.01)))

_BG, _WM, _FIT = {}, {}, {}

def bg(W, H, t):
    drift = int(12 * math.sin(t * 0.22))
    key = (W, H, drift)
    if key in _BG: return _BG[key].copy()
    img = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(img)
    top_l, top_r = H * 0.68 + drift, H * 0.58 + drift
    if H > W: top_l, top_r = H * 0.68 + drift, H * 0.58 + drift
    else: top_l, top_r = H * 0.74 + drift, H * 0.62 + drift
    d.polygon([(0, top_l), (W, top_r), (W, H), (0, H)], fill=RED + (255,))
    d.rectangle([int(W * 0.05), int(H * 0.10), int(W * 0.05) + max(4, int(10 * W / 1080)), int(H * 0.42)], fill=RED + (255,))
    _BG[key] = img
    return img.copy()

def watermark(W, H, kind, li=None):
    key = (W, H, kind, li)
    if key in _WM: return _WM[key]
    s = math.sqrt(W * H / (1080 * 1920))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    midy = H * 0.44
    if kind == "hook":
        f = F("Amiri.ttf", 300 * s); txt, col = HOOK_AMIRI, RED + (15,)
    elif kind == "verse":
        ws = [w["w"] for w in BY_LINE[li]]
        txt = max(ws, key=len).upper()
        f = F("Montserrat.ttf", 225 * s, 800); col = INK + (12,)
    else:
        txt = WM_WORD; f = F("Montserrat.ttf", 250 * s, 800); col = INK + (12,)
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, midy - 130 * s), txt, font=f, fill=col)
    _WM[key] = ov
    return ov

def center(d, y, txt, font, col):
    w = d.textlength(txt, font=font); d.text(((d.im.size[0] - w) / 2, y), txt, font=font, fill=col)

def row_pop(d, cx, y, items, base, t, s):
    """items: [(word, state, ws, we)] — Montserrat 800, current word pops + red."""
    fonts, widths = [], []
    for w, st, ws, we in items:
        pop = 1.0
        if st == "now": pop = 1 + 0.20 * max(0.0, 1 - (t - ws) / 0.25)
        f = F("Montserrat.ttf", base * pop, 800)
        fonts.append(f); widths.append(d.textlength(w, font=f))
    gap = 26 * s
    total = sum(widths) + gap * (len(items) - 1)
    x = cx - total / 2
    for (w, st, ws, we), f, wd in zip(items, fonts, widths):
        col = {"sung": INK + (255,), "now": RED + (255,), "next": INK + (100,)}[st]
        d.text((x, y), w, font=f, fill=col)
        if st == "now":
            uw = wd * min(1.0, (t - ws) / max(we - ws, 0.05) + 0.15)
            d.rectangle([x, y + base * 1.28, x + uw, y + base * 1.28 + 6 * s], fill=RED + (230,))
        x += wd + gap
    return total

def fit_base(d, items_words, base, maxw, s):
    b = base
    while b > 16 * s:
        f = F("Montserrat.ttf", b, 800)
        if sum(d.textlength(w, font=f) for w in items_words) + 26 * s * (len(items_words) - 1) <= maxw: return b
        b *= 0.94
    return b

def states(li, t):
    return [(w["w"], "sung" if w["e"] <= t else ("now" if w["s"] <= t else "next"), w["s"], w["e"])
            for w in BY_LINE[li]]

def draw(t, W, H):
    s = math.sqrt(W * H / (1080 * 1920))
    img = bg(W, H, t)
    d = ImageDraw.Draw(img, "RGBA")
    midy = H * 0.44
    # progress hairline
    d.rectangle([0, 0, W * t / TOTAL, 6 * s], fill=RED + (200,))
    if t < FIRST - 0.35:
        img.alpha_composite(watermark(W, H, "big"))
        d = ImageDraw.Draw(img, "RGBA")
        fa = fade(t, 1.6, 2.6)
        if fa > 0: center(d, H * 0.24, AMIRI_TXT, F("Amiri.ttf", 140 * s), blend(CREAM, RED, fa) + (255,))
        y1 = H * 0.355 - 14 * s * (1 - fade(t, 0.5, 0.9))
        if t >= 0.5: center(d, y1, TITLE1, F("Montserrat.ttf", 118 * s, 800), INK + (255,))
        y2 = y1 + 132 * s
        if t >= 1.1: center(d, y2, TITLE2, F("Montserrat.ttf", 118 * s, 800), RED + (255,))
        if t >= 2.4: center(d, H * 0.52, ARTIST_LINE, F("Montserrat.ttf", 30 * s, 700), INK + (255,))
        if t >= 3.2: center(d, H * 0.52 + 42 * s, SUBCREDIT,
                            F("Montserrat.ttf", 21 * s, 500), (110, 102, 92, 255))
        if t >= 4:
            center(d, H * 0.575, "I N S T R U M E N T A L   I N T R O", F("Montserrat.ttf", 20 * s, 600), (110, 102, 92, 255))
            bx0, bx1, by = W * 0.35, W * 0.65, H * 0.602
            d.rectangle([bx0, by, bx1, by + 5 * s], fill=INK + (50,))
            d.rectangle([bx0, by, bx0 + (bx1 - bx0) * t / FIRST, by + 5 * s], fill=RED + (255,))
        return img.convert("RGB")
    li = active_line(t)
    line_end = BY_LINE[li][-1]["e"]
    nxt = STARTS[li + 1] if li + 1 < len(STARTS) else TOTAL + 99
    if t > line_end + 2.0 and t < nxt - 0.1:  # interlude
        img.alpha_composite(watermark(W, H, "big"))
        d = ImageDraw.Draw(img, "RGBA")
        r = (34 + 9 * math.sin(t * 2.4)) * s
        d.ellipse([W / 2 - r, midy - r, W / 2 + r, midy + r], outline=RED + (220,), width=max(2, int(3 * s)))
        center(d, midy + 110 * s, "I N S T R U M E N T A L", F("Montserrat.ttf", 23 * s, 600), (110, 102, 92, 255))
        return img.convert("RGB")
    if TOTAL > 60 and t >= TOTAL - 6.23:  # outro (long songs only)
        img.alpha_composite(watermark(W, H, "big"))
        d = ImageDraw.Draw(img, "RGBA")
        fo = fade(t, TOTAL - 6.23, TOTAL - 5.43)
        center(d, midy - 90 * s, OUTRO_TITLE, F("GreatVibes.ttf", 88 * s), blend(CREAM, INK, fo) + (255,))
        center(d, midy + 30 * s, CREDIT_STRIP, F("Montserrat.ttf", 26 * s, 700), blend(CREAM, RED, fo) + (255,))
        center(d, midy + 78 * s, OUTRO_SUB, F("Montserrat.ttf", 21 * s, 500), (110, 102, 92, 255))
        return img.convert("RGB")
    is_hook = LINES_TXT[li].strip() == HOOK_LINE
    img.alpha_composite(watermark(W, H, "hook" if is_hook else "verse", li))
    d = ImageDraw.Draw(img, "RGBA")
    center(d, H * 0.115, HEADER_WORD, F("Montserrat.ttf", 30 * s, 700), INK + (230,))
    items = states(li, t)
    maxw = W - 130 * s
    if is_hook:
        center(d, midy - 320 * s, HOOK_AMIRI, F("Amiri.ttf", 150 * s), RED + (255,))
        b = fit_base(d, [w for w, *_ in items], 92 * s, maxw, s)
        row_pop(d, W / 2, midy - 130 * s, items, b, t, s)
    else:
        half = (len(items) + 1) // 2
        b1 = fit_base(d, [w for w, *_ in items[:half]], 52 * s, maxw, s)
        b2 = fit_base(d, [w for w, *_ in items[half:]], 74 * s, maxw, s)
        row_pop(d, W / 2, midy - 165 * s, items[:half], b1, t, s)
        row_pop(d, W / 2, midy - 55 * s, items[half:], b2, t, s)
    e = EN.get(li)
    if e: center(d, midy + 95 * s, e, F("Montserrat.ttf", 25 * s, 500), (96, 88, 78, 235))
    center(d, H * 0.80, CREDIT_STRIP, F("Montserrat.ttf", 21 * s, 600), CREAM + (225,))
    return img.convert("RGB")

def render_video(W, H, t0, t1, out, audio_start=0.0):
    n = int((t1 - t0) * FPS)
    cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio_start > 0: cmd += ["-ss", f"{audio_start:.2f}"]
    cmd += ["-i", str(PROJ / "assets" / "song.mp3"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k", "-shortest", str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for i in range(n):
        t = t0 + i / FPS
        p.stdin.write(draw(t, W, H).tobytes())
        if i % 480 == 0: print(f"{Path(out).name}: frame {i}/{n} (t={t:.0f}s)", flush=True)
    p.stdin.close(); p.wait()
    print(f"DONE {out} rc={p.returncode}", flush=True)

def thumb(out):
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(0, H * 0.78), (W, H * 0.60), (W, H), (0, H)], fill=RED)
    cover = Image.open(ROOT / "assets" / "soundcloud-cover.jpg").resize((430, 430))
    img.paste(cover, (W - 480, 110))
    d.rectangle([W - 480, 110, W - 50, 540], outline=RED, width=6)
    d.rectangle([48, 84, 58, 330], fill=RED)
    d.text((84, 96), "O QARARA", font=F("Montserrat.ttf", 84, 800), fill=INK)
    d.text((84, 196), "RASHA", font=F("Montserrat.ttf", 84, 800), fill=RED)
    d.text((86, 310), "قراره راشه", font=F("Amiri.ttf", 74), fill=RED)
    d.text((86, 420), "ISMAIL & JUNAID — QARAR", font=F("Montserrat.ttf", 27, 700), fill=INK)
    d.text((86, 462), "Pashto lyric video · word-by-word sync", font=F("Montserrat.ttf", 22, 500), fill=(110, 102, 92))
    d.text((86, H - 74), "FULL SONG", font=F("Montserrat.ttf", 24, 700), fill=CREAM)
    img.save(out, quality=92)
    print("DONE thumb", out, flush=True)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "frame":
        draw(float(a[1]), int(a[2]), int(a[3])).save(a[4]); print("frame ok")
    elif a[0] == "thumb":
        thumb(a[1])
    elif a[0] == "video":
        ast = float(a[6].split("=")[1]) if len(a) > 6 else 0.0
        render_video(int(a[1]), int(a[2]), float(a[3]), float(a[4]), a[5], ast)
    elif a[0] == "all":
        out = ROOT / "renders"; out.mkdir(exist_ok=True)
        render_video(1080, 1920, 0, TOTAL, out / "qarar-lyric-video-9x16.mp4")
        render_video(1920, 1080, 0, TOTAL, out / "qarar-lyric-video-16x9.mp4")
        render_video(1080, 1920, 228.0, TOTAL, out / "qarar-viral-cut-9x16.mp4", audio_start=228.0)
        thumb(out / "thumbnail-1280x720.jpg")
        print("ALL DONE", flush=True)
