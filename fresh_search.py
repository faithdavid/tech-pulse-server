#!/usr/bin/env python3
"""Fresh search using ddgs library."""
import json, sys, time
from ddgs import DDGS

def search(q, max_results=10):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results))
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return []

queries = {
    "filmschool": [
        "AI video filmmaking techniques tutorial April May 2026",
        "AI cinematography guide Sora Runway Kling prompting 2026",
        "AI video production workflow character consistency 2026",
    ],
    "industry": [
        "Sora OpenAI shutdown Veo Google AI video 2026",
        "Runway Kling Pika AI video generation news May 2026",
        "AI video model release milestone April 2026",
        "Google Gemini Veo AI video update 2026",
    ],
    "tools": [
        "new AI video generator tool launched 2026",
        "Kling Runway Pika AI video software update 2026",
        "AI video editing audio generation tool 2026",
        "Runway Gen-4 Adobe Firefly AI video integration 2026",
    ],
    "niches": [
        "AI video content niche demand 2026 YouTube TikTok",
        "faceless YouTube channel AI video 2026",
        "AI generated video viral niche trend 2026",
    ],
    "offers": [
        "monetize AI generated videos sell 2026",
        "AI video commercial license commercial use 2026",
        "make money AI video creator freelancing 2026",
    ],
    "inspire": [
        "AI generated film award winning short 2026",
        "AI film festival showcase competition 2026",
        "AI art film creative project director 2026",
    ],
}

all_results = {}
for category, qlist in queries.items():
    print(f"=== {category} ===", file=sys.stderr)
    all_results[category] = []
    seen = set()
    for q in qlist:
        print(f"  Searching: {q}", file=sys.stderr)
        results = search(q)
        for r in results:
            url = r.get("href", r.get("link", "")).split("?")[0].split("#")[0]
            if url and url not in seen:
                seen.add(url)
                all_results[category].append({
                    "title": r.get("title", ""),
                    "url": url,
                    "snippet": r.get("body", r.get("snippet", "")),
                })
        time.sleep(1)
    print(f"  Got {len(all_results[category])} unique results", file=sys.stderr)

with open("/tmp/fresh_search_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
print("Saved to /tmp/fresh_search_results.json", file=sys.stderr)
