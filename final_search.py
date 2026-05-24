#!/usr/bin/env python3
"""Final search using ddgs (newer duckduckgo_search replacement) - Phase 1 + 2."""
import json, sys, time
from ddgs import DDGS

def search(q, max_results=8):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results))
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return []

all_results = {
    "filmschool": [],
    "industry": [],
    "tools": [],
    "niches": [],
    "offers": [],
    "inspire": []
}
seen_urls = set()

# Phase 1 - Broad parallel searches
phase1 = {
    "filmschool": [
        "AI video generation filmmaking techniques prompt engineering 2026",
        "text to video AI cinematography camera movement tutorial",
        "Runway Gen-4 filmmaking tutorial director mode",
        "AI video production workflow guide techniques",
    ],
    "industry": [
        "Runway Gen-4 AI video generation news release 2026",
        "Pika Labs funding $80M AI video news",
        "Google Veo 3.1 AI video generation audio release",
        "ElevenLabs image video platform launch 2026",
    ],
    "tools": [
        "Kling 3.0 AI video generator features storyboard",
        "Pika 2.0 AI video tool update features",
        "Runway Gen-4 AI video generator capabilities",
        "Hailuo AI video generator text to video",
    ],
    "niches": [
        "AI generated video content marketing demand 2026",
        "AI video ads creation business niche",
        "short form AI generated video trend social media",
    ],
    "offers": [
        "sell AI generated videos stock footage marketplace",
        "AI video creation freelance business monetization",
        "AI video production agency pricing services",
    ],
    "inspire": [
        "AI generated short film award winning 2026",
        "AI music video generated creative project",
        "best AI video art showcase 2026 viral",
    ],
}

print("=== Phase 1 ===", file=sys.stderr)
for cat, qlist in phase1.items():
    print(f"\n{cat}:", file=sys.stderr)
    for q in qlist:
        results = search(q, max_results=5)
        fresh = 0
        for r in results:
            href = r.get('href', '')
            if href and href not in seen_urls:
                seen_urls.add(href)
                all_results[cat].append(r)
                fresh += 1
        print(f"  '{q[:50]}...' → {len(results)} results, {fresh} new", file=sys.stderr)
        time.sleep(0.3)
    # Show top results
    for r in all_results[cat][:4]:
        print(f"  • {r.get('title','?')[:90]}", file=sys.stderr)
        print(f"    {r.get('body','?')[:120]}", file=sys.stderr)

# Phase 2 - Deep dive follow-ups
print("\n=== Phase 2 ===", file=sys.stderr)
phase2 = {
    "industry": [
        "Pika raises $80 million Series B AI video generation",
        "Runway Gen-4 world model video generation capabilities",
        "ElevenLabs Image Video beta platform models",
        "Google Veo 3.1 native audio generation video",
    ],
    "tools": [
        "Kling 3.0 multimodal AI video engine storyboard audio sync",
        "Runway Gen-4 features text to video generation",
        "Hailuo AI video generator Minimax text to video",
        "Pika 2.0 Lipsync Pikaformance features",
    ],
    "filmschool": [
        "Runway Gen-4 director mode camera control tutorial",
        "AI video prompting techniques cinematography guide",
        "Kling 3.0 multi shot storyboard tutorial",
    ],
}

for cat, qlist in phase2.items():
    print(f"\n{cat}:", file=sys.stderr)
    for q in qlist:
        results = search(q, max_results=5)
        fresh = 0
        for r in results:
            href = r.get('href', '')
            if href and href not in seen_urls:
                seen_urls.add(href)
                all_results[cat].append(r)
                fresh += 1
        print(f"  '{q[:50]}...' → {len(results)} results, {fresh} new", file=sys.stderr)
        time.sleep(0.3)
    for r in all_results[cat][:6]:
        print(f"  • {r.get('title','?')[:90]}", file=sys.stderr)
        print(f"    {r.get('body','?')[:130]}", file=sys.stderr)
        print(f"    {r.get('href','?')}", file=sys.stderr)

# Save results
with open("/tmp/final_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n\n=== FINAL SUMMARY ===", file=sys.stderr)
for cat, items in all_results.items():
    print(f"\n{cat}: {len(items)} total", file=sys.stderr)
    for r in items[:5]:
        print(f"  [{r.get('source','?')}] {r.get('title','?')[:80]}", file=sys.stderr)
