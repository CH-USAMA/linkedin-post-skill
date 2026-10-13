"""
"Neon Terminal" visual style for LinkedIn images, videos and carousels.

- Palette: deep navy base, violet/cyan aurora glows, vivid accent set.
- Icons: Lucide (ISC, 2k programming/UI icons) + Simple Icons brand logos (CC0 data;
  logos are trademarks of their owners, used only to name the technology).
- Helpers: canvas with aurora background, gradient headline text, glass cards,
  icon tiles, pills, signature.

Usage:
    import sys; sys.path.insert(0, "path/to/tools")
    from style import *
    c = NeonCanvas()
    c.pill(64, 70, "POSTGRESQL 19", CYAN, brand="postgresql")
    c.gradient_text(64, 130, "Headline", 64, (CYAN, VIOLET))
    c.card(64, 300, 952, 200, accent=CORAL)
    c.icon_tile(96, 330, "split", CORAL)
    c.signature(); c.save("out.png")
"""
import os, io, json, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cairosvg

HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.environ.get("LI_ICONS", os.path.join(HERE, "..", "assets", "icons"))  # run setup.sh to fetch Lucide icons

# ---------- palette ----------
BG      = (8, 11, 24)
INK     = (241, 245, 255)   # primary text
SUB     = (160, 170, 196)   # secondary text
DIM     = (104, 114, 140)
CYAN    = (34, 211, 238)
VIOLET  = (167, 139, 250)
PINK    = (244, 114, 182)
CORAL   = (251, 113, 133)
LIME    = (163, 230, 53)
EMERALD = (52, 211, 153)
AMBER   = (251, 191, 36)
BLUE    = (96, 165, 250)
ACCENTS = dict(cyan=CYAN, violet=VIOLET, pink=PINK, coral=CORAL, lime=LIME,
               emerald=EMERALD, amber=AMBER, blue=BLUE)

def _font(bold=False, mono=False):
    if mono:
        return ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold
                else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    return ("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
SANS_B, SANS_R, MONO, MONO_B = _font(True), _font(), _font(mono=True), _font(True, True)
def F(p, s): return ImageFont.truetype(p, s)

def _mix(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def _dark(c, t=0.82): return _mix(c, BG, t)

# ---------- icons ----------
_cache = {}
_brand_hex = None
def icon(name, size=48, color=INK, stroke=2.0):
    """Lucide icon as RGBA image. name e.g. 'database', 'split', 'shield-check'."""
    key = ("l", name, size, color, stroke)
    if key in _cache: return _cache[key]
    svg = open(os.path.join(ICONS, "lucide", f"{name}.svg")).read()
    hexc = "#%02x%02x%02x" % color
    svg = svg.replace("currentColor", hexc)
    svg = re.sub(r'stroke-width="[\d.]+"', f'stroke-width="{stroke}"', svg)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    im = Image.open(io.BytesIO(png)).convert("RGBA"); _cache[key] = im; return im

def brand(slug, size=48, color=None):
    """Simple Icons logo. color=None uses the brand's official color."""
    global _brand_hex
    if _brand_hex is None:
        d = json.load(open(os.path.join(ICONS, "brands", "simple-icons.json")))
        d = d if isinstance(d, list) else d.get("icons", [])
        _brand_hex = {}
        for i in d:
            s = i.get("slug") or re.sub(r"[^a-z0-9]", "", i["title"].lower().replace(".", "dot"))
            _brand_hex[s] = i["hex"]
    hexc = "#" + (("%02x%02x%02x" % color) if color else _brand_hex.get(slug, "FFFFFF"))
    svg = open(os.path.join(ICONS, "brands", f"{slug}.svg")).read()
    svg = svg.replace("<svg ", f'<svg fill="{hexc}" ', 1)
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(png)).convert("RGBA")

# ---------- canvas ----------
_BG_CACHE = {}
def _local_blur(img, box_draw, bbox, radius):
    """Draw on a transparent patch, blur only that patch, composite. Much faster than full-canvas blur."""
    x0, y0, x1, y1 = [int(v) for v in bbox]; pad = radius * 3
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad); x1, y1 = min(img.width, x1 + pad), min(img.height, y1 + pad)
    patch = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    box_draw(ImageDraw.Draw(patch), -x0, -y0)
    patch = patch.filter(ImageFilter.GaussianBlur(radius))
    region = img.crop((x0, y0, x1, y1)); img.paste(Image.alpha_composite(region, patch), (x0, y0))

