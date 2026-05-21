#!/usr/bin/env python3
"""
Jin Yong Character Course Generator - Kangbo Academy Style
Reads existing HTML + JSON data, rebuilds all courses with:
- Kangbo Academy dark theme (gold #e2b64f, no emoji)
- 8-chapter structured content
- 500-char narration script
- Audio player placeholder
"""

import os, re, json, sys

BASE = "/Users/apple/Desktop/OPC/jinyong-characters/docs"
COURSES_DIR = os.path.join(BASE, "courses")
OUTPUT_DIR = os.path.join(BASE, "courses_v2")  # New output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load character data from JSONs
all_chars = {}
seen = set()

for jf in os.listdir(COURSES_DIR):
    if not jf.endswith('.json'):
        continue
    with open(os.path.join(COURSES_DIR, jf)) as f:
        data = json.load(f)
    if "novels" in data:
        for nk, nd in data["novels"].items():
            novel_name = nd.get("novel_name", nk)
            for c in nd.get("characters", []):
                slug = c.get("slug", "")
                if slug not in seen:
                    seen.add(slug)
                    c["novel_name"] = novel_name
                    c["novel_key"] = nk
                    all_chars[slug] = c

print(f"Loaded {len(all_chars)} characters from JSON")
print("Ready for batch generation.")
