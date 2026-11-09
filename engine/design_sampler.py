#!/usr/bin/env python3
"""10 design samples for Qarara Rasha — same two real moments in every design:
verse line 1 @92.6s and hook line 29 @250.8s, 1080x1920, real words.json timings
drive the karaoke word colours. Usage: python3 work/design_sampler.py"""
import json, math, random, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os
ROOT = Path(__file__).resolve().parent.parent
PROJ = Path(os.environ.get("LVS_PROJECT", str(ROOT)))
FONTS = ROOT / "assets" / "fonts"
WORDS = json.loads((PROJ / "assets" / "words.json").read_text())
LINES_TXT = [l.rstrip("\n") for l in open(PROJ / "lyrics.txt") if l.strip()]
BY_LINE = {}
for w in WORDS: BY_LINE.setdefault(w["line"], []).append(w)
EN = {0: "i will become rain and fall on your beautiful face", 28: "oh peace, come to me"}
W, H = 1080, 1920
CX = W // 2
MIDY = int(H * 0.44)

def F(name, size, wght=None):
    f = ImageFont.truetype(str(FONTS / name), int(size))
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f
def blend(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def grad(top, bottom, horizon=1.0):
    img = Image.new("RGB", (W, H), top)
    d = ImageDraw.Draw(img)
    hh = int(H * horizon)
    for y in range(0, hh, 4):
        d.rectangle([0, y, W, y + 4], fill=blend(top, bottom, (y / max(hh, 1)) ** 1.4))
    if hh < H: d.rectangle([0, hh, W, H], fill=bottom)
    return img

def grain(img, amt=0.05):
    n = Image.effect_noise((W, H), 30).convert("L")
    return Image.blend(img, Image.merge("RGB", (n, n, n)), amt)

def vignette(img, strength=110):
    ov = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ov)
    d.ellipse([-W * 0.25, -H * 0.18, W * 1.25, H * 1.18], fill=strength)
    ov = ov.filter(ImageFilter.GaussianBlur(180))
    return Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), ov.point(lambda p: 255 - p // 3))

def stars(d, n, seed, ymax=None, col=(235, 230, 200)):
    ymax = ymax or int(H * 0.55)
    for k in range(n):
        r = random.Random(seed * 1000 + k)
        x, y = r.randint(10, W - 10), r.randint(10, ymax)
        s = r.choice([1.4, 1.4, 2.2, 3.0]); a = r.randint(50, 190)
        d.ellipse([x - s, y - s, x + s, y + s], fill=col + (a,))

def mountains(d, cols=((13, 28, 36), (7, 16, 21))):
    d.polygon([(0, H * 0.80), (W * 0.17, H * 0.62), (W * 0.34, H * 0.77), (W * 0.5, H * 0.58),
               (W * 0.69, H * 0.78), (W * 0.84, H * 0.64), (W, H * 0.79), (W, H), (0, H)], fill=cols[0])
    d.polygon([(0, H * 0.88), (W * 0.23, H * 0.73), (W * 0.44, H * 0.86), (W * 0.64, H * 0.71),
               (W, H * 0.87), (W, H), (0, H)], fill=cols[1])

def frame(d, col, inset=26, width=2, double=False):
    d.rectangle([inset, inset, W - inset, H - inset], outline=col, width=width)
    if double: d.rectangle([inset + 12, inset + 12, W - inset - 12, H - inset - 12], outline=col, width=1)

# ---------- shared lyric block ----------
def word_states(li, t):
    ws = BY_LINE[li]
    out = []
    for w in ws:
        st = "sung" if w["e"] <= t else ("now" if w["s"] <= t else "next")
        out.append((w["w"], st))
    return out

def fit_font(d, fname, words, base, maxw=W - 110, wght=None):
    size = int(base)
    while size > 14:
        f = F(fname, size, wght)
        if sum(d.textlength(w + " ", font=f) for w in words) <= maxw: return f
        size -= 3
    return F(fname, size, wght)

def row(d, cx, y, items, font, cols):
    """items: [(word, state)] — cols: dict state->color(rgba)"""
    total = sum(d.textlength(w + " ", font=font) for w, _ in items)
    x = cx - total / 2
    for w, st in items:
        lift = -6 if st == "now" else 0
        d.text((x, y + lift), w, font=font, fill=cols[st])
        x += d.textlength(w + " ", font=font)

def center(d, y, txt, font, col):
    w = d.textlength(txt, font=font); d.text(((W - w) / 2, y), txt, font=font, fill=col)

def lyric_block(img, li, t, pal, hook_amiri=True, base1=46, base2=60, y_off=0):
    """pal: text(sung), now, next, sub, fam1, fam2"""
    d = ImageDraw.Draw(img, "RGBA")
    items = word_states(li, t)
    is_hook = LINES_TXT[li].strip() == "o qarara rasha"
    cols = {"sung": pal["text"], "now": pal["now"], "next": pal["next"]}
    my = MIDY + y_off
    if is_hook:
        if hook_amiri:
            center(d, my - 320, "قراره راشه", F("Amiri.ttf", 150), pal["now"])
        row(d, CX, my - 130, items, fit_font(d, pal["fam2"], [w for w, _ in items], 96, wght=pal.get("w2")), cols)
    else:
        half = (len(items) + 1) // 2
        row(d, CX, my - 150, items[:half], fit_font(d, pal["fam1"], [w for w, _ in items[:half]], base1, wght=pal.get("w1")), cols)
        row(d, CX, my - 60, items[half:], fit_font(d, pal["fam2"], [w for w, _ in items[half:]], base2, wght=pal.get("w2")), cols)
    e = EN.get(li)
    if e: center(d, my + 70, e, F("Montserrat.ttf", 24, 500), pal["sub"])
    return d

def tag(d, num, name, col, y=None):
    f = F("Montserrat.ttf", 21, 600)
    txt = f"DESIGN {num:02d} · {name}"
    w = d.textlength(txt, font=f)
    d.text(((W - w) / 2, y or H - 74), txt, font=f, fill=col)

def credit(d, col, y=None):
    center(d, y or int(H * 0.775), "QARAR — ISMAIL & JUNAID", F("Montserrat.ttf", 20), col)

# ---------- the 10 designs ----------
def d01():  # Pashto Heritage (locked design)
    img = grad((22, 48, 62), (198, 108, 48), 0.62); d = ImageDraw.Draw(img, "RGBA")
    stars(d, 90, 1); mountains(d); frame(d, (212, 175, 55, 190))
    return img, {"text": (245, 238, 220, 255), "now": (255, 205, 90, 255), "next": (200, 205, 210, 130),
                 "sub": (205, 216, 224, 210), "fam1": "GreatVibes.ttf", "fam2": "PlayfairDisplay.ttf"}

def d02():  # Minimal Sketch (PDF style 1)
    img = Image.new("RGB", (W, H), (243, 233, 216)); d = ImageDraw.Draw(img, "RGBA")
    ink = (74, 44, 36)
    pts = [(x, int(H * 0.74 + 46 * math.sin(x / 130.0) + 20 * math.sin(x / 47.0))) for x in range(0, W, 8)]
    d.line(pts, fill=ink + (200,), width=3)
    pts2 = [(x, int(H * 0.79 + 34 * math.sin(x / 170.0 + 2))) for x in range(0, W, 8)]
    d.line(pts2, fill=ink + (120,), width=2)
    d.ellipse([W * 0.70, H * 0.13, W * 0.70 + 120, H * 0.13 + 120], outline=(222, 152, 120, 255), width=4)
    for k in range(26):
        r = random.Random(k * 31); x, y = r.randint(20, W - 20), r.randint(20, int(H * 0.4))
        d.ellipse([x - 1.6, y - 1.6, x + 1.6, y + 1.6], fill=(74, 44, 36, 90))
    return img, {"text": (74, 44, 36, 255), "now": (196, 98, 55, 255), "next": (74, 44, 36, 105),
                 "sub": (74, 44, 36, 170), "fam1": "KaushanScript.ttf", "fam2": "PlayfairDisplay.ttf"}

def d03():  # Warm Fireflies (PDF style 2)
    img = grad((26, 16, 6), (74, 44, 12), 1.0)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for k in range(85):
        r = random.Random(k * 77 + 5)
        x, y = r.randint(15, W - 15), r.randint(15, H - 15)
        s = r.uniform(2, 6)
        for rr, a in ((s * 4, 26), (s * 2.2, 60), (s, 190)):
            od.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(237, 180, 92, a))
    img = Image.alpha_composite(img.convert("RGBA"), ov.filter(ImageFilter.GaussianBlur(3))).convert("RGB")
    d = ImageDraw.Draw(img, "RGBA"); frame(d, (237, 180, 92, 110))
    return img, {"text": (255, 236, 200, 255), "now": (255, 197, 66, 255), "next": (255, 236, 200, 110),
                 "sub": (237, 180, 92, 200), "fam1": "GreatVibes.ttf", "fam2": "CormorantGaramond.ttf"}

