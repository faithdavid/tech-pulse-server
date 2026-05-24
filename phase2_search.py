#!/usr/bin/env python3
"""Phase 2 — Deep-dive follow-ups using DuckDuckGo with targeted queries."""
import json, time, sys
from duckduckgo_search import DDGS

# Targeted deep-dive queries for each category
deep_queries = {
    "ai": [
        "Stanford AI Index 2026 report key findings",
        "world models AI continual learning breakthrough 2026",
        "GPT Claude Gemini new model May 2026",
        "AI reasoning benchmark leader 2026"
    ],
    "funding": [
        "AI startup funding round millions 2026 latest",
        "OpenAI Anthropic valuation funding 2026",
        "venture capital AI investment Q2 2026",
        "tech IPO SPAC 2026"
    ],
    "tools": [
        "VS Code Cursor Windsurf IDE 2026 update",
        "GitHub Copilot Claude Code developer tool 2026",
        "AI coding assistant new release May 2026",
        "software development framework 2026 launch"
    ],
    "industry": [
        "EU AI Act enforcement 2026",
        "Microsoft Google Apple news May 2026",
        "AI safety regulation policy 2026",
        "tech earnings Q1 2026 results"
    ],
    "oss": [
        "Llama Phi Mistral open source model 2026",
        "Hugging Face top model May 2026",
        "PyTorch TensorFlow release 2026",
        "open source database tool 2026"
    ]
}

results = {k: [] for k in deep_queries}
seen_urls = {k: set() for k in deep_queries}

for category, qlist in deep_queries.items():
    for q in qlist:
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(q, max_results=6):
                    url = r.get("href", "")
                    title = r.get("title", "")
                    body = r.get("body", "")
                    if url and url not in seen_urls[category] and len(title) > 10:
                        seen_urls[category].add(url)
                        results[category].append({
                            "title": title,
                            "description": body,
                            "url": url,
                            "source": url.split("/")[2] if url else ""
                        })
        except Exception as e:
            print(f"Error '{q}': {e}", file=sys.stderr)
        time.sleep(0.7)

# Print results
for cat, items in results.items():
    print(f"\n=== {cat.upper()} ({len(items)} results) ===")
    for item in items[:6]:
        print(f"  • {item['title']}")
        print(f"    {item['url']}")
        print(f"    {item['description'][:150]}...")

# Save combined Phase 1+2 results
with open("/home/faith/tech-pulse-server/phase1_raw.json") as f:
    phase1 = json.load(f)

combined = {cat: phase1.get(cat, []) + results.get(cat, []) for cat in ["ai","funding","tools","industry","oss"]}

with open("/home/faith/tech-pulse-server/phase2_raw.json", "w") as f:
    json.dump(combined, f, indent=2)

print(f"\n✅ Phase 2 complete. Combined totals:")
for cat, items in combined.items():
    print(f"  {cat}: {len(items)} results")
