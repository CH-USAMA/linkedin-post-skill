#!/usr/bin/env python3
"""Slop lint for LinkedIn captions. Usage: python3 slop_lint.py caption.txt
Exit 0 = clean, 1 = findings. Inspired by the MIT-licensed linkedin-agent-skill idea, written fresh for this account."""
import re, sys
WORDS = ["delve","leverage","utilize","harness","embark","foster","facilitate","showcase","unlock","elevate",
 "streamline","spearhead","cultivate","amplify","revolutionize","robust","seamless","pivotal","comprehensive",
 "game-changing","game changer","groundbreaking","multifaceted","tapestry","landscape","moreover","furthermore",
 "in today's fast-paced","cutting-edge","paradigm","synergy","holistic","supercharge","dive into","deep dive"]
TELLS = [
 (r"\bnot just\b.{0,60}\bit'?s\b", "'not just X, it's Y' pattern"),
 (r"\bnot only\b.{0,80}\bbut also\b", "'not only X but also Y'"),
 (r"\bisn'?t about\b.{0,60}\bit'?s about\b", "'isn't about X, it's about Y'"),
 (r"(?m)^\s*(the result|the catch|the truth|the lesson)\?\s*$", "one-word rhetorical question line"),
 (r"here'?s what i learned", "'Here's what I learned' announcement"),
 (r"[\U0001F680\U0001F525\U0001F4A1✨\U0001F3AF]", "rocket/fire/bulb/sparkle/dart emoji"),
 (r"as an ai\b|as a language model", "model self-reference"),
 (r"(?mi)^\s*(in summary|to summarize|in conclusion)", "essay-closer opener"),
 (r"(?i)(thoughts\?|am i wrong\?|agree\?)\s*$", "reflex engagement bait"),
 (r"—|–|--", "em/en dash or double hyphen (hard rule)"),
 (r"https?://", "link in caption (use First comment: line; allowed only after that marker)"),
]
t = open(sys.argv[1], encoding="utf-8").read()
body = t.split("First comment:")[0]
body_nohash = re.sub(r"(?m)^(#\w+\s*)+$", "", body)
bad = []
low = body.lower()
for w in WORDS:
    if re.search(r"\b"+re.escape(w), low): bad.append(f"AI-ish word: {w}")
for rx, msg in TELLS:
    if re.search(rx, body, re.I|re.S): bad.append(msg)
tags = re.findall(r"#\w+", t)
if len(tags) > 5: bad.append(f"hashtag wall ({len(tags)})")
if tags and len(tags) < 3: bad.append("fewer than 3 hashtags")
first = body.strip().split("\n")[0]
if len(first) > 140: bad.append(f"line 1 is {len(first)} chars (>140)")
words = len(body_nohash.split())
if words > 260: bad.append(f"{words} words (target 120-220)")
print(f"words={words} chars={len(body)} hashtags={len(tags)} line1={len(first)}")
print("CLEAN" if not bad else "FIX:\n- " + "\n- ".join(bad))
sys.exit(1 if bad else 0)
