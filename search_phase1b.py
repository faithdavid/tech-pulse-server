#!/usr/bin/env python3
"""Phase 1 search using googlesearch-python"""
import json, sys
from googlesearch import search

queries = {
    "filmschool": "AI filmmaking cinematic techniques tutorial 2025 2026",
    "industry": "AI video generation company launch funding 2026",
    "tools": "new AI video generator released 2026",
    "niches": "AI video content trends viral style 2026",
    "offers": "AI video freelancer pricing Upwork 2026",
    "inspire": "best AI generated film short 2025 2026",
}

results = {}
for cat, q in queries.items():
    try:
        urls = list(search(q, num_results=10))
        results[cat] = [{"url": u} for u in urls]
        print(f"[OK] {cat}: {len(results[cat])} results", file=sys.stderr)
    except Exception as e:
        results[cat] = []
        print(f"[ERR] {cat}: {e}", file=sys.stderr)

with open("/home/faith/tech-pulse-server/phase1_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nTotal: {sum(len(v) for v in results.values())}", file=sys.stderr)