def tree(d, x, y, ang, ln, wdt, col, depth):
    if depth == 0 or ln < 6: return
    x2, y2 = x + ln * math.cos(ang), y - ln * math.sin(ang)
    d.line([x, y, x2, y2], fill=col, width=max(1, int(wdt)))
    tree(d, x2, y2, ang - 0.38, ln * 0.74, wdt * 0.7, col, depth - 1)
    tree(d, x2, y2, ang + 0.30, ln * 0.74, wdt * 0.7, col, depth - 1)

def d04():  # Red Moon Tree (PDF style 3)
    img = grad((13, 16, 46), (30, 22, 62), 1.0); d = ImageDraw.Draw(img, "RGBA")
    stars(d, 70, 4)
    d.ellipse([W * 0.56, H * 0.07, W * 0.56 + 330, H * 0.07 + 330], fill=(178, 34, 52, 255))
    d.ellipse([W * 0.56, H * 0.07, W * 0.56 + 330, H * 0.07 + 330], outline=(220, 80, 95, 160), width=3)
    tree(d, W * 0.80, H * 0.86, math.pi / 2, 190, 13, (5, 5, 10, 255), 8)
    d.rectangle([0, H * 0.86, W, H], fill=(5, 5, 10))
    for k in range(14):
        r = random.Random(k * 53 + 2); x, y = r.randint(int(W * 0.45), W - 30), r.randint(int(H * 0.3), int(H * 0.8))
        d.ellipse([x - 5, y - 3, x + 5, y + 3], fill=(200, 50, 70, 200))
    return img, {"text": (240, 238, 248, 255), "now": (255, 120, 130, 255), "next": (240, 238, 248, 110),
                 "sub": (200, 195, 220, 190), "fam1": "GreatVibes.ttf", "fam2": "CormorantGaramond.ttf"}

