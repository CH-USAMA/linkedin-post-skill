# Usage guide

## 1. Install
Requirements: Python 3.9+, `pip`, `npm` (only to fetch icons), fonts `Liberation Sans` and `DejaVu Sans Mono` (present on most Linux; on macOS/Windows edit the font paths at the top of `style.py`).

```bash
bash setup.sh
```
This installs `pillow cairosvg numpy imageio imageio-ffmpeg` and copies the Lucide SVG icons to `skill/daily-linkedin-post/assets/icons/lucide/`. Brand logos are optional: put SVGs in `assets/icons/brands/` (check each brand's trademark rules) and use `brand_slug="laravel"` in `pill()` or `icon_tile()`.

Environment variables: `LI_NAME` and `LI_HANDLE` set the signature on every image; `LI_ICONS` points to a different icon folder.

## 2. Set up your state folder
Keep this outside the skill folder, in a place that is writable and private (do not commit it):

```
state/
  voice.md        # your tone, words you never use, 3 to 5 sample posts
  history.jsonl   # one JSON line per draft/post: date, pillar, lane, topic, status, files
  ideas.json      # backlog of topics
  config.json     # copy of config.example.json; keep "autopublish": false
```
Every topic in `history.jsonl` is treated as used (any status). That is what stops repeats.

## 3. Install the skill in your agent
Copy `skill/daily-linkedin-post/` into your agent's skills directory (for Claude: a skill folder containing `SKILL.md`). Edit the **Lanes** and **Pillars** in `SKILL.md` to match you.

## 4. First run
Ask the agent: "Run the daily LinkedIn post skill." It should: read state, pick the lane for today, research, design the asset, write the caption, run the linter, save files, log a draft, and give you a ready-to-post block.

## 5. Build assets yourself
**Single image** (see `example-post.py`): `NeonCanvas()`, then `pill`, `text`, `gradient_text`, `card`, `icon_tile`, `signature`, `save`. Canvas is 1080x1350.

**Carousel**: write `slides.json` and run `python3 tools/carousel.py slides.json out.pdf`.

| Slide type | Fields |
|---|---|
| `cover` | `title`, `subtitle`, `icon` |
| `point` | `n`, `title`, `lines[]`, `code[]`, `icon`, `color` |
| `compare` | `title`, `left{h,items[]}`, `right{h,items[]}` |
| `cta` | `title`, `question` |

Colours: `cyan violet pink coral lime emerald amber blue`. Meaning: coral = mistake, emerald = fix, amber = insight. Icons are Lucide names such as `database`, `timer`, `shield-check`.

**Video**: render frames with `NeonCanvas`, reveal elements over time, and write 12 to 15 seconds at 30 fps with `imageio` (`libx264`, `yuv420p`). Upload as a native video, not a GIF.

## 5b. Visual Rotation templates (`tools/templates.py`)
```python
import sys; sys.path.insert(0, "skill/daily-linkedin-post/tools"); from templates import *
news_card("t1.png", "photo.jpg", headline=[[("LARAVEL ", False), ("13.35", True)], [("SHIPPED", False)]], sub="...", source="Source: ...")
screenshot_card("t2.png", "shot.png", headline=["LINE ONE", "LINE TWO"], pill="TOPIC", highlights=[((x0,y0,x1,y1), (255,236,120))], note="...", fix_text="...")
proof_card("t3.png", "shot.png", title_lines=["...", "..."], kicker="...", circles=[(x0,y0,x1,y1)], notes=[("label", (100,118), 0, (250,110))], checklist=["..."])
light_carousel(spec, "t4.pdf")                       # cream style
styled_carousel(spec, "news.pdf", style="news")      # T1 look
styled_carousel(spec, "yellow.pdf", style="yellow")  # T2 look
capture("https://example.com/page", {"part": (x, y, w, h)}, outdir=".")  # real screenshot via Playwright
```
Carousel `spec`: `{"kicker": "...", "slides": [...]}` with slide types `cover` (title, subtitle, photo, inset, shot, note),
`card` (n, title, code, shot, bullets, note, verdict, keep_case), `table` (title, cols, rows, note), `cta` (title, question).
Wrap words in `[brackets]` to highlight them in news/yellow titles. Every call is shown in `templates-demo.py`.
Fonts: run `python3 skill/daily-linkedin-post/tools/fetch_fonts.py` (setup.sh does it).

## 6. Caption rules
Line 1 is a bold, specific claim (140 characters or fewer). Short lines, 3 to 5 bullets, 120 to 220 words. Finish with a question that divides experienced people. No links in the caption: put them in a `First comment:` line. 3 to 5 hashtags at the end. No em dashes.

## 7. Lint
```bash
python3 skill/daily-linkedin-post/tools/slop_lint.py caption.txt
```
Exit code 0 means clean. It checks AI-sounding words, structural tells ("not just X, it's Y", one-word rhetorical lines), em/en dashes and double hyphens, links before the `First comment:` marker, hashtag count, line-1 length and word count. Edit the lists at the top of the script to fit your voice.

## 8. Post
Open LinkedIn, upload the file, paste the caption, publish, then paste the first comment. See [WORKFLOW.md](WORKFLOW.md).
