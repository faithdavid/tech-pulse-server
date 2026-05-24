#!/usr/bin/env python3
"""Phase 2 — Deep-dive follow-ups. Fetch article details + find more current stories."""
import json
import sys
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

def fetch_url(url, timeout=10):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/json,*/*',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            encoding = resp.headers.get_content_charset() or 'utf-8'
            return data.decode(encoding, errors='replace')
    except Exception as e:
        return None

def fetch_json(url, timeout=10):
    content = fetch_url(url, timeout)
    if content:
        try:
            return json.loads(content)
        except:
            return None
    return None

def extract_og(html, prop):
    m = re.search(rf'<meta[^>]*(?:property|name)=["\'](?:og:)?{prop}["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""

def extract_title(html):
    t = extract_og(html, "title")
    if t: return t
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if m:
        return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return ""

def extract_desc(html):
    d = extract_og(html, "description")
    if d: return d
    m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m: return m.group(1).strip()
    return ""

# Fetch specific articles to get better descriptions
articles_to_fetch = {
    "cerebras_ipo": "https://techcrunch.com/2026/05/14/cerebras-ipo-makes-billions-for-benchmark-but-vc-eric-vishria-almost-didnt-take-the-meeting/",
    "socher_ai": "https://techcrunch.com/2026/05/14/what-happens-when-ai-starts-building-itself/",
    "openai_apple": "https://techcrunch.com/2026/05/14/openai-is-reportedly-preparing-legal-action-against-apple-it-wouldnt-be-the-first-partner-to-feel-burned/",
    "vibe_hardware": "https://techcrunch.com/2026/05/14/lovable-just-backed-a-company-thats-looking-to-bring-vibe-coding-to-hardware/",
    "glasswing": "https://www.anthropic.com/glasswing",
    "openai_funding": "https://www.cnbc.com/2026/03/31/openai-funding-round-ipo.html",
    "anthropic_funding": "https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation"
}

print("=== Fetching article details ===", file=sys.stderr)
article_details = {}
for key, url in articles_to_fetch.items():
    print(f"  Fetching {key}...", file=sys.stderr)
    html = fetch_url(url)
    if html:
        title = extract_title(html)
        desc = extract_desc(html)
        # Also try to get article body excerpt
        body_match = re.search(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
        body = ""
        if body_match:
            body = re.sub(r'<[^>]+>', '', body_match.group(1)).strip()[:200]
        article_details[key] = {
            "title": title,
            "description": desc or body,
            "url": url
        }
        print(f"    Title: {title[:70]}", file=sys.stderr)
        print(f"    Desc: {desc[:100] if desc else 'N/A'}", file=sys.stderr)
    else:
        print(f"    Failed to fetch", file=sys.stderr)

# Fetch HN front page stories with date filter (last 24h)
print("\n=== HN latest top stories ===", file=sys.stderr)
hn_data = fetch_json("https://hn.algolia.com/api/v1/search?hitsPerPage=50&tags=story&numericFilters=points>20")
hn_current = []
if hn_data and "hits" in hn_data:
    for h in hn_data["hits"]:
        hn_current.append({
            "title": h.get("title", ""),
            "url": h.get("url", "") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}",
            "points": h.get("points", 0),
            "created_at": h.get("created_at", "")
        })

# Try to find more current tech news via googlesearch
print("\n=== Google search for current tech news ===", file=sys.stderr)
try:
    from googlesearch import search
    for query, num in [
        ("Cerebras IPO news 2026", 5),
        ("AI startup news this week 2026", 5),
        ("open source AI release June 2026", 5),
        ("developer tools AI coding 2026 launch", 5),
    ]:
        print(f"  Searching: {query[:50]}", file=sys.stderr)
        for url in search(query, num_results=num, lang="en", region="us"):
            html = fetch_url(url)
            if html:
                title = extract_title(html)
                desc = extract_desc(html)
                domain = urlparse(url).netloc
                print(f"    {domain:30s} | {title[:70]}", file=sys.stderr)
except Exception as e:
    print(f"Google search error: {e}", file=sys.stderr)

# Print all results for reference
print("\n\n=== SUMMARY ===", file=sys.stderr)
print(json.dumps({"articles": article_details, "hn_current": hn_current[:10]}, indent=2))