def d05():  # Neon Noir Gold
    img = Image.new("RGB", (W, H), (5, 5, 8)); d = ImageDraw.Draw(img, "RGBA")
    frame(d, (212, 175, 55, 220), double=True)
    for k in range(4):
        y = int(H * (0.30 + 0.14 * k))
        d.line([90, y, W - 90, y], fill=(212, 175, 55, 26), width=1)
    center(d, int(H * 0.16), "Q A R A R", F("Cinzel.ttf", 40), (212, 175, 55, 230))
    return img, {"text": (255, 244, 214, 255), "now": (255, 205, 60, 255), "next": (255, 244, 214, 100),
                 "sub": (212, 175, 55, 190), "fam1": "Montserrat.ttf", "fam2": "Cinzel.ttf", "w1": 600}

def d06():  # Cinematic Serif
    img = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, W, int(H * 0.13)], fill=(0, 0, 0)); d.rectangle([0, H - int(H * 0.13), W, H], fill=(0, 0, 0))
    center(d, int(H * 0.155), "A  P A S H T O  B A L L A D", F("Montserrat.ttf", 20), (170, 170, 175, 200))
    img = grain(img.convert("RGB"), 0.04); d = ImageDraw.Draw(img, "RGBA")
    return img, {"text": (245, 243, 238, 255), "now": (232, 197, 132, 255), "next": (245, 243, 238, 100),
                 "sub": (180, 178, 172, 200), "fam1": "CormorantGaramond.ttf", "fam2": "PlayfairDisplay.ttf"}

def d07():  # Constellation / COTODAMA
    img = grad((7, 12, 34), (16, 26, 58), 1.0); d = ImageDraw.Draw(img, "RGBA")
    stars(d, 150, 7, ymax=int(H * 0.8))
    pts = []
    for k in range(9):
        a = k * 2 * math.pi / 9 - math.pi / 2
        pts.append((CX + 330 * math.cos(a), MIDY - 130 + 330 * math.sin(a)))
    d.line(pts + [pts[0]], fill=(150, 180, 255, 90), width=2)
    for x, y in pts: d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(220, 230, 255, 255))
    d.ellipse([CX - 355, MIDY - 485, CX + 355, MIDY + 225], outline=(150, 180, 255, 60), width=1)
    return img, {"text": (238, 242, 255, 255), "now": (160, 200, 255, 255), "next": (238, 242, 255, 110),
                 "sub": (170, 190, 230, 200), "fam1": "CormorantGaramond.ttf", "fam2": "CormorantGaramond.ttf"}

