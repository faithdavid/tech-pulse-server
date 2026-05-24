#!/usr/bin/env python3
"""Phase 1 + Phase 2 search for AI Video Pulse using DuckDuckGo."""
import json, sys, time
from duckduckgo_search import DDGS

def search(q, max_results=10):
    """Search DuckDuckGo and return results."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results))
    except Exception as e:
        print(f"  ERROR searching '{q}': {e}", file=sys.stderr)
        return []

# Phase 1: Broad searches for all 6 categories
queries = {
    "filmschool": [
        "AI video generation filmmaking techniques tutorial 2026",
        "text to video AI cinematography guide 2026",
        "AI film production workflow techniques 2026",
    ],
    "industry": [
        "Sora Runway Pika Kling AI video news May 2026",
        "AI video generation company funding milestone 2026",
        "OpenAI Sora update Google Veo AI video latest",
    ],
    "tools": [
        "new AI video tool software release May 2026",
        "Runway Gen-4 Pika 2.0 Kling AI tool update 2026",
        "AI video editing software launch 2026",
    ],
    "niches": [
        "AI generated video content demand niches 2026",
        "AI video creation in-demand categories 2026",
        "AI short form video content trends 2026",
    ],
    "offers": [
        "sell AI generated videos monetization 2026",
        "AI video creation freelancing pricing 2026",
        "AI video content creator income strategy 2026",
    ],
    "inspire": [
        "AI generated film award winning 2026",
        "best AI video art creative projects 2026",
        "AI film festival showcase 2026",
    ],
}

phase1_results = {}
for category, qlist in queries.items():
    print(f"=== Phase 1: {category} ===", file=sys.stderr)
    phase1_results[category] = []
    for q in qlist:
        print(f"  Searching: {q}", file=sys.stderr)
        results = search(q)
        phase1_results[category].extend(results)
        print(f"  Got {len(results)} results", file=sys.stderr)
        time.sleep(0.5)  # polite delay

# Save Phase 1 results for analysis
with open("/tmp/phase1_results.json", "w") as f:
    json.dump(phase1_results, f, indent=2, default=str)

# Print summary
for category, results in phase1_results.items():
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  {category}: {len(results)} total results", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    for r in results[:5]:
        print(f"  - {r.get('title','?')[:80]}", file=sys.stderr)
        print(f"    {r.get('body','?')[:120]}", file=sys.stderr)
        print(f"    {r.get('href','?')}", file=sys.stderr)
        print(file=sys.stderr)

print("Phase 1 complete. Results saved to /tmp/phase1_results.json", file=sys.stderr)
