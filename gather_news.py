#!/usr/bin/env python3
"""Tech Pulse 24/7 — News gathering script using duckduckgo_search"""
import json
import sys
from duckduckgo_search import DDGS

CATEGORIES = {
    "ai": [
        "AI breakthrough new model May 2026",
        "artificial intelligence latest news June 2026",
        "large language model release 2026",
        "AI research paper breakthrough 2026"
    ],
    "funding": [
        "AI startup funding round 2026",
        "tech startup investment venture capital 2026",
        "AI company raises series funding 2026"
    ],
    "tools": [
        "developer tools release 2026",
        "new programming framework IDE 2026",
        "developer productivity tool launch 2026"
    ],
    "industry": [
        "tech industry news policy regulation AI 2026",
        "big tech company news antitrust 2026",
        "technology sector news June 2026"
    ],
    "oss": [
        "open source project release 2026",
        "notable open source launch GitHub 2026",
        "open source AI tool release 2026"
    ]
}

def search_news(queries, max_results=10):
    """Search for news using duckduckgo_search"""
    results = []
    seen_urls = set()
    with DDGS() as ddgs:
        for query in queries:
            try:
                for r in ddgs.text(query, max_results=max_results):
                    url = r.get("href", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        results.append({
                            "title": r.get("title", ""),
                            "description": r.get("body", ""),
                            "url": url,
                            "source": ""
                        })
            except Exception as e:
                print(f"Query '{query}' failed: {e}", file=sys.stderr)
    return results

def deduplicate(results):
    """Remove near-duplicate results"""
    seen_titles = set()
    deduped = []
    for r in results:
        title_lower = r["title"].lower().strip()
        # Simple dedup - check if any significant words overlap
        words = set(title_lower.split())
        is_dup = False
        for seen in seen_titles:
            seen_words = set(seen.split())
            overlap = words & seen_words
            if len(overlap) >= 4:  # 4+ words overlap = likely duplicate
                is_dup = True
                break
        if not is_dup:
            seen_titles.add(title_lower)
            deduped.append(r)
    return deduped

def enrich_with_sources(results):
    """Try to extract source domain and better descriptions"""
    for r in results:
        from urllib.parse import urlparse
        try:
            domain = urlparse(r["url"]).netloc
            r["source"] = domain.replace("www.", "").split(".")[0].title()
            if not r["source"]:
                r["source"] = "Tech News"
        except:
            r["source"] = "Tech News"
    return results

def main():
    all_data = {}
    for category, queries in CATEGORIES.items():
        print(f"\n=== Searching: {category} ===", file=sys.stderr)
        results = search_news(queries)
        results = deduplicate(results)
        results = enrich_with_sources(results)
        
        # Take top 6-8 results per category
        results = results[:8]
        
        for r in results:
            print(f"  - {r['title'][:80]}", file=sys.stderr)
        
        all_data[category] = results
    
    # Output JSON
    print(json.dumps(all_data, indent=2))

if __name__ == "__main__":
    main()
