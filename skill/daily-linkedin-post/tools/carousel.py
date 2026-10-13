"""Render a LinkedIn PDF carousel (1080x1350 pages) in the Neon Terminal style.

Usage:  python3 carousel.py slides.json out.pdf      (also writes out-cover.png)
Env:    LI_NAME / LI_HANDLE (signature), LI_ICONS (icon folder override)

slides.json:
{ "kicker": "BACKEND / CHECKLIST", "accent": "cyan",
  "slides": [
    {"type": "cover",   "title": "5 checks before you ship", "subtitle": "Short line under the title", "icon": "rocket"},
    {"type": "point",   "n": 1, "title": "Point title", "lines": ["One or two short lines"], "code": ["optional", "code lines"], "icon": "layers", "color": "cyan"},
    {"type": "compare", "title": "X vs Y", "left": {"h": "X", "items": ["..."]}, "right": {"h": "Y", "items": ["..."]}},
    {"type": "cta",     "title": "Save this for later", "question": "One question that divides experienced engineers?"}
  ]}
Keep 6 to 10 slides, one idea per slide, at most ~35 words per slide.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import style
from style import *
X, CW = 64, 952
COL = dict(cyan=CYAN, violet=VIOLET, pink=PINK, coral=CORAL, lime=LIME, emerald=EMERALD, amber=AMBER, blue=BLUE)

def wrap(c, x, y, s, font, size, fill, width, lh=1.3):
    f = F(font, size); line = ""
    for w in s.split():
        t = (line + " " + w).strip()
        if c.d.textlength(t, font=f) > width and line:
            c.d.text((x, y), line, font=f, fill=fill); y += int(size * lh); line = w
        else: line = t
    if line: c.d.text((x, y), line, font=f, fill=fill); y += int(size * lh)
    return y

def render(spec, out):
    acc = COL.get(spec.get("accent", "cyan"), CYAN); S = spec["slides"]; n = len(S); pages = []
    for i, s in enumerate(S, 1):
        c = NeonCanvas(); col = COL.get(s.get("color", ""), acc); t = s["type"]
        c.pill(X, 60, spec.get("kicker", "").upper(), acc, size=22)
        c.text(1080 - 64 - 70, 70, f"{i}/{n}", MONO_B, 24, fill=DIM)
        c.d.rounded_rectangle([64, 1296, 600, 1302], 3, fill=(30, 33, 50))
        c.d.rounded_rectangle([64, 1296, 64 + int(536 * i / n), 1302], 3, fill=acc)
        c.signature()
        if t == "cover":
            if s.get("icon"): c.icon_tile(X, 300, s["icon"], acc, size=130)
            y = wrap(c, X, 500, s["title"], SANS_B, 84, INK, CW, 1.1)
            if s.get("subtitle"): wrap(c, X, y + 30, s["subtitle"], SANS_R, 40, SUB, CW)
            c.text(X, 1180, "Swipe  ->", MONO_B, 28, fill=acc)
        elif t == "point":
            if s.get("n"): c.pill(X, 150, f"{s['n']} OF {sum(1 for q in S if q['type']=='point')}", col, size=22)
            if s.get("icon"): c.icon_tile(X, 240, s["icon"], col, size=130)
            y = wrap(c, X, 410, s["title"], SANS_B, 72, INK, CW, 1.12) + 24
            code = s.get("code", [])
            c.card(X, y, CW, min(1262 - y, 760), accent=col)
            yy = y + 44
            for l in s.get("lines", []): yy = wrap(c, X + 40, yy, l, SANS_B if l is s["lines"][0] else SANS_R, 40, INK if l is s["lines"][0] else SUB, CW - 80, 1.28) + 18
            if code:
                c.d.rounded_rectangle([X + 40, yy, X + CW - 40, yy + 36 + len(code) * 40], 14, fill=(14, 18, 34))
                for j, l in enumerate(code): c.d.text((X + 60, yy + 18 + j * 40), l, font=F(MONO, 25), fill=col)
        elif t == "compare":
            y = wrap(c, X, 170, s["title"], SANS_B, 60, INK, CW, 1.15) + 40
            for j, side in enumerate(("left", "right")):
                d = s[side]; x = X + j * 486; cc = EMERALD if j == 1 else CORAL
                h = 120 + 100 * max(len(s["left"]["items"]), len(s["right"]["items"]))
                c.card(x, y, 466, min(h, 1200 - y), accent=cc)
                c.text(x + 28, y + 30, d["h"], SANS_B, 38, fill=cc); yy = y + 100
                for it in d["items"]: yy = wrap(c, x + 28, yy, "- " + it, SANS_R, 30, SUB, 410) + 14
        elif t == "cta":
            if s.get("icon", "bookmark"): c.icon_tile(X, 260, s.get("icon", "bookmark"), VIOLET, size=110)
            y = wrap(c, X, 430, s["title"], SANS_B, 72, INK, CW, 1.12) + 30
            if s.get("question"):
                c.card(X, y, CW, 300, accent=acc); wrap(c, X + 36, y + 44, s["question"], SANS_B, 38, acc, CW - 72, 1.3)
        pages.append(c.img.convert("RGB"))
    pages[0].save(out, save_all=True, append_images=pages[1:], resolution=150)
    pages[0].save(out.replace(".pdf", "-cover.png"))
    return out

if __name__ == "__main__":
    print(render(json.load(open(sys.argv[1])), sys.argv[2]))
