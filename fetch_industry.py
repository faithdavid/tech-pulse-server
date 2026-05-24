#!/usr/bin/env python3
"""Fetch industry/policy news from multiple sources"""
import json, urllib.request, urllib.parse, sys, re, html

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Accept": "text/html,application/json,*/*"
    })
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='replace')

def fetch_ddg_simple(query, max_results=10):
    """Simpler DDG scraper"""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    try:
        html_content = fetch_url(url)
        results = []
        # Find all result blocks
        blocks = re.split(r'<div class="result results_links[^"]*">', html_content)
        for block in blocks[1:]:
            # Get title
            title_match = re.search(r'class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)', block)
            if not title_match: continue
            href = title_match.group(1)
            title = html.unescape(re.sub(r'<[^>]+>', '', title_match.group(2))).strip()
            if not title: continue
            
            # Clean DDG redirect URL
            if '//duckduckgo.com/l/?uddg=' in href:
                href = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
            elif href.startswith('/'):
                continue
            
            # Get snippet
            snippet_match = re.search(r'class="result__snippet"[^>]*>(.*?)</(?:a|div)', block, re.DOTALL)
            snippet = ""
            if snippet_match:
                snippet = html.unescape(re.sub(r'<[^>]+>', '', snippet_match.group(1))).strip()
            
            results.append({
                "title": title,
                "url": href,
                "snippet": snippet
            })
        return results[:max_results]
    except Exception as e:
        print(f"  DDG Error: {e}", file=sys.stderr)
        return []

def fetch_hn_industry():
    """Fetch industry/policy news from HN"""
    queries = [
        "AI regulation",
        "tech policy",
        "antitrust tech",
        "technology law",
        "tech industry news"
    ]
    results = []
    seen = set()
    for q in queries:
        url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(q)}&tags=story&hitsPerPage=8"
        try:
            data = json.loads(fetch_url(url))
            for h in data.get("hits", []):
                t = h.get("title", "")
                if t.lower() not in seen and t:
                    seen.add(t.lower())
                    results.append({
                        "title": t,
                        "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID','')}",
                        "points": h.get("points", 0),
                        "author": h.get("author", "")
                    })
        except:
            pass
    return results[:12]

# Try multiple industry queries
industry_queries = [
    "tech industry news regulation 2026",
    "AI regulation law policy technology companies",
    "big tech antitrust legislation 2026",
    "technology industry layoffs hiring 2026",
    "Google Apple Microsoft news 2026"
]

ddg_results = []
for q in industry_queries:
    r = fetch_ddg_simple(q, 6)
    ddg_results.extend(r)
    if len(ddg_results) >= 15:
        break

# Also try HN
hn_results = fetch_hn_industry()
print(f"DDG results: {len(ddg_results)}", file=sys.stderr)
print(f"HN results: {len(hn_results)}", file=sys.stderr)

# Combine, deduplicate
seen = set()
industry = []
for r in ddg_results:
    t = r["title"].lower()
    if t not in seen and len(t) > 10:
        seen.add(t)
        industry.append({
            "title": r["title"],
            "description": r.get("snippet", ""),
            "url": r["url"],
            "source": "DuckDuckGo",
            "image_url": ""
        })

for h in hn_results:
    t = h["title"].lower()
    if t not in seen:
        seen.add(t)
        pts = h.get("points", 0)
        desc = f"Trending with {pts} points on HN" if pts else ""
        industry.append({
            "title": h["title"],
            "description": desc,
            "url": h["url"],
            "source": "Hacker News",
            "image_url": ""
        })

print(f"Industry total: {len(industry)}", file=sys.stderr)

# Read existing data
with open("/home/faith/tech-pulse-server/pulse-data.json", "r") as f:
    data = json.load(f)

data["industry"] = industry[:8]

with open("/home/faith/tech-pulse-server/pulse-data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Updated pulse-data.json with industry data", file=sys.stderr)
