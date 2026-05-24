#!/usr/bin/env python3
"""Phase 3 — Ultra-targeted DuckDuckGo searches with better queries."""
import json, time, sys
from duckduckgo_search import DDGS

specific_queries = {
    "ai": [
        '"new AI model" "beats" benchmark 2026',
        '"world model" AI research 2026 breakthrough',
        '"AI Index" Stanford 2026 report findings',
        '"GPT-5" OR "Claude 4" OR "Gemini 3" capabilities 2026'
    ],
    "funding": [
        '"raises" "million" AI startup 2026 Series',
        '"AI" company valuation "billion" 2026',
        '"funding round" AI infrastructure 2026',
        '"invests" "AI" "million" 2026'
    ],
    "tools": [
        '"VS Code" update 2026 new feature',
        '"Cursor" IDE AI coding 2026',
        '"GitHub Copilot" new feature 2026',
        '"developer tool" launch 2026 AI'
    ],
    "industry": [
        '"EU AI Act" enforcement 2026',
        '"AI regulation" policy "2026" law',
        'Microsoft Google AI earnings 2026',
        'Apple AI strategy 2026 news'
    ],
    "oss": [
        '"open source" "AI model" released 2026',
        'Meta Llama 4 open source 2026',
        'Mistral AI new model 2026 open source',
        '"Hugging Face" trending model May 2026'
    ]
}

results = {k: [] for k in specific_queries}
seen_urls = {k: set() for k in specific_queries}

for category, qlist in specific_queries.items():
    for q in qlist:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(q, max_results=5, region="wt-wt", safesearch="off", timelimit="m"):
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    if url and url not in seen_urls[category]:
                        seen_urls[category].add(url)
                        results[category].append({
                            "title": title,
                            "description": body,
                            "url": url,
                            "source": url.split("/")[2] if url else ""
                        })
        except Exception as e:
            print(f"Error '{q}': {e}", file=sys.stderr)
        time.sleep(1.0)

for cat, items in results.items():
    print(f"\n=== {cat.upper()} ({len(items)} results) ===")
    for item in items[:6]:
        print(f"  • {item['title']}")
        print(f"    {item['url']}")
        print(f"    {item['description'][:200]}")

with open("/home/faith/tech-pulse-server/phase3_raw.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Phase 3 complete. Results:")
for cat, items in results.items():
    print(f"  {cat}: {len(items)}")
