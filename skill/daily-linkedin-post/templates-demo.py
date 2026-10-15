"""Render every Visual Rotation template with generic demo content (no third-party images needed).
Run:  LI_NAME="Your Name" python3 templates-demo.py [outdir] [--photo path/to/your/photo.jpg]
For real posts, replace the generated "screenshots" with real ones (tools/templates.py capture())
and the generated background with a real, lawfully licensed photo."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "tools"))
from templates import *
from PIL import Image, ImageDraw, ImageFilter
args = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = args[0] if args else os.path.join(HERE, "demo-out"); os.makedirs(OUT, exist_ok=True)
PHOTO = sys.argv[sys.argv.index("--photo") + 1] if "--photo" in sys.argv else None
O = lambda f: os.path.join(OUT, f)

def fake_photo(path):
    """Placeholder background when no real photo is given: dark gradient with soft light blobs."""
    im = Image.new("RGB", (1600, 1100), (18, 22, 34)); d = ImageDraw.Draw(im)
    for i, (x, y, r, c) in enumerate([(300, 300, 260, (40, 90, 160)), (1200, 250, 300, (110, 50, 140)),
                                     (900, 800, 340, (30, 120, 120)), (200, 900, 200, (150, 110, 30))]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)
    im.filter(ImageFilter.GaussianBlur(120)).save(path); return path

def fake_screenshot(path, lines, width=1700, mono_from=0, size=34):
    """A docs-style screenshot rendered from your own text (stand-in for a real capture)."""
    lh = int(size * 1.9); h = 60 + lh * len(lines)
    im = Image.new("RGB", (width, h), (255, 255, 255)); d = ImageDraw.Draw(im)
    for k, l in enumerate(lines):
        mono = k >= mono_from
        if mono and k == mono_from: d.rectangle((20, 30 + lh * k - 20, width - 20, h - 10), fill=(244, 245, 248))
        d.text((50, 30 + lh * k), l, font=F(MONO, size - 2) if mono else I("Regular", size),
               fill=(60, 64, 80) if mono else (40, 44, 52), **(NOLIG if mono else {}))
    im.save(path); return path, lh

photo = PHOTO or fake_photo(O("_bg.jpg"))
code_png, lh = fake_screenshot(O("_code.png"), [
    "A retry loop around a payment call looks harmless:",
    "// retries on timeout",
    "Http::retry(3, 200)->post('/charges', $payload);",
    "",
    "// safe: the server dedupes repeats",
    "Http::withHeaders(['Idempotency-Key' => $key])",
    "    ->retry(3, 200)->post('/charges', $payload);"], mono_from=1)
log_png, llh = fake_screenshot(O("_log.png"), [
    "12:00:01  POST /charges  amount=4900  status=timeout",
    "12:00:01  POST /charges  amount=4900  status=201",
    "12:00:02  POST /charges  amount=4900  status=201"], mono_from=0, size=36)

# T1 news card
news_card(O("T1-news-card.png"), photo,
    headline=[[("RETRIES ", False), ("CHARGED", True)], [("THE SAME CARD", False)], [("TWICE", True)]],
    sub="Retries are only safe when the server can tell a repeat from a new request.",
    tag="EXAMPLE", date="Demo", source="Source: your source  ·  Photo: your licensed photo")

# T2 screenshot card
screenshot_card(O("T2-screenshot-card.png"), code_png,
    headline=["THIS RETRY CAN", "CHARGE A CARD", "TWICE."], pill="PAYMENTS", kicker="Retries and idempotency",
    highlights=[((30, 30 + lh * 1 - 10, 1300, 30 + lh * 3 - 15), (255, 236, 120)),
                ((30, 30 + lh * 4 - 10, 1500, 30 + lh * 7 - 15), (190, 240, 190))],
    note="timeout != failed", fix_text="Idempotency-Key: <uuid>", source="Source: your docs link")

# T3 proof card
proof_card(O("T3-proof-card.png"), log_png, title_lines=["One timeout.", "Two successful charges."],
    kicker="A log excerpt like the one you should screenshot from your own app:",
    circles=[(40, 30 + llh * 1, 1250, 30 + llh * 1 + 40), (40, 30 + llh * 2, 1250, 30 + llh * 2 + 40)],
    notes=[("the client gave up\nthe server did not", (100, 118), 0, (250, 110)),
           ("the retry\ncharged again", (600, 118), 1, (640, 110))],
    checklist_title="BEFORE YOU RETRY", checklist=["Send an idempotency key", "Store it with the result", "Retry only on safe errors"],
    source="Source: your own logs")

# Carousels in three styles
base = [
    {"type": "cover", "title": "Retries without [idempotency] keys", "subtitle": "Why a timeout can still charge a card, and the fix."},
    {"type": "card", "n": 1, "title": "A timeout is not a [failure]", "icon": "timer", "color": ORANGE,
     "bullets": ["The request may have reached the server.", "The client only knows it stopped waiting."],
     "verdict": "Treat timeouts as unknown, not failed."},
    {"type": "card", "n": 2, "title": "Send an [Idempotency-Key]", "icon": "lock", "color": GREEN, "keep_case": True,
     "code": "Http::withHeaders(['Idempotency-Key' => $key])\n    ->retry(3, 200)->post('/charges', $payload);",
     "bullets": ["Same key, same result. The server returns the first response."], "verdict": "Retries become safe."},
    {"type": "table", "title": "When is a retry [safe]?", "cols": ["", "GET", "POST\nno key", "POST\nwith key"],
     "rows": [["Can repeat safely", "Yes", "No", "Yes"], ["Needs server support", "No", "No", "Yes"]]},
    {"type": "cta", "title": "Which calls in your app retry [blindly]?", "question": "Do you add idempotency keys by default, or only for payments?"},
]
light = [dict(s, title=s["title"].replace("[", "").replace("]", "")) for s in base]
light[0]["logos"] = []
light_carousel({"kicker": "RETRIES", "accent": BLUE, "slides": light}, O("T4-light-carousel.pdf"))
news = [dict(base[0], photo=photo)] + base[1:]
styled_carousel({"kicker": "RETRIES", "slides": news}, O("T1-news-carousel.pdf"), style="news")
yellow = [dict(base[0], shot=log_png, note="one timeout, two charges")] + base[1:]
styled_carousel({"kicker": "RETRIES", "slides": yellow}, O("T2-yellow-carousel.pdf"), style="yellow")
for f in os.listdir(OUT):
    if f.startswith("_"): pass
print("rendered to", OUT)
