#!/usr/bin/env python3
"""Phase 2 — deep-dive follow-ups on promising stories"""
import json, sys, time, re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}

targets = [
    # ElevenLabs Image & Video deep dive
    {"source": "elevenlabs_video", "url": "https://elevenlabs.io/blog/introducing-elevenlabs-image-and-video"},
    # ElevenLabs crosses $500M ARR
    {"source": "elevenlabs_arr", "url": "https://elevenlabs.io/blog/elevenlabs-crosses-500m-arr"},
    # Pika announcement
    {"source": "pika", "url": "https://pika.art/blog/announcement"},
    # HeyGen Avatar V
    {"source": "heygen_avatar", "url": "https://www.heygen.com/blog/announcing-avatar-v"},
    # HeyGen Seedance 2.0
    {"source": "heygen_seedance", "url": "https://www.heygen.com/blog/introducing-seedance-2-and-heygen"},
    # Runway Characters
    {"source": "runway_chars", "url": "https://runwayml.com/characters"},
    # Runway Gen-4.5
    {"source": "runway_gen45", "url": "https://runwayml.com/research/introducing-runway-gen-4.5"},
    # Kling Director Mode
    {"source": "kling_director", "url": "https://klingai.com/blog/kling-video-3-director-mode-multi-shot-tutorial"},
    # Kling Native 4K
    {"source": "kling_4k", "url": "https://klingai.com/blog/professional-native-4k-ai-video-generation"},
    # Kling Subject Binding
    {"source": "kling_binding", "url": "https://klingai.com/blog/kling-3-subject-binding-character-consistency"},
    # Kling Lighting Prompts
    {"source": "kling_lighting", "url": "https://klingai.com/blog/ai-video-lighting-prompts-volumetric-golden-hour"},
    # AI video freelancer pricing
    {"source": "freelance_pricing", "url": "https://betonai.net/the-ai-freelancer-pricing-playbook-2026-how-to-charge-k-5k-per-project-using-value-based-pricing-scripts-templates-and-rate-tables/"},
    # Clippie AI freelancer
    {"source": "clippie", "url": "https://clippie.ai/blog/freelancers-scale-client-work-ai-video-2026"},
    # HeyGen April 2026 release
    {"source": "heygen_april", "url": "https://www.heygen.com/blog/heygen-april-2026-release"},
]

results = []
for t in targets:
    try:
        r = requests.get(t["url"], headers=HEADERS, timeout=20, allow_redirects=True)
        if r.status_code != 200:
            print(f"  [{t['source']}] HTTP {r.status_code}", file=sys.stderr)
            continue
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup(['script','style','nav','footer','header','noscript']):
            tag.decompose()
        text = soup.get_text(separator='\n', strip=True)
        # Extract meaningful content
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 40]
        content = '\n'.join(lines[:80])  # Keep first 80 meaningful lines
        title = soup.title.string.strip() if soup.title else t["url"]
        results.append({"source": t["source"], "url": t["url"], "title": title, "content": content[:5000]})
        print(f"  [{t['source']}] OK: {title[:80]}", file=sys.stderr)
        time.sleep(1)
    except Exception as e:
        print(f"  [{t['source']}] ERR: {e}", file=sys.stderr)

with open("/home/faith/tech-pulse-server/phase2_deepdives.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\nTotal deep-dives: {len(results)}", file=sys.stderr)