class NeonCanvas:
    def __init__(self, w=1080, h=1350, glows=((VIOLET, (-0.25, -0.2), 0.75), (CYAN, (1.05, 0.95), 0.6))):
        self.w, self.h = w, h
        key = (w, h, glows)
        if key in _BG_CACHE:
            self.img = _BG_CACHE[key].copy(); self.d = ImageDraw.Draw(self.img); return
        self.img = Image.new("RGBA", (w, h), BG + (255,))
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        for col, (cx, cy), r in glows:
            R = int(w * r); X, Y = int(w * cx), int(h * cy)
            gd.ellipse([X - R, Y - R, X + R, Y + R], fill=_mix(col, BG, 0.78) + (255,))
        self.img = Image.alpha_composite(self.img, g.filter(ImageFilter.GaussianBlur(170)))
        # subtle dot grid
        grid = Image.new("RGBA", (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(grid)
        for y in range(24, h, 36):
            for x in range(24, w, 36):
                gd.point((x, y), fill=(255, 255, 255, 18))
        self.img = Image.alpha_composite(self.img, grid)
        _BG_CACHE[key] = self.img.copy()
        self.d = ImageDraw.Draw(self.img)

    def _refresh(self): self.d = ImageDraw.Draw(self.img)

    def text(self, x, y, s, font, size, fill=INK):
        self.d.text((x, y), s, font=F(font, size), fill=fill)
    def tw(self, s, font, size): return self.d.textlength(s, font=F(font, size))

    def gradient_text(self, x, y, s, size, cols=(CYAN, VIOLET), font=SANS_B):
        f = F(font, size); bb = self.d.textbbox((0, 0), s, font=f)
        w, h = bb[2] + 4, bb[3] + 8
        mask = Image.new("L", (w, h), 0); ImageDraw.Draw(mask).text((0, 0), s, font=f, fill=255)
        grad = Image.new("RGB", (w, 1))
        for i in range(w):
            t = i / max(w - 1, 1)
            grad.putpixel((i, 0), _mix(cols[0], cols[-1], t) if len(cols) == 2 else
                          (_mix(cols[0], cols[1], t * 2) if t < .5 else _mix(cols[1], cols[2], t * 2 - 1)))
        grad = grad.resize((w, h)); self.img.paste(grad, (x, y), mask); self._refresh()
        return w

    def card(self, x, y, w, h, accent=CYAN, r=26, fill_t=0.9):
        _local_blur(self.img, lambda d, ox, oy: d.rounded_rectangle(
            [x + ox, y + 14 + oy, x + w + ox, y + h + 14 + oy], r, fill=(0, 0, 0, 120)), (x, y + 14, x + w, y + h + 14), 20)
        self._refresh()
        self.d.rounded_rectangle([x, y, x + w, y + h], r, fill=_mix(accent, (14, 18, 34), fill_t),
                                 outline=_mix(accent, BG, 0.45), width=2)
        self.d.rounded_rectangle([x + 28, y - 2, x + 148, y + 3], 2, fill=accent)  # short accent tab

    def icon_tile(self, x, y, name, color, size=64, brand_slug=None, icon_color=None):
        _local_blur(self.img, lambda d, ox, oy: d.rounded_rectangle(
            [x - 4 + ox, y - 4 + oy, x + size + 4 + ox, y + size + 4 + oy], 18, fill=color + (70,)),
            (x - 4, y - 4, x + size + 4, y + size + 4), 10)
        self._refresh()
        self.d.rounded_rectangle([x, y, x + size, y + size], 16, fill=_dark(color, 0.72),
                                 outline=_mix(color, BG, 0.3), width=2)
        s = int(size * 0.56)
        ic = brand(brand_slug, s, icon_color) if brand_slug else icon(name, s, icon_color or color, 2.2)
        self.img.alpha_composite(ic, (x + (size - s) // 2, y + (size - s) // 2)); self._refresh()

    def pill(self, x, y, text, color, icon_name=None, brand_slug=None, size=22):
        f = F(MONO_B, size); tw = self.d.textlength(text, font=f)
        pad = 18; isz = size + 8 if (icon_name or brand_slug) else 0
        w = int(tw + pad * 2 + (isz + 10 if isz else 0)); h = size + 22
        self.d.rounded_rectangle([x, y, x + w, y + h], h // 2, fill=_dark(color, 0.8),
                                 outline=_mix(color, BG, 0.4), width=2)
        tx = x + pad
        if isz:
            ic = brand(brand_slug, isz, color) if brand_slug else icon(icon_name, isz, color)
            self.img.alpha_composite(ic, (tx, y + (h - isz) // 2)); self._refresh(); tx += isz + 10
        self.d.text((tx, y + 10), text, font=f, fill=color); return w

    def strike(self, x, y, w, color=CORAL, width=4):
        self.d.line([x, y, x + w, y], fill=color, width=width)

    def signature(self, name=os.environ.get("LI_NAME","Your Name"), handle=os.environ.get("LI_HANDLE","Your headline")):
        x, y = self.w - 64, self.h - 58
        f = F(SANS_B, 26); nw = self.d.textlength(name, font=f)
        self.icon_tile(int(x - nw - 58), y - 6, "code-xml", CYAN, size=44)
        self.d.text((x - nw, y), name, font=f, fill=SUB)

    def save(self, path): self.img.convert("RGB").save(path, quality=95)