def d08():  # JIZURA Kinetic
    img = Image.new("RGB", (W, H), (245, 239, 228)); d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(0, H * 0.66), (W, H * 0.56), (W, H), (0, H)], fill=(178, 34, 52))
    d.rectangle([54, int(H * 0.10), 64, int(H * 0.42)], fill=(178, 34, 52))
    center(d, int(H * 0.115), "QARAR", F("Montserrat.ttf", 30, 700), (20, 20, 20, 220))
    return img, {"text": (20, 20, 20, 255), "now": (178, 34, 52, 255), "next": (20, 20, 20, 105),
                 "sub": (90, 84, 74, 210), "fam1": "Montserrat.ttf", "fam2": "Montserrat.ttf", "w1": 800, "w2": 800}

def star8(d, cx, cy, r, col, width=2):
    pts = []
    for k in range(16):
        rr = r if k % 2 == 0 else r * 0.52
        a = k * math.pi / 8 - math.pi / 2
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, outline=col, width=width)

def d09():  # Emerald Mehfil
    img = grad((6, 42, 34), (10, 66, 52), 1.0); d = ImageDraw.Draw(img, "RGBA")
    gold = (201, 168, 92, 200)
    for x in range(70, W, 130): star8(d, x, 70, 30, gold); star8(d, x, H - 70, 30, gold)
    for y in range(200, H - 130, 130): star8(d, 70, y, 30, gold); star8(d, W - 70, y, 30, gold)
    frame(d, gold, inset=110, width=1)
    return img, {"text": (246, 240, 222, 255), "now": (226, 192, 110, 255), "next": (246, 240, 222, 110),
                 "sub": (201, 190, 150, 200), "fam1": "GreatVibes.ttf", "fam2": "PlayfairDisplay.ttf"}

def d10():  # Dusty Rose Vintage
    img = grad((74, 48, 46), (46, 30, 34), 1.0); d = ImageDraw.Draw(img, "RGBA")
    frame(d, (232, 205, 190, 170), inset=34, width=2, double=True)
    stars(d, 30, 10, ymax=int(H * 0.3), col=(240, 215, 200))
    img = vignette(grain(img, 0.06), 130); d = ImageDraw.Draw(img, "RGBA")
    frame(d, (232, 205, 190, 150), inset=34, width=2, double=True)
    return img, {"text": (248, 238, 228, 255), "now": (240, 186, 158, 255), "next": (248, 238, 228, 110),
                 "sub": (226, 200, 186, 200), "fam1": "CormorantGaramond.ttf", "fam2": "GreatVibes.ttf"}

DESIGNS = [(1, "PASHTO HERITAGE", d01), (2, "MINIMAL SKETCH", d02), (3, "WARM FIREFLIES", d03),
           (4, "RED MOON TREE", d04), (5, "NEON NOIR GOLD", d05), (6, "CINEMATIC SERIF", d06),
           (7, "CONSTELLATION", d07), (8, "KINETIC RED", d08), (9, "EMERALD MEHFIL", d09),
           (10, "DUSTY ROSE VINTAGE", d10)]
MOMENTS = [(0, 92.6, "verse"), (28, 250.8, "hook")]

def main():
    out = PROJ / "previews" / "designs"; out.mkdir(parents=True, exist_ok=True)
    for num, name, fn in DESIGNS:
        for li, t, mtag in MOMENTS:
            img, pal = fn()
            d = lyric_block(img, li, t, pal)
            tagcol = (255, 255, 255, 150) if num not in (2, 8) else ((245, 239, 228, 210) if num == 8 else (40, 30, 25, 170))
            if num == 8 and mtag == "hook": pass
            tag(d, num, name, tagcol, y=H - 165 if num == 9 else None)
            img.save(out / f"design{num:02d}-{mtag}.jpg", quality=90)
        print(f"design {num:02d} {name} done")

if __name__ == "__main__":
    main()
