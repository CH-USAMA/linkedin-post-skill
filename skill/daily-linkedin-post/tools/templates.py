"""
Visual Rotation templates for daily-linkedin-post.

T1 news_card        real photo + white/yellow headline + source screenshot inset
T2 screenshot_card  solid yellow page + highlighted real screenshot + handwritten note + fix bar
T3 proof_card       light page + real screenshot with red circles/arrows + checklist
T4 light_carousel   cream/white PDF carousel with colorful cards and Lucide icons
T5 text only        no image (write the caption only)
T6 Neon Terminal    style.py (old dark style)

Usage:
    import sys; sys.path.insert(0, "<skill>/tools"); from templates import *
Fonts live in <skill>/assets/fonts (Anton, Inter, JetBrains Mono, Caveat; all OFL). Run tools/fetch_fonts.py once.
Icons: <skill>/assets/icons/{lucide,brands}/*.svg (setup.sh fetches Lucide) (needs: pip install cairosvg --break-system-packages).
Screenshots: capture(url, {"name": (x, y, w, h)}, outdir) uses Playwright + the HTTPS_PROXY env if set.
Signature text: LI_NAME env var. Every image source must be lawful (own screenshots, official pages, Unsplash/Pexels, Wikimedia). Never
another page's branded card, news agency photos, or AI images of real people.
"""
import os, io, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = os.environ.get("LS_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FONTS = os.path.join(ROOT, "assets", "fonts")
ICONS = os.path.join(ROOT, "assets", "icons")
ANTON = os.path.join(FONTS, "Anton.ttf")
MONO = os.path.join(FONTS, "JBMono.ttf")
HAND = os.path.join(FONTS, "Caveat.ttf")
def INTER(w):   # Black ExtraBold Bold SemiBold Medium Regular (.ttf from fetch_fonts.py, or .otf)
    for ext in (".ttf", ".otf"):
        p = os.path.join(FONTS, f"Inter-{w}{ext}")
        if os.path.exists(p): return p
    return os.path.join(FONTS, f"Inter-{w}.ttf")

YEL = (255, 212, 0); BLK = (12, 12, 12); WHITE = (255, 255, 255); RED = (230, 30, 40)
CREAM = (251, 247, 239); INK = (20, 22, 28); MUTE = (95, 99, 110)
BLUE = (37, 99, 235); GREEN = (22, 163, 74); ORANGE = (249, 115, 22); PURPLE = (124, 58, 237); PINK = (219, 39, 119)
TINT = {BLUE: (224, 234, 255), GREEN: (220, 245, 228), ORANGE: (255, 234, 214), PURPLE: (237, 228, 255),
        PINK: (252, 228, 240), RED: (254, 226, 226), YEL: (255, 244, 194)}
NOLIG = dict(features=["-calt", "-liga"])
W, H = 1080, 1350
SIGNATURE = os.environ.get("LI_NAME", "Your Name")

def F(path, size): return ImageFont.truetype(path, size)
def I(weight, size): return F(INTER(weight), size)

# ---------- generic helpers ----------
def cover(img, w, h, fx=0.5, fy=0.5):
    r = max(w / img.width, h / img.height)
    im = img.resize((int(img.width * r) + 1, int(img.height * r) + 1), Image.LANCZOS)
    x = int((im.width - w) * fx); y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))

def rounded(im, rad):
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), rad, fill=255)
    out = im.convert("RGBA"); out.putalpha(m); return out

def shadow_paste(base, card, x, y, blur=24, off=(0, 14), alpha=150):
    sh = Image.new("RGBA", (card.width + blur * 4, card.height + blur * 4), (0, 0, 0, 0))
    a = card.split()[-1].point(lambda v: alpha if v > 0 else 0)
    k = Image.new("RGBA", card.size, (0, 0, 0, 255)); k.putalpha(a)
    sh.paste(k, (blur * 2, blur * 2), k); sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh, (x - blur * 2 + off[0], y - blur * 2 + off[1])); base.alpha_composite(card, (x, y))

def screenshot_on_card(img, width, pad=20, rad=18, rotate=0.0, top_pad=None):
    img = img.convert("RGB"); img = img.resize((width, int(img.height * width / img.width)), Image.LANCZOS)
    tp = pad if top_pad is None else top_pad
    card = Image.new("RGB", (img.width + pad * 2, img.height + tp + pad), WHITE); card.paste(img, (pad, tp))
    card = rounded(card, rad)
    return card.rotate(rotate, expand=True, resample=Image.BICUBIC) if rotate else card

