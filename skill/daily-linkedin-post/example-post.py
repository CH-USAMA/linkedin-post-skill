"""Minimal example: one 1080x1350 'Neon Terminal' post image. Run: LI_NAME="Jane Doe" python3 example-post.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools"))
from style import *
c = NeonCanvas()
c.pill(64, 64, "EXAMPLE  ·  3 THINGS", CYAN, icon_name="circle-check")
c.text(64, 132, "A headline that", SANS_B, 60)
c.gradient_text(64, 204, "states one idea.", 64, (CYAN, VIOLET, PINK))
y = 330
for ic, a, b, col in [("database","Row one","short supporting line",VIOLET),("zap","Row two","short supporting line",CYAN),("shield-check","Row three","short supporting line",EMERALD)]:
    c.card(64, y, 952, 150, accent=col); c.icon_tile(96, y+43, ic, col, size=64)
    c.text(184, y+34, a, SANS_B, 36); c.text(184, y+88, b, MONO, 25, fill=DIM); y += 172
c.signature(); c.save("example-post.png")
