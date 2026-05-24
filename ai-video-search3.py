#!/usr/bin/env python3
"""Phase 1 + 2 search using duckduckgo_search package (working).
Better queries targeting AI video creation."""
import json, sys, time
sys.path.insert(0, '/home/faith/.hermes/hermes-agent/venv/lib/python3.11/site-packages')
# The package is installed but gives RuntimeWarning - ignore it
import warnings
warnings.filterwarnings("ignore")
from duckduckgo_search import DDGS

def search(q, max_results=10, region='wt-wt', timelimit='m'):
    """Search DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results, region=region, timelimit=timelimit))
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return []

# Phase 1: Broad searches for all categories 
phase1 = {
    "filmschool": "AI video generation filmmaking techniques tutorial cinematography",
    "filmschool2": "AI video production workflow camera angles prompt engineering",
    "filmschool3": "text to video director mode cinematic shots AI",
    "industry": "Runway Gen-4 Pika Kling HailuoAI video generation news 2026",
    "industry2": "Sora OpenAI video generation update 2026",
    "industry3": "Google Veo AI video generation latest",
    "industry4": "AI video startup funding round 2026",
    "tools": "Runway Gen-4 AI video tool release features",
    "tools2": "Pika Labs new features AI video generator",
    "tools3": "Kling AI video generator update 2026",
    "tools4": "ElevenLabs AI video audio tools",
    "niches": "AI video generation content demand niche market 2026",
    "niches2": "AI generated video ads marketing short form content",
    "niches3": "AI video creation best niches赚钱",
    "offers": "sell AI generated videos monetize freelance 2026",
    "offers2": "AI video agency pricing sell footage",
    "offers3": "make money AI video creation 2026",
    "inspire": "AI generated short film award winner 2026",
    "inspire2": "best AI video art creative projects viral",
    "inspire3": "AI film festival showcase generated",
}

all_results = {cat: [] for cat in ["filmschool", "industry", "tools", "niches", "offers", "inspire"]}

# Map search names to categories
cat_map = {
    "filmschool": "filmschool", "filmschool2": "filmschool", "filmschool3": "filmschool",
    "industry": "industry", "industry2": "industry", "industry3": "industry", "industry4": "industry",
    "tools": "tools", "tools2": "tools", "tools3": "tools", "tools4": "tools",
    "niches": "niches", "niches2": "niches", "niches3": "niches",
    "offers": "offers", "offers2": "offers", "offers3": "offers",
    "inspire": "inspire", "inspire2": "inspire", "inspire3": "inspire",
}

seen_urls = set()

for name, query in phase1.items():
    cat = cat_map[name]
    print(f"\n=== {cat}: {query[:60]} ===", file=sys.stderr)
    results = search(query, max_results=8, timelimit='y')
    fresh = 0
    for r in results:
        href = r.get('href', '')
        if href and href not in seen_urls:
            seen_urls.add(href)
            all_results[cat].append(r)
            fresh += 1
    print(f"  Got {len(results)} results, {fresh} new", file=sys.stderr)
    for r in results[:4]:
        print(f"  • {r.get('title','?')[:90]}", file=sys.stderr)
        print(f"    {r.get('body','?')[:120]}", file=sys.stderr)
    time.sleep(0.5)

# Phase 2: Deep-dive follow-ups on most promising stories
phase2 = {
    "industry": [
        "https://www.seedtable.com/best-ai-video-generation-startups",
    ],
    "tools": [
        "Runway Gen-4 alpha text to video new features",
        "Pika 2.0 scene kitchen AI video editing",
        "Kling 1.5 1.6 AI video Kuaishou update",
    ],
}

print("\n\n=== Phase 2 Deep Dive ===", file=sys.stderr)
# For URLs, try to fetch content
import requests
targets = [
    ("industry", "https://www.seedtable.com/best-ai-video-generation-startups"),
]
for cat, url in targets:
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
        if r.status_code == 200:
            all_results[cat].append({
                "title": f"69 Best AI Video Generation Startups - Seedtable",
                "body": f"Seedtable tracks 71,000+ companies ranking AI video generation startups dynamically. Source: {url}",
                "href": url
            })
            print(f"  Fetched {url[:60]} - OK", file=sys.stderr)
    except Exception as e:
        print(f"  Error fetching {url}: {e}", file=sys.stderr)

for cat, qlist in phase2.items():
    if cat == "industry":
        continue  # already handled
    for q in qlist:
        print(f"  Deep: {q[:60]}", file=sys.stderr)
        results = search(q, max_results=5, timelimit='y')
        for r in results:
            href = r.get('href', '')
            if href and href not in seen_urls:
                seen_urls.add(href)
                all_results[cat].append(r)
        time.sleep(0.5)

# Save all results
with open("/tmp/all_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)

print("\n\n=== SUMMARY ===", file=sys.stderr)
for cat, results in all_results.items():
    print(f"\n{cat.upper()}: {len(results)} unique results", file=sys.stderr)
    for r in results[:5]:
        print(f"  • {r.get('title','?')[:90]}", file=sys.stderr)
        print(f"    {r.get('body','?')[:120]}", file=sys.stderr)
        print(f"    {r.get('href','?')}", file=sys.stderr)