def highlight(img, boxes):
    """Marker highlight on a screenshot. boxes = [((x0,y0,x1,y1), color)] in screenshot pixels."""
    img = img.convert("RGB"); hl = Image.new("RGB", img.size, WHITE); hd = ImageDraw.Draw(hl)
    for b, c in boxes: hd.rounded_rectangle(b, 8, fill=c)
    return ImageChops.multiply(img, hl)

def rich_line(d, x, y, parts, font, pad=(14, 6), hl=YEL, fg=WHITE, hl_fg=BLK):
    """parts = [(text, highlighted_bool)]"""
    cx = x
    for t, h in parts:
        bb = d.textbbox((cx, y), t, font=font)
        if h:
            d.rectangle((bb[0] - pad[0], bb[1] - pad[1], bb[2] + pad[0], bb[3] + pad[1]), fill=hl)
            d.text((cx, y), t, font=font, fill=hl_fg); cx = bb[2] + pad[0] * 2
        else:
            d.text((cx, y), t, font=font, fill=fg); cx = bb[2]
    return cx

def wrap(d, text, font, maxw):
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def draw_wrapped(d, x, y, text, font, maxw, fill, lh):
    for l in wrap(d, text, font, maxw): d.text((x, y), l, font=font, fill=fill); y += lh
    return y

