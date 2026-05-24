#!/usr/bin/env python3
"""Phase 1 — Broad parallel sweeps across all 5 tech categories using DuckDuckGo."""
import json, time, sys
from duckduckgo_search import DDGS

queries = {
    "ai": [
        "AI breakthrough new model 2026",
        "large language model release May 2026",
        "artificial intelligence research breakthrough 2026",
        "AI model benchmark leader 2026"
    ],
    "funding": [
        "startup funding round AI 2026",
        "tech startup venture capital 2026",
        "AI company raises series funding 2026",
        "deep tech investment 2026"
    ],
    "tools": [
        "developer tools release 2026",
        "new programming IDE framework 2026",
        "developer productivity tool launch 2026",
        "AI coding assistant tool 2026"
    ],
    "industry": [
        "tech industry news regulation AI policy 2026",
        "big tech company news May 2026",
        "AI regulation policy government 2026",
        "technology industry layoffs hiring 2026"
    ],
    "oss": [
        "open source project release May 2026",
        "new open source tool launch 2026",
        "open source AI model release 2026",
        "github trending project May 2026"
    ]
}

results = {k: [] for k in queries}
seen_urls = {k: set() for k in queries}

for category, qlist in queries.items():
    for q in qlist:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(q, max_results=5):
                    url = r.get("href", "")
                    if url and url not in seen_urls[category]:
                        seen_urls[category].add(url)
                        results[category].append({
                            "title": r.get("title", ""),
                            "description": r.get("body", ""),
                            "url": url,
                            "source": r.get("source", "") or url.split("/")[2] if url else ""
                        })
        except Exception as e:
            print(f"Error searching '{q}': {e}", file=sys.stderr)
        time.sleep(0.5)

# Print summary
for cat, items in results.items():
    print(f"\n=== {cat.upper()} ({len(items)} results) ===")
    for item in items[:8]:
        print(f"  • {item['title']}")
        print(f"    {item['url']}")

# Save raw results
with open("/home/faith/tech-pulse-server/phase1_raw.json", "w") as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Phase 1 complete. Total results: {sum(len(v) for v in results.values())}")
