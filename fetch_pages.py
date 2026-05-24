#!/usr/bin/env python3
"""Fetch key pages for detailed content to use in the pulse."""
import json, sys, re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"}

pages = {
    "pika_funding": "https://www.maginative.com/article/pika-labs-secures-80m-in-series-b-funding/",
    "veo_31": "https://deepmind.google/technologies/veo/",
    "elevenlabs_video": "https://elevenlabs.io/blog/introducing-elevenlabs-image-and-video/",
    "runway_gen4": "https://runwayml.com/",
    "kling_30": "https://kling3.pro/",
    "hailuo": "https://hailuoai.video/",
    "digen_trends": "https://resource.digen.ai/top-emerging-ai-video-generator-trends-2026/",
    "digen_guide": "https://resource.digen.ai/how-to-use-ai-video-generators/",
    "digen_tutorial": "https://resource.digen.ai/ai-video-generator-from-text-tutorial-2026/",
    "digen_visual": "https://resource.digen.ai/ai-video-generation-for-visual-ideas-2026/",
    "heygen_marketing": "https://www.heygen.com/blog/ai-video-generators-in-marketing",
    "dubai_award": "https://gulfnews.com/entertainment/dubai-launches-1m-ai-short-film-award",
}

for name, url in pages.items():
    print(f"\n=== {name} ===", file=sys.stderr)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        # Save first 2000 chars
        with open(f"/tmp/{name}.txt", "w") as f:
            f.write(text[:3000])
        print(f"  Saved {len(text[:3000])} chars", file=sys.stderr)
    except Exception as e:
        print(f"  FAIL: {e}", file=sys.stderr)

print("\nDone fetching pages.", file=sys.stderr)
