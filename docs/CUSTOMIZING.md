# Customizing

- **Lanes and pillars**: edit the `Lanes` section of `SKILL.md`. Keep 4 to 5 pillars so your profile stays coherent.
- **Voice**: fill `voice.md` with 3 to 5 of your own posts, words you never use, and your usual opening and closing style. The agent should read it before every draft.
- **Linter**: add your own banned words or patterns to the `WORDS` and `TELLS` lists in `tools/slop_lint.py`.
- **Hooks**: add or remove patterns in `hook-formulas.md`; keep the failure mode next to each.
- **Colours**: edit the palette constants at the top of `tools/style.py`. Accents should keep a meaning (bad, good, insight).
- **Fonts**: change the paths in `_font()` in `style.py` for your OS.
- **Signature**: `LI_NAME` and `LI_HANDLE` environment variables, or edit `signature()`.
- **New slide type**: add a branch in `tools/carousel.py` (`elif t == "yourtype":`) and document its fields in `USAGE.md`.
- **Other platforms**: change the canvas size (`NeonCanvas(w, h)`) and re-check text sizes for that feed.
