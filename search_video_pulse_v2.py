#!/usr/bin/env python3
"""AI Video Pulse — Search scraper using Bing (via requests + BeautifulSoup)."""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from urllib.parse import urlparse, quote_plus

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

CATEGORY_QUERIES = {
    "filmschool": [
        "AI filmmaking techniques workflow 2026",
        "generative AI film production tutorial",
        "AI cinema camera movement storytelling",
        "Runway Pika filmmaking tips",
    ],
    "industry": [
        "AI video platform news May 2026",
        "OpenAI Sora update 2026",
        "Runway Gen-4 AI video release",
        "AI video generation funding",
    ],
    "tools": [
        "new AI video generator editor 2026",
        "AI video editing tool launch May 2026",
        "text to video AI tool latest",
        "AI video creation software review",
    ],
    "niches": [
        "AI video art trends 2026",
        "AI generated music video style",
        "cinematic AI video aesthetic",
        "AI short film viral trend",
    ],
    "offers": [
        "AI video freelance pricing 2026",
        "AI filmmaker client strategy Upwork",
        "selling AI video production services",
        "AI video creator business rates",
    ],
    "inspire": [
        "best AI generated short films 2026",
        "award winning AI film 2026",
        "viral AI video creator notable",
        "AI filmmaker breakthrough work",
    ],
}

def search_bing(query, max_results=5):
    """Search Bing and parse results."""
    url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f"  Error searching '{query}': {e}")
        return []
    
    soup = BeautifulSoup(html, "lxml")
    results = []
    
    # Bing result containers
    # Try multiple selectors
    selectors = [
        "li.b_algo",
        "li.b_algo div.b_caption",
        "div.b_caption",
        ".b_algo",
    ]
    
    # Find all result containers
    containers = soup.select("li.b_algo")
    if not containers:
        containers = soup.select(".b_algo")
    
    for container in containers:
        # Title link
        title_elem = container.select_one("h2 a") or container.select_one("a[href]")
        if not title_elem:
            continue
        
        title = title_elem.get_text(strip=True)
        link = title_elem.get("href", "")
        
        if not link or not link.startswith("http"):
            continue
        
        # Skip known non-result links
        if "bing.com" in link.lower() and "/search" not in link.lower():
            continue
        
        # Description/snippet
        desc_elem = container.select_one(".b_caption p") or container.select_one("p")
        description = ""
        if desc_elem:
            description = desc_elem.get_text(strip=True)
        
        # Source from domain
        domain = urlparse(link).netloc
        source = domain.replace("www.", "").split(".")[0].title()
        
        results.append({
            "title": title,
            "url": link,
            "description": description[:400] if description else "",
            "source": source,
        })
        
        if len(results) >= max_results:
            break
    
    return results

def deduplicate(results):
    """Remove near-duplicate results."""
    seen = set()
    unique = []
    for r in results:
        key = urlparse(r["url"]).netloc + "|" + r["title"][:60]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique

# === MAIN ===
all_data = {cat: [] for cat in CATEGORY_QUERIES}

for category, queries in CATEGORY_QUERIES.items():
    print(f"\n{'='*60}")
    print(f"CATEGORY: {category}")
    print(f"{'='*60}")
    
    all_results = []
    for i, query in enumerate(queries):
        print(f"  [{i+1}/{len(queries)}] Searching: {query}")
        results = search_bing(query, max_results=4)
        print(f"    Found {len(results)} results")
        all_results.extend(results)
        if i < len(queries) - 1:
            time.sleep(0.5)  # Polite delay
    
    # Deduplicate
    all_results = deduplicate(all_results)
    print(f"  Total unique results: {len(all_results)}")
    
    # Take top 3-4
    stories = []
    unsplash_photo_map = {
        "filmschool": "photo-1485846234645",
        "industry": "photo-1492691527719",
        "tools": "photo-1620712943543",
        "niches": "photo-1551288049",
        "offers": "photo-1454165804606",
        "inspire": "photo-1536240478700",
    }
    
    for r in all_results[:4]:
        stories.append({
            "title": r["title"],
            "description": r.get("description", "")[:300] if r.get("description") else f"Latest development in AI video ({category}).",
            "url": r["url"],
            "source": r.get("source", "Web"),
            "image_url": ""
        })
    
    all_data[category] = stories

# Write the data file
output_path = "/home/faith/tech-pulse-server/ai-video-data.json"
with open(output_path, "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"Data written to {output_path}")
print(f"Total stories: {sum(len(v) for v in all_data.values())}")
for cat, stories in all_data.items():
    print(f"  {cat}: {len(stories)} stories")
    for s in stories:
        print(f"    - {s['title'][:80]}...")
