#!/usr/bin/env python3
"""Scrape AI video news using requests + BeautifulSoup directly"""
import json, sys, re, time
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def fetch_urls(source, urls):
    """Try to fetch text content from a list of URLs"""
    results = []
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            if r.status_code != 200:
                print(f"  [{source}] {r.status_code} for {url[:80]}", file=sys.stderr)
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            # Remove scripts, styles
            for tag in soup(['script','style','nav','footer','header']):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            # Get title
            title = soup.title.string.strip() if soup.title else url
            results.append({"url": url, "title": title, "text": text[:3000]})
            print(f"  [{source}] OK: {title[:80]}", file=sys.stderr)
            time.sleep(1)
        except Exception as e:
            print(f"  [{source}] ERR {url[:60]}: {e}", file=sys.stderr)
    return results

all_results = {}

# Try ElevenLabs blog
print("=== ELEVENLABS ===", file=sys.stderr)
all_results["elevenlabs"] = fetch_urls("elevenlabs", [
    "https://elevenlabs.io/blog",
    "https://elevenlabs.io/blog/introducing-elevenlabs-image-and-video",
    "https://elevenlabs.io/blog/introducing-elevenmusic",
])

# Try Runway
print("=== RUNWAY ===", file=sys.stderr)
all_results["runway"] = fetch_urls("runway", [
    "https://runwayml.com/news",
    "https://runwayml.com/research",
])

# Try Kling
print("=== KLING ===", file=sys.stderr)
all_results["kling"] = fetch_urls("kling", [
    "https://klingai.com/blog",
])

# Try HeyGen
print("=== HEYGEN ===", file=sys.stderr)
all_results["heygen"] = fetch_urls("heygen", [
    "https://www.heygen.com/blog",
])

# Try Google DeepMind Veo
print("=== DEEPMIND ===", file=sys.stderr)
all_results["deepmind"] = fetch_urls("deepmind", [
    "https://deepmind.google/technologies/veo/",
])

# Save all raw results
with open("/home/faith/tech-pulse-server/scraped_results.json", "w") as f:
    json.dump(all_results, f, indent=2)

total = sum(len(v) for v in all_results.values())
print(f"\nTotal scraped pages: {total}", file=sys.stderr)
