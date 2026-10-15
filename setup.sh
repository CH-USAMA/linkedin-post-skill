#!/usr/bin/env bash
# Install Python deps, fetch the OFL fonts, and fetch Lucide icons (ISC licence) into the skill's assets folder.
set -e
cd "$(dirname "$0")/skill/daily-linkedin-post"
pip install pillow cairosvg numpy imageio imageio-ffmpeg --break-system-packages 2>/dev/null || pip install pillow cairosvg numpy imageio imageio-ffmpeg
python3 tools/fetch_fonts.py
mkdir -p assets/icons/lucide assets/icons/brands
tmp=$(mktemp -d); (cd "$tmp" && npm pack lucide-static >/dev/null && tar xzf lucide-static-*.tgz)
cp "$tmp"/package/icons/*.svg assets/icons/lucide/ && cp "$tmp"/package/LICENSE assets/icons/lucide/LICENSE
echo "Fonts and icons ready. Optional: pip install playwright && playwright install chromium (for capture() screenshots)."
echo "Brand logos (optional): download SVGs from simple-icons into assets/icons/brands/ (check each brand's trademark rules)."
