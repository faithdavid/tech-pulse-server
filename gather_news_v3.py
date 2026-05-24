#!/usr/bin/env python3
"""Tech Pulse v3 — Multi-source news gathering"""
import json
import sys
import re
from datetime import datetime, timezone
from urllib.parse import urlparse
import urllib.request
import urllib.error
import socket

def fetch_url(url, timeout=10):
    """Fetch a URL with proper headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/json,application/xml;q=0.9,*/*;q=0.8',
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
    """Fetch JSON from URL"""
    content = fetch_url(url, timeout)
    if content:
        try:
            return json.loads(content)
        except:
            return None
    return None

def extract_from_html(html):
    """Extract title and description from HTML"""
    title = ""
    description = ""
    
    if not html:
        return title, description
    
    # Try to find title
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if m:
        title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    
    # Try OG title
    m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m:
        title = m.group(1).strip()
    
    # Try OG description
    m = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m:
        description = m.group(1).strip()
    else:
        # Try meta description
        m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if m:
            description = m.group(1).strip()
    
    return title, description

# === SOURCE 1: Hacker News API ===
def fetch_hn_stories(query="", min_points=30):
    """Fetch stories from HN Algolia API"""
    results = []
    if query:
        url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&hitsPerPage=30&tags=story&numericFilters=points>={min_points}"
    else:
        url = f"https://hn.algolia.com/api/v1/search?hitsPerPage=50&tags=story&numericFilters=points>={min_points}"
    
    data = fetch_json(url)
    if data and "hits" in data:
        for h in data["hits"]:
            title = h.get("title", "")
            story_url = h.get("url", "") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
            points = h.get("points", 0)
            desc = h.get("story_text", "") or ""
            if desc:
                desc = re.sub(r'<[^>]+>', '', desc)[:300]
            else:
                desc = f"{points} points on Hacker News"
            
            domain = urlparse(story_url).netloc
            source = domain.replace("www.", "")
            
            results.append({
                "title": title,
                "description": desc,
                "url": story_url,
                "source": source or "news.ycombinator.com"
            })
    return results

# === SOURCE 2: Direct tech news site scraping ===
def scrape_techcrunch():
    """Scrape TechCrunch front page"""
    results = []
    html = fetch_url("https://techcrunch.com/")
    if not html:
        return results
    
    # Find article links
    articles = re.findall(r'<a[^>]*href="(https?://techcrunch\.com/\d{4}/\d{2}/\d{2}/[^"]+)"[^>]*>', html)
    seen = set()
    for url in articles:
        if url in seen:
            continue
        seen.add(url)
        title, desc = extract_from_html(fetch_url(url))
        if title:
            results.append({
                "title": title,
                "description": desc or "Latest from TechCrunch",
                "url": url,
                "source": "techcrunch.com"
            })
    return results

def scrape_theverge():
    """Scrape The Verge AI/tech section"""
    results = []
    html = fetch_url("https://www.theverge.com/ai-artificial-intelligence")
    if not html:
        return results
    
    articles = re.findall(r'<a[^>]*href="(https?://www\.theverge\.com/[^"]+)"[^>]*>', html)
    seen = set()
    for url in articles:
        if url in seen or not re.search(r'/20\d{2}/\d{2}/\d{2}/', url):
            continue
        seen.add(url)
        title, desc = extract_from_html(fetch_url(url))
        if title:
            results.append({
                "title": title,
                "description": desc or "Latest from The Verge",
                "url": url,
                "source": "theverge.com"
            })
    return results

# === SOURCE 3: Google News via googlesearch-python ===
def search_google_news(query, num=10):
    """Search Google News using googlesearch-python"""
    results = []
    try:
        from googlesearch import search
        for url in search(query, num_results=num, lang="en", region="us"):
            title, desc = extract_from_html(fetch_url(url))
            if title:
                domain = urlparse(url).netloc
                source = domain.replace("www.", "")
                results.append({
                    "title": title,
                    "description": desc or "",
                    "url": url,
                    "source": source or "unknown"
                })
    except Exception as e:
        print(f"Google search error for '{query[:50]}': {e}", file=sys.stderr)
    return results

# === CATEGORY-SPECIFIC SEARCHES ===
CATEGORY_SEARCHES = {
    "ai": [
        lambda: scrape_theverge(),
        lambda: fetch_hn_stories("AI", min_points=20),
        lambda: search_google_news("AI model breakthrough 2026", 8),
        lambda: search_google_news("generative AI latest news", 8),
    ],
    "funding": [
        lambda: fetch_hn_stories("funding", min_points=15),
        lambda: search_google_news("AI startup funding round 2026", 8),
        lambda: search_google_news("venture capital technology investment 2026", 8),
    ],
    "tools": [
        lambda: fetch_hn_stories("developer tool", min_points=20),
        lambda: search_google_news("developer tools release 2026", 8),
        lambda: search_google_news("AI coding assistant tool new 2026", 8),
    ],
    "industry": [
        lambda: scrape_techcrunch(),
        lambda: fetch_hn_stories("tech", min_points=30),
        lambda: search_google_news("tech industry news policy 2026", 8),
        lambda: search_google_news("EU AI Act regulation enforcement 2026", 8),
    ],
    "oss": [
        lambda: fetch_hn_stories("open source", min_points=25),
        lambda: search_google_news("open source AI project release 2026", 8),
        lambda: search_google_news("notable open source launch 2026", 8),
    ]
}

def deduplicate(results):
    """Remove near-duplicate results"""
    seen = set()
    deduped = []
    for r in results:
        url = r.get("url", "")
        title = r.get("title", "").lower().strip()
        if url in seen:
            continue
        # Dedup by URL
        seen.add(url)
        # Also dedup by very similar titles
        is_dup = False
        title_words = set(title.split())
        for existing in deduped:
            existing_words = set(existing["title"].lower().split())
            overlap = title_words & existing_words
            if len(overlap) >= len(title_words) * 0.7 and len(overlap) >= 3:
                is_dup = True
                break
        if not is_dup:
            deduped.append(r)
    return deduped

def rank_results(results):
    """Rank by source quality and description length"""
    premium_sources = [
        "techcrunch.com", "theverge.com", "arstechnica.com",
        "reuters.com", "bloomberg.com", "cnbc.com",
        "wired.com", "venturebeat.com", "zdnet.com",
        "openai.com", "anthropic.com", "google.ai",
        "github.blog", "huggingface.co"
    ]
    
    for r in results:
        score = 0
        source = r.get("source", "").lower()
        desc = r.get("description", "")
        
        if any(ps in source for ps in premium_sources):
            score += 3
        if len(desc) > 50:
            score += 2
        elif len(desc) > 20:
            score += 1
        # Prefer results with specific numbers
        if re.search(r'\d+', r.get("title", "") + " " + desc):
            score += 1
        
        r["_score"] = score
    
    results.sort(key=lambda x: x["_score"], reverse=True)
    for r in results:
        del r["_score"]
    return results

def main():
    all_data = {}
    
    for category, searchers in CATEGORY_SEARCHES.items():
        print(f"\n=== {category.upper()} ===", file=sys.stderr)
        all_results = []
        
        for searcher in searchers:
            try:
                results = searcher()
                print(f"  Got {len(results)} results", file=sys.stderr)
                all_results.extend(results)
            except Exception as e:
                print(f"  Error: {e}", file=sys.stderr)
        
        all_results = deduplicate(all_results)
        all_results = rank_results(all_results)
        all_results = all_results[:6]  # Keep top 6
        
        for r in all_results:
            print(f"  {r['source']:30s} | {r['title'][:70]}", file=sys.stderr)
        
        all_data[category] = all_results
    
    print(json.dumps(all_data, indent=2))

if __name__ == "__main__":
    main()