def scribble(d, box, color=RED, w=5, loops=2, seed=4):
    rnd = random.Random(seed)
    (x0, y0), (x1, y1) = box; mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2 + 26, (y1 - y0) / 2 + 16; pts = []
    for i in range(int(360 * loops * 1.08) // 4):
        a = math.radians(i * 4 - 20); k = 1 + 0.04 * math.sin(a * 1.3)
        pts.append((mx + rx * k * math.cos(a) + rnd.uniform(-2, 2), my + ry * k * math.sin(a) + rnd.uniform(-2, 2)))
    d.line(pts, fill=color, width=w, joint="curve")

def arrow(d, p0, p1, color=RED, w=6, head=30):
    d.line([p0, p1], fill=color, width=w); ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    for da in (2.6, -2.6): d.line([p1, (p1[0] + head * math.cos(ang + da), p1[1] + head * math.sin(ang + da))], fill=color, width=w)

def icon(name, size, color=INK, brand=False):
    """Lucide (stroke) or brand (fill) SVG -> RGBA image tinted with color."""
    import cairosvg
    p = os.path.join(ICONS, "brands" if brand else "lucide", name + ".svg")
    svg = open(p, encoding="utf-8").read()
    hexc = "#%02x%02x%02x" % color[:3]
    svg = svg.replace("currentColor", hexc)
    if brand and "fill=" not in svg.split(">")[0]: svg = svg.replace("<svg", f'<svg fill="{hexc}"', 1)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")

def footer(d, source, dark=False, sig_color=None):
    fg = (200, 200, 200) if dark else (70, 70, 70)
    if dark: d.line((60, H - 82, W - 60, H - 82), fill=(255, 255, 255, 70), width=2)
    d.text((60, H - 64), source, font=I("SemiBold", 24), fill=fg)
    sf = I("Black", 26); sc = sig_color or (YEL if dark else BLK)
    d.text((W - 60 - d.textlength(SIGNATURE, font=sf), H - 65), SIGNATURE, font=sf, fill=sc)

def capture(url, clips, outdir=".", width=900, scale=2, wait_ms=4000):
    """clips = {"name": (x, y, w, h)} in CSS px of a full-page layout; also saves name_top.png of the viewport.
    Find coordinates with page.evaluate on the element (see find_boxes)."""
    from playwright.sync_api import sync_playwright
    proxy = {"server": os.environ["HTTPS_PROXY"]} if os.environ.get("HTTPS_PROXY") else None
    with sync_playwright() as p:
        b = p.chromium.launch(proxy=proxy, args=["--ignore-certificate-errors"])
        pg = b.new_page(viewport={"width": width, "height": 1200}, device_scale_factor=scale, ignore_https_errors=True)
        pg.goto(url, wait_until="domcontentloaded", timeout=60000); pg.wait_for_timeout(wait_ms)
        out = {}
        for name, (x, y, w, h) in clips.items():
            path = os.path.join(outdir, name + ".png")
            pg.screenshot(path=path, full_page=True, clip={"x": x, "y": y, "width": w, "height": h}); out[name] = path
        b.close(); return out

FIND_BOXES_JS = """(needle)=>[...document.querySelectorAll('p,li,pre,h1,h2,h3')].filter(e=>e.innerText.includes(needle))
 .map(e=>{const r=e.getBoundingClientRect();return [e.tagName,e.innerText.slice(0,80),r.x,r.y+scrollY,r.width,r.height]})"""

# ---------- T1 NEWS CARD ----------
def news_card(out, photo, headline, sub, tag="NEW RELEASE", date=None, inset=None, source="",
              photo_focus=(0.5, 0.3), head_size=116, head_y=690, inset_y=200, inset_w=640):
    """headline = [[(text, hl), ...], ...] max 3 lines, Anton caps. inset = PIL image (source headline screenshot)."""
    bg = cover(Image.open(photo).convert("RGB"), W, H, *photo_focus).convert("RGBA")
    g = Image.new("L", (1, H), 0)
    for y in range(H):
        t = max(0, (y - 380) / (H - 560)); g.putpixel((0, y), int(min(250, 255 * (min(1, t) ** 0.8))))
    grad = Image.new("RGBA", (W, H), (8, 8, 10, 255)); grad.putalpha(g.resize((W, H))); bg.alpha_composite(grad)
    d = ImageDraw.Draw(bg)
    tf = I("Black", 30); pw = d.textlength(tag, font=tf) + 44
    d.rounded_rectangle((56, 56, 56 + pw, 114), 10, fill=YEL); d.text((78, 68), tag, font=tf, fill=BLK)
    if date:
        df = I("Bold", 28); dw = d.textlength(date, font=df) + 44
        d.rounded_rectangle((56 + pw + 12, 56, 56 + pw + 12 + dw, 114), 10, fill=(12, 12, 12, 230))
        d.text((56 + pw + 34, 69), date, font=df, fill=WHITE)
    if inset is not None:
        card = screenshot_on_card(inset, inset_w, pad=14, rotate=-2.5); shadow_paste(bg, card, W - card.width - 40, inset_y)
        d = ImageDraw.Draw(bg)
    f = F(ANTON, head_size); lh = int(head_size * 1.19)
    for i, parts in enumerate(headline): rich_line(d, 60, head_y + i * lh, parts, f)
    y = head_y + lh * len(headline) + 34
    draw_wrapped(d, 60, y, sub, I("SemiBold", 33), 960, (235, 235, 235), 46)
    footer(d, source, dark=True); bg.convert("RGB").save(out, quality=95); return out

# ---------- T2 SCREENSHOT CARD ----------
def screenshot_card(out, shot, headline, pill, kicker="", highlights=(), note=None, fix_label="THE FIX",
                    fix_text=None, source="", bg_color=YEL, head_size=112, card_y=560, card_w=960, note_y=1010):
    """headline = list of plain strings (Anton caps). highlights in screenshot pixels."""
    bg = Image.new("RGBA", (W, H), bg_color + (255,)); d = ImageDraw.Draw(bg)
    pf = I("Black", 28); pw = d.textlength(pill, font=pf) + 44
    d.rounded_rectangle((60, 60, 60 + pw, 118), 10, fill=BLK); d.text((82, 72), pill, font=pf, fill=bg_color)
    if kicker: d.text((60 + pw + 18, 74), kicker, font=I("Bold", 28), fill=BLK)
    f = F(ANTON, head_size)
    for i, l in enumerate(headline): d.text((60, 150 + i * int(head_size * 1.14)), l, font=f, fill=BLK)
    img = highlight(Image.open(shot), highlights) if highlights else Image.open(shot)
    card = screenshot_on_card(img, card_w, rotate=1.2, rad=22); shadow_paste(bg, card, (W - card.width) // 2, card_y, alpha=110)
    d = ImageDraw.Draw(bg)
    if note: d.text((70, note_y), note, font=F(HAND, 52), fill=RED)
    if fix_text:
        d.rounded_rectangle((60, 1090, W - 60, 1210), 16, fill=BLK)
        d.text((92, 1104), fix_label, font=I("Black", 24), fill=YEL)
        d.text((92, 1140), fix_text, font=F(MONO, 40), fill=WHITE, **NOLIG)
    footer(d, source); bg.convert("RGB").save(out, quality=95); return out

# ---------- T3 PROOF CARD ----------
def proof_card(out, shot, title_lines, kicker, circles=(), notes=(), checklist_title=None, checklist=(),
               source="", crop=None, shot_w=1020, card_y=320):
    """circles = [(x0,y0,x1,y1)] in screenshot pixels (after crop offset is removed automatically).
    notes = [(text_multiline, (x, y_offset_below_card), target_circle_index, (ax, ay_offset))]"""
    bg = Image.new("RGBA", (W, H), (246, 246, 244, 255)); d = ImageDraw.Draw(bg)
    for i, t in enumerate(title_lines): d.text((60, 70 + i * 70), t, font=I("Black", 58), fill=BLK)
    d.text((60, 70 + len(title_lines) * 70 + 18), kicker, font=I("Medium", 30), fill=(70, 70, 70))
    img = Image.open(shot).convert("RGB"); ox, oy = 0, 0
    if crop: img = img.crop(crop); ox, oy = crop[0], crop[1]
    s = shot_w / img.width
    card = screenshot_on_card(img, shot_w, pad=10, top_pad=30); cx = (W - card.width) // 2
    shadow_paste(bg, card, cx, card_y, blur=16, off=(0, 8), alpha=60); d = ImageDraw.Draw(bg)
    P = lambda x, y: (cx + 10 + (x - ox) * s, card_y + 30 + (y - oy) * s)
    boxes = []
    for i, (x0, y0, x1, y1) in enumerate(circles):
        b = (P(x0, y0), P(x1, y1)); boxes.append(b); scribble(d, b, seed=4 + i)
    cb = card_y + card.height; hf = F(HAND, 58)
    for text, (nx, ny), ti, (ax, ay) in notes:
        b = boxes[ti]; arrow(d, (ax, cb + ay), ((b[0][0] + b[1][0]) / 2, b[1][1] + 26))
        d.multiline_text((nx, cb + ny), text, font=hf, fill=RED, spacing=0)
    if checklist:
        y0 = cb + 340; h = 110 + 72 * len(checklist)
        d.rounded_rectangle((60, y0, W - 60, y0 + h), 18, fill=(22, 22, 26))
        d.text((96, y0 + 36), checklist_title or "BEFORE YOU SHIP", font=I("Black", 28), fill=YEL)
        for i, t in enumerate(checklist):
            d.ellipse((96, y0 + 104 + i * 72, 128, y0 + 136 + i * 72), fill=YEL)
            d.text((112, y0 + 120 + i * 72), str(i + 1), font=I("Black", 22), fill=BLK, anchor="mm")
            d.text((150, y0 + 96 + i * 72), t, font=I("SemiBold", 36), fill=WHITE)
    footer(d, source); bg.convert("RGB").save(out, quality=95); return out

# ---------- T4 LIGHT CAROUSEL ----------
def _slide_frame(kicker, i, n, accent):
    im = Image.new("RGBA", (W, H), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.ellipse((W - 380, -220, W + 220, 380), fill=TINT.get(accent, (240, 240, 240)))   # soft corner blob
    d.text((64, 60), kicker, font=I("Black", 24), fill=accent)
    pg = f"{i}/{n}"; pf = I("Bold", 24); d.text((W - 64 - d.textlength(pg, font=pf), 60), pg, font=pf, fill=MUTE)
    d.rounded_rectangle((64, 1286, W - 64, 1294), 4, fill=(230, 226, 216))
    d.rounded_rectangle((64, 1286, 64 + int((W - 128) * i / n), 1294), 4, fill=accent)
    sf = I("Black", 24); d.text((W - 64 - d.textlength(SIGNATURE, font=sf), 1236), SIGNATURE, font=sf, fill=INK)
    return im, d

def _paste_icon(im, name, x, y, size, color, brand=False, tile=None):
    if tile:
        ImageDraw.Draw(im).rounded_rectangle((x, y, x + size + 36, y + size + 36), 22, fill=tile)
        x += 18; y += 18
    try: ic = icon(name, size, color, brand); im.alpha_composite(ic, (int(x), int(y)))
    except Exception as e: print("icon skipped:", name, e)

def light_carousel(spec, out_pdf):
    """spec = {"kicker": "...", "accent": BLUE, "slides": [
         {"type":"cover","title":"...","subtitle":"...","logos":["laravel"]},
         {"type":"card","n":1,"color":GREEN,"icon":"lock","title":"...","code":"...","bullets":["..."],"verdict":"..."},
         {"type":"table","title":"...","cols":["","A","B"],"rows":[["label","yes","no"],...]},
         {"type":"cta","title":"...","question":"..."}]}"""
    S = spec["slides"]; n = len(S); acc = spec.get("accent", BLUE); pages = []
    for i, s in enumerate(S, 1):
        col = s.get("color", acc); im, d = _slide_frame(spec.get("kicker", ""), i, n, col); t = s["type"]
        if t == "cover":
            x = 64
            for lg in s.get("logos", []): _paste_icon(im, lg, x, 190, 120, (255, 45, 32) if lg == "laravel" else INK, brand=True); x += 150
            d = ImageDraw.Draw(im)
            y = draw_wrapped(d, 64, 340, s["title"], I("Black", 92), 940, INK, 104)
            # underline accent under the title
            d.rounded_rectangle((64, y + 18, 300, y + 32), 7, fill=col)
            if s.get("subtitle"): draw_wrapped(d, 64, y + 70, s["subtitle"], I("Medium", 40), 920, MUTE, 54)
            d.rounded_rectangle((64, 1120, 300, 1190), 35, fill=INK); d.text((104, 1136), "Swipe  >", font=I("Bold", 30), fill=WHITE)
        elif t == "card":
            _paste_icon(im, s.get("icon", "layers"), 64, 150, 64, col, tile=TINT.get(col)); d = ImageDraw.Draw(im)
            if s.get("n"): d.text((200, 168), f"{s['n']:02d}", font=I("Black", 56), fill=col)
            y = draw_wrapped(d, 64, 300, s["title"], I("Black", 72), 950, INK, 84) + 34
            if s.get("code"):
                lines = s["code"].split("\n"); h = 56 + 56 * len(lines)
                d.rounded_rectangle((64, y, W - 64, y + h), 20, fill=(24, 26, 33))
                ms = 34
                while ms > 22 and max(d.textlength(l, font=F(MONO, ms), **NOLIG) for l in lines) > W - 128 - 64: ms -= 1
                for k, l in enumerate(lines): d.text((96, y + 30 + k * 56), l, font=F(MONO, ms), fill=(236, 236, 236), **NOLIG)
                y += h + 44
            for b in s.get("bullets", []):
                d.ellipse((70, y + 18, 88, y + 36), fill=col)
                y = draw_wrapped(d, 112, y, b, I("Medium", 40), 900, (40, 42, 50), 56) + 22
            if s.get("verdict"):
                y = y + 30
                d.rounded_rectangle((64, y, W - 64, y + 120), 20, fill=TINT.get(col, (240, 240, 240)))
                draw_wrapped(d, 96, y + 34, s["verdict"], I("Bold", 40), 880, INK, 50)
        elif t == "table":
            y = draw_wrapped(d, 64, 160, s["title"], I("Black", 64), 950, INK, 76) + 40
            cols = s["cols"]; cw = [330] + [(W - 128 - 330) // (len(cols) - 1)] * (len(cols) - 1)
            colors = s.get("col_colors", [INK, BLUE, GREEN, PURPLE])
            x = 64
            for k, c in enumerate(cols):
                if k: d.rounded_rectangle((x + 6, y, x + cw[k] - 6, y + 96), 16, fill=TINT.get(colors[k], (235, 235, 235)))
                d.multiline_text((x + 20, y + 14), c, font=I("Black", 26), fill=colors[k], spacing=6) if k else None
                x += cw[k]
            y += 112
            for r in s["rows"]:
                x = 64; d.line((64, y - 8, W - 64, y - 8), fill=(225, 220, 210), width=2)
                for k, c in enumerate(r):
                    if k == 0: draw_wrapped(d, x + 6, y + 6, c, I("SemiBold", 34), cw[0] - 20, INK, 42)
                    else:
                        ok = c.lower().startswith(("yes", "on")); bad = c.lower().startswith(("no", "off"))
                        _paste_icon(im, "circle-check" if ok else ("circle-x" if bad else "triangle-alert"), x + 20, y + 8, 44,
                                    GREEN if ok else (RED if bad else ORANGE)); d = ImageDraw.Draw(im)
                        draw_wrapped(d, x + 74, y + 8, c, I("Bold", 30), cw[k] - 80, (50, 52, 60), 36)
                    x += cw[k]
                y += s.get("row_h", 130)
            if s.get("note"): draw_wrapped(d, 64, y + 20, s["note"], I("SemiBold", 34), 950, MUTE, 46)
        elif t == "cta":
            y = draw_wrapped(d, 64, 380, s["title"], I("Black", 80), 950, INK, 94)
            if s.get("question"):
                d.rounded_rectangle((64, y + 60, W - 64, y + 260), 24, fill=TINT.get(col))
                draw_wrapped(d, 104, y + 100, s["question"], I("Bold", 40), 870, INK, 54)
            d.text((64, 1130), "Save it for your next code review.", font=I("SemiBold", 32), fill=MUTE)
        pages.append(im.convert("RGB"))
    pages[0].save(out_pdf, save_all=True, append_images=pages[1:], resolution=150)
    cov = out_pdf.rsplit(".", 1)[0] + "-cover.png"; pages[0].save(cov)
    for k, p in enumerate(pages, 1): p.save(out_pdf.rsplit(".", 1)[0] + f"-p{k}.png")
    return out_pdf

# ---------- CAROUSEL VARIANTS in the T1 / T2 design language ----------
# styled_carousel(spec, out_pdf, style="news" | "yellow" | "light")
#   news   = T1 language: dark pages, real-photo cover, Anton caps, yellow highlight boxes
#   yellow = T2 language: yellow pages, black Anton, white screenshot/code cards, red handwritten notes
#   light  = T4 language (light_carousel)
# Title highlight syntax: wrap words in [brackets] -> highlighted box, e.g. "LARAVEL [AI SDK 1.1]".
# Extra slide fields: "shot" (path to a real screenshot, optional "shot_crop" and "shot_marks"
#   [((x0,y0,x1,y1),color)]), "note" (red handwritten line), "photo" (cover only, plus "photo_focus").

def _tokens(text):
    toks = []; inside = False
    for raw in text.split():
        if "[" in raw: inside = True
        hl = inside
        if "]" in raw: inside = False
        toks.append((raw.replace("[", "").replace("]", ""), hl))
    return toks

def anton_title(d, x, y, text, size, maxw, fg, hl_bg, hl_fg, lh=1.24, pad=(12, 6), keep_case=False):
    """Wrap Anton caps title; [bracketed] words get a solid box. keep_case for code names. Returns bottom y."""
    f = F(ANTON, size); toks = _tokens(text if keep_case else text.upper()); lines = [[]]; cur = 0
    space = d.textlength(" ", font=f)
    for t, h in toks:
        w_ = d.textlength(t, font=f) + (pad[0] * 2 if h else 0)
        if lines[-1] and cur + space + w_ > maxw: lines.append([]); cur = 0
        cur += (space if lines[-1] else 0) + w_; lines[-1].append((t, h))
    for ln in lines:
        cx = x
        # merge adjacent highlighted tokens into one box
        groups = []
        for t, h in ln:
            if groups and groups[-1][1] == h: groups[-1][0] += " " + t
            else: groups.append([t, h])
        for t, h in groups:
            bb = d.textbbox((cx + (pad[0] if h else 0), y), t, font=f)
            if h:
                d.rectangle((bb[0] - pad[0], bb[1] - pad[1], bb[2] + pad[0], bb[3] + pad[1]), fill=hl_bg)
                d.text((cx + pad[0], y), t, font=f, fill=hl_fg); cx = bb[2] + pad[0] + space
            else:
                d.text((cx, y), t, font=f, fill=fg); cx = bb[2] + space
        y += int(size * lh)
    return y

STYLE = {
    "news":   dict(bg=(11, 11, 13), fg=WHITE, sub=(205, 205, 210), acc=YEL, acc_fg=BLK, code_bg=(26, 26, 31),
                   code_fg=(236, 236, 236), card_bg=(26, 26, 31), card_fg=WHITE, track=(40, 40, 46), note=YEL, pill_bg=YEL, pill_fg=BLK),
    "yellow": dict(bg=YEL, fg=BLK, sub=(40, 36, 20), acc=BLK, acc_fg=YEL, code_bg=BLK, code_fg=WHITE,
                   card_bg=WHITE, card_fg=BLK, track=(230, 190, 0), note=RED, pill_bg=BLK, pill_fg=YEL),
}

def _vframe(st, kicker, i, n):
    im = Image.new("RGBA", (W, H), st["bg"] + (255,)); d = ImageDraw.Draw(im)
    pf = I("Black", 24); pw = d.textlength(kicker, font=pf) + 36
    d.rounded_rectangle((60, 54, 60 + pw, 102), 10, fill=st["pill_bg"]); d.text((78, 64), kicker, font=pf, fill=st["pill_fg"])
    pg = f"{i}/{n}"; gf = I("Black", 26); d.text((W - 60 - d.textlength(pg, font=gf), 64), pg, font=gf, fill=st["fg"])
    d.rectangle((60, 1290, W - 60, 1298), fill=st["track"]); d.rectangle((60, 1290, 60 + int((W - 120) * i / n), 1298), fill=st["acc"])
    sf = I("Black", 24); d.text((W - 60 - d.textlength(SIGNATURE, font=sf), 1240), SIGNATURE, font=sf, fill=st["fg"])
    return im, d

def _code_block(d, y, code, st):
    lines = code.split("\n"); ms = 38
    while ms > 22 and max(d.textlength(l, font=F(MONO, ms), **NOLIG) for l in lines) > W - 120 - 72: ms -= 1
    lh = int(ms * 1.6); h = 56 + lh * len(lines)
    d.rounded_rectangle((60, y, W - 60, y + h), 18, fill=st["code_bg"])
    d.rectangle((60, y + 18, 68, y + h - 18), fill=YEL)
    for k, l in enumerate(lines): d.text((96, y + 28 + k * lh), l, font=F(MONO, ms), fill=st["code_fg"], **NOLIG)
    return y + h

def _shot_block(im, y, s, st, maxh=520):
    img = Image.open(s["shot"]).convert("RGB")
    if s.get("shot_crop"): img = img.crop(s["shot_crop"])
    if s.get("shot_marks"):
        marks = [((b[0] - (s.get("shot_crop") or (0, 0))[0], b[1] - (s.get("shot_crop") or (0, 0))[1],
                   b[2] - (s.get("shot_crop") or (0, 0))[0], b[3] - (s.get("shot_crop") or (0, 0))[1]), c) for b, c in s["shot_marks"]]
        img = highlight(img, marks)
    w_ = W - 156
    if img.height * w_ / img.width > maxh: w_ = int(img.width * maxh / img.height)
    card = screenshot_on_card(img, w_, pad=18, rad=18, rotate=s.get("shot_rotate", 0))
    shadow_paste(im, card, (W - card.width) // 2, y, blur=18, off=(0, 10), alpha=120 if st is STYLE["news"] else 90)
    return y + card.height

def styled_carousel(spec, out_pdf, style="news"):
    if style == "light": return light_carousel(spec, out_pdf)
    st = STYLE[style]; S = spec["slides"]; n = len(S); pages = []
    for i, s in enumerate(S, 1):
        t = s["type"]
        if t == "cover" and style == "news" and s.get("photo"):
            im = cover(Image.open(s["photo"]).convert("RGB"), W, H, *s.get("photo_focus", (0.5, 0.3))).convert("RGBA")
            g = Image.new("L", (1, H), 0)
            for yy in range(H):
                tt = max(0, (yy - 300) / (H - 520)); g.putpixel((0, yy), int(min(250, 255 * (min(1, tt) ** 0.8))))
            gr = Image.new("RGBA", (W, H), st["bg"] + (255,)); gr.putalpha(g.resize((W, H))); im.alpha_composite(gr)
            d = ImageDraw.Draw(im)
            pf = I("Black", 26); kk = spec.get("kicker", ""); pw = d.textlength(kk, font=pf) + 40
            d.rounded_rectangle((60, 56, 60 + pw, 108), 10, fill=YEL); d.text((80, 67), kk, font=pf, fill=BLK)
            if s.get("inset") is not None:
                c_ = screenshot_on_card(s["inset"], 620, pad=14, rotate=-2.5); shadow_paste(im, c_, W - c_.width - 40, 170); d = ImageDraw.Draw(im)
            y = anton_title(d, 60, s.get("title_y", 640), s["title"], s.get("size", 118), W - 120, WHITE, YEL, BLK)
            if s.get("subtitle"): y = draw_wrapped(d, 60, y + 40, s["subtitle"], I("SemiBold", 38), 960, (235, 235, 235), 52)
            d.rounded_rectangle((60, 1150, 290, 1214), 32, fill=YEL); d.text((96, 1163), "SWIPE  >", font=I("Black", 30), fill=BLK)
            d.rectangle((60, 1290, W - 60, 1298), fill=(40, 40, 46)); d.rectangle((60, 1290, 60 + (W - 120) // n, 1298), fill=YEL)
            sf = I("Black", 24); d.text((W - 60 - d.textlength(SIGNATURE, font=sf), 1240), SIGNATURE, font=sf, fill=YEL)
            pages.append(im.convert("RGB")); continue
        im, d = _vframe(st, spec.get("kicker", ""), i, n)
        if t == "cover":
            y = anton_title(d, 60, 170, s["title"], s.get("size", 128), W - 120, st["fg"], st["acc"], st["acc_fg"])
            if s.get("subtitle"): y = draw_wrapped(d, 60, y + 40, s["subtitle"], I("SemiBold", 38), 960, st["sub"], 50)
            if s.get("shot"): y = _shot_block(im, y + 40, s, st, maxh=s.get("shot_maxh", 420)); d = ImageDraw.Draw(im)
            if s.get("note"): d.text((70, y + 26), s["note"], font=F(HAND, 54), fill=st["note"])
            d.rounded_rectangle((60, 1150, 290, 1214), 32, fill=st["acc"]); d.text((96, 1163), "SWIPE  >", font=I("Black", 30), fill=st["acc_fg"])
        elif t == "card":
            y = 150
            if s.get("n"):
                d.text((60, y), f"{s['n']:02d}", font=F(ANTON, 96), fill=st["acc"] if style == "news" else BLK); y += 118
            y = anton_title(d, 60, y, s["title"], s.get("size", 100), W - 120, st["fg"], st["acc"], st["acc_fg"], keep_case=s.get("keep_case", False)) + 24
            if s.get("code"): y = _code_block(d, y, s["code"], st) + 36
            if s.get("shot"): y = _shot_block(im, y, s, st, maxh=s.get("shot_maxh", 520)) + 30; d = ImageDraw.Draw(im)
            for b in s.get("bullets", []):
                d.rectangle((62, y + 19, 82, y + 39), fill=st["acc"])
                y = draw_wrapped(d, 108, y, b, I("SemiBold", 44), 900, st["fg"], 60) + 24
            if s.get("note"): d.text((66, y + 4), s["note"], font=F(HAND, 60), fill=st["note"]); y += 86
            if s.get("verdict"):
                y += 16; lines = wrap(d, s["verdict"], I("Black", 42), 880); h = 60 + 54 * len(lines)
                d.rounded_rectangle((60, y, W - 60, y + h), 16, fill=st["acc"] if style == "news" else BLK)
                for k, l in enumerate(lines): d.text((96, y + 28 + k * 54), l, font=I("Black", 42), fill=BLK if style == "news" else YEL)
        elif t == "table":
            y = anton_title(d, 60, 150, s["title"], s.get("size", 90), W - 120, st["fg"], st["acc"], st["acc_fg"]) + 30
            cols = s["cols"]; cw = [330] + [(W - 120 - 330) // (len(cols) - 1)] * (len(cols) - 1)
            x = 60
            for k, c in enumerate(cols):
                if k:
                    d.rectangle((x + 6, y, x + cw[k] - 6, y + 96), fill=st["acc"])
                    d.multiline_text((x + 20, y + 14), c, font=I("Black", 26), fill=st["acc_fg"], spacing=6)
                x += cw[k]
            y += 116
            for r in s["rows"]:
                if style == "yellow": d.rectangle((60, y - 10, W - 60, y + s.get("row_h", 130) - 22), fill=WHITE)
                else: d.line((60, y - 10, W - 60, y - 10), fill=(50, 50, 58), width=2)
                x = 60
                for k, c in enumerate(r):
                    if k == 0: draw_wrapped(d, x + 18, y + 6, c, I("Bold", 32), cw[0] - 30, st["card_fg"] if style == "yellow" else WHITE, 40)
                    else:
                        ok = c.lower().startswith(("yes", "on")); bad = c.lower().startswith(("no", "off"))
                        _paste_icon(im, "circle-check" if ok else ("circle-x" if bad else "triangle-alert"), x + 20, y + 8, 44,
                                    GREEN if ok else (RED if bad else ORANGE)); d = ImageDraw.Draw(im)
                        d.text((x + 74, y + 10), c, font=I("Black", 30), fill=BLK if style == "yellow" else WHITE)
                    x += cw[k]
                y += s.get("row_h", 130)
            if s.get("note"): d.text((66, y + 10), s["note"], font=F(HAND, 54), fill=st["note"])
        elif t == "cta":
            y = anton_title(d, 60, 300, s["title"], s.get("size", 110), W - 120, st["fg"], st["acc"], st["acc_fg"])
            if s.get("question"):
                lines = wrap(d, s["question"], I("Bold", 42), 860); h = 80 + 56 * len(lines)
                d.rounded_rectangle((60, y + 60, W - 60, y + 60 + h), 18, fill=st["card_bg"])
                for k, l in enumerate(lines): d.text((100, y + 100 + k * 56), l, font=I("Bold", 42), fill=st["card_fg"])
            d.text((60, 1150), s.get("footer_line", "Save it for your next code review."), font=I("SemiBold", 32), fill=st["sub"])
        pages.append(im.convert("RGB"))
    pages[0].save(out_pdf, save_all=True, append_images=pages[1:], resolution=150)
    base = out_pdf.rsplit(".", 1)[0]; pages[0].save(base + "-cover.png")
    for k, p in enumerate(pages, 1): p.save(base + f"-p{k}.png")
    return out_pdf
