#!/usr/bin/env python3
"""Phase 1 search - broad parallel sweeps across all 6 AI video categories"""
import json, sys
from duckduckgo_search import DDGS

queries = {
    "filmschool": "AI filmmaking techniques tutorial 2026",
    "industry": "AI video platform launch news 2026",
    "tools": "new AI video generator text to video 2026",
    "niches": "AI video trend emerging style aesthetic 2026",
    "offers": "AI video freelancer pricing client strategy 2026",
    "inspire": "notable AI film maker creator project 2026",
}

results = {}
for cat, q in queries.items():
    try:
        r = DDGS().text(q, max_results=10)
        results[cat] = [{"title": x.get("title",""), "href": x.get("href",""), "body": x.get("body","")} for x in r]
        print(f"[OK] {cat}: {len(results[cat])} results", file=sys.stderr)
    except Exception as e:
        results[cat] = []
        print(f"[ERR] {cat}: {e}", file=sys.stderr)

with open("/home/faith/tech-pulse-server/phase1_results.json", "w") as f:
    json.dump(results, f, indent=2)
print(f"\nTotal results: {sum(len(v) for v in results.values())}", file=sys.stderr)
