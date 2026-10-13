#!/usr/bin/env bash
# Fetch Lucide icons (ISC licence) into the skill's assets folder and install Python deps.
set -e
cd "$(dirname "$0")/skill/daily-linkedin-post"
pip install pillow cairosvg numpy imageio imageio-ffmpeg --break-system-packages 2>/dev/null || pip install pillow cairosvg numpy imageio imageio-ffmpeg
mkdir -p assets/icons/lucide assets/icons/brands
tmp=$(mktemp -d); (cd "$tmp" && npm pack lucide-static >/dev/null && tar xzf lucide-static-*.tgz)
cp "$tmp"/package/icons/*.svg assets/icons/lucide/ && cp "$tmp"/package/LICENSE assets/icons/lucide/LICENSE
echo "Icons ready. Brand logos (optional): download SVGs from simple-icons into assets/icons/brands/ (check each brand's trademark rules)."
