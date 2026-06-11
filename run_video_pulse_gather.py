#!/usr/bin/env python3
"""Gather AI Video Pulse data via ddgs for all 6 categories."""
import json
import re
import time
from urllib.parse import urlparse
from ddgs import DDGS

OUT = "/home/ubuntu/tech-pulse-server/ai-video-data.json"

IMAGES = {
    "filmschool": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1558494949-ef0d38d3f9e2?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=60",
    "niches": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=600&q=60",
    "offers": "https://images.unsplash.com/photo-1607083206869-4c6d35b4c5f3?w=600&q=60",
    "inspire": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&q=60",
}

QUERIES = {
    "filmschool": [
        "AI filmmaking film school Runway 2026",
        "generative AI film production tutorial",
        "AI cinema storytelling workflow",
    ],
    "industry": [
        "AI video industry news studio deals 2026",
        "OpenAI Sora Disney licensing AI video",
        "Runway Luma AI video funding 2026",
    ],
    "tools": [
        "new AI video generator 2026",
        "Adobe Premiere AI video editing 2026",
        "best AI text to video tools 2026",
    ],
    "niches": [
        "faceless YouTube AI video niches 2026",
        "AI video marketing vertical applications",
        "AI short film viral trends 2026",
    ],
    "offers": [
        "AI video generator coupon discount 2026",
        "cheapest AI video subscription plans",
        "AI video freelance pricing services 2026",
    ],
    "inspire": [
        "Runway AI film festival 2026",
        "award winning AI generated short film",
        "best AI video creative showcase 2026",
    ],
}

EXTRA_IMAGES = [
    "https://images.unsplash.com/photo-1536240478700-b869070f9279?w=600&q=60",
    "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=600&q=60",
    "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=600&q=60",
    "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=600&q=60",
]


def source_from_url(url):
    try:
        host = urlparse(url).netloc.replace("www.", "")
        return host.split(".")[0].title() if host else "Web"
    except Exception:
        return "Web"


def to_story(r, cat, idx):
    title = (r.get("title") or "").strip()[:200]
    body = (r.get("body") or "").strip()
    href = (r.get("href") or "").strip()
    if not title or not href.startswith("http"):
        return None
    img = IMAGES[cat]
    if idx > 0:
        img = EXTRA_IMAGES[(idx - 1) % len(EXTRA_IMAGES)]
    desc = body[:300] if body else f"Latest in AI video — {cat}."
    return {
        "title": title,
        "description": desc,
        "url": href,
        "source": source_from_url(href),
        "image_url": img,
    }


def gather_category(cat, queries):
    seen = set()
    stories = []
    with DDGS() as ddgs:
        for q in queries:
            try:
                for r in ddgs.text(q, max_results=5):
                    key = (r.get("href") or "")[:80]
                    if key in seen:
                        continue
                    seen.add(key)
                    s = to_story(r, cat, len(stories))
                    if s:
                        stories.append(s)
                    if len(stories) >= 4:
                        return stories
            except Exception as e:
                print(f"  warn {cat}/{q}: {e}")
            time.sleep(0.4)
    return stories[:4]


def main():
    data = {}
    for cat, queries in QUERIES.items():
        print(f"Gathering {cat}...")
        data[cat] = gather_category(cat, queries)
        print(f"  -> {len(data[cat])} stories")
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT}, total {sum(len(v) for v in data.values())}")


if __name__ == "__main__":
    main()