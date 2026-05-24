#!/usr/bin/env python3
"""AI Video Pulse — Scraper using multiple accessible sources."""

import requests
import json
import time
import re
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def get_hn_stories(query, max_results=5):
    """Search Hacker News via Algolia API."""
    url = f"https://hn.algolia.com/api/v1/search?query={requests.utils.quote(query)}&hitsPerPage={max_results}&tags=story"
    try:
        resp = requests.get(url, timeout=15)
        data = resp.json()
        results = []
        for hit in data.get("hits", []):
            title = hit.get("title", "")
            url_val = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            desc = hit.get("story_text", "")[:200] if hit.get("story_text") else ""
            source = "Hacker News"
            results.append({"title": title, "url": url_val, "description": desc, "source": source})
        return results
    except Exception as e:
        print(f"    HN API error: {e}")
        return []

def get_reddit_stories(subreddit, query, max_results=5):
    """Search Reddit via JSON API."""
    url = f"https://www.reddit.com/r/{subreddit}/search/.json?q={requests.utils.quote(query)}&sort=new&limit={max_results}&restrict_sr=1"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        data = resp.json()
        results = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            title = d.get("title", "")
            url_val = d.get("url", "")
            permalink = "https://www.reddit.com" + d.get("permalink", "")
            desc = d.get("selftext", "")[:200] if d.get("selftext") else ""
            results.append({"title": title, "url": url_val, "description": desc, "source": f"r/{subreddit}"})
        return results
    except Exception as e:
        print(f"    Reddit API error: {e}")
        return []

def get_google_news_rss(query, max_results=5):
    """Try Google News RSS."""
    url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        import xml.etree.ElementTree as ET
        root = ET.fromstring(resp.content)
        results = []
        for item in root.findall(".//item")[:max_results]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            desc = item.findtext("description", "")[:200] if item.findtext("description") else ""
            source = "Google News"
            results.append({"title": title, "url": link, "description": desc, "source": source})
        return results
    except Exception as e:
        print(f"    Google News error: {e}")
        return []

def scrape_website(url):
    """Try to scrape content from a specific website."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")
            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator=" ", strip=True)
            # Clean whitespace
            text = re.sub(r'\s+', ' ', text)
            return text[:2000]
        return None
    except:
        return None

# Define news source websites to scrape directly
NEWS_SOURCES = {
    "filmschool": [
        {"url": "https://theresanaiforthat.com/c/video-generation/", "desc": "AI video tools directory"},
        {"url": "https://www.reddit.com/r/aivideo/top/.json?limit=15", "type": "reddit_api"},
    ],
    "industry": [
        {"url": "https://techcrunch.com/tag/ai-video/feed/", "desc": "TechCrunch AI video"},
        {"url": "https://www.theverge.com/ai-artificial-intelligence/archive", "desc": "The Verge AI"},
    ],
    "tools": [
        {"url": "https://www.reddit.com/r/StableDiffusion/top/.json?limit=15", "type": "reddit_api"},
    ],
}

# Build a comprehensive search using multiple sources
CATEGORY_SOURCES = {
    "filmschool": [
        ("hn", "AI video filmmaking"),
        ("hn", "generative AI film production"),
        ("reddit", {"sub": "aivideo", "q": "filmmaking"}),
        ("reddit", {"sub": "aivideo", "q": "tutorial"}),
        ("gn", "AI filmmaking techniques 2026"),
    ],
    "industry": [
        ("hn", "AI video generation"),
        ("hn", "Sora AI video"),
        ("reddit", {"sub": "singularity", "q": "AI video"}),
        ("gn", "AI video platform news 2026"),
    ],
    "tools": [
        ("hn", "AI video tool"),
        ("hn", "text to video"),
        ("reddit", {"sub": "StableDiffusion", "q": "video"}),
        ("gn", "new AI video generator 2026"),
    ],
    "niches": [
        ("hn", "AI generated video art"),
        ("reddit", {"sub": "aivideo", "q": "music video"}),
        ("gn", "AI video art trends 2026"),
    ],
    "offers": [
        ("hn", "freelance AI video"),
        ("reddit", {"sub": "freelance", "q": "AI video"}),
        ("gn", "AI video freelance pricing 2026"),
    ],
    "inspire": [
        ("hn", "AI generated short film"),
        ("reddit", {"sub": "aivideo", "q": "short film"}),
        ("gn", "best AI short film 2026"),
    ],
}

unsplash_map = {
    "filmschool": "photo-1485846234645",
    "industry": "photo-1492691527719",
    "tools": "photo-1620712943543",
    "niches": "photo-1551288049",
    "offers": "photo-1454165804606",
    "inspire": "photo-1536240478700",
}

all_data = {}

for category, sources in CATEGORY_SOURCES.items():
    print(f"\n{'='*60}")
    print(f"CATEGORY: {category}")
    print(f"{'='*60}")
    
    all_results = []
    
    for src in sources:
        kind = src[0]
        query = src[1]
        
        if kind == "hn":
            print(f"  [HN] Searching: {query}")
            results = get_hn_stories(query, 5)
            print(f"    Found {len(results)} results")
            all_results.extend(results)
            
        elif kind == "reddit":
            params = src[1]
            sub = params["sub"]
            q = params["q"]
            print(f"  [Reddit r/{sub}] Searching: {q}")
            results = get_reddit_stories(sub, q, 5)
            print(f"    Found {len(results)} results")
            all_results.extend(results)
            
        elif kind == "gn":
            print(f"  [Google News] Searching: {query}")
            results = get_google_news_rss(query, 5)
            print(f"    Found {len(results)} results")
            all_results.extend(results)
        
        time.sleep(0.3)
    
    # Deduplicate by title similarity
    seen_titles = set()
    unique_results = []
    for r in all_results:
        title_key = r["title"].lower().strip()[:60]
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_results.append(r)
    
    print(f"  Total unique: {len(unique_results)}")
    
    # Convert to story format
    stories = []
    for r in unique_results[:4]:
        # Clean up description
        desc = r.get("description", "")
        if not desc or len(desc) < 10:
            # Fall back: try to scrape the page for content
            pass
        desc = desc[:300] if desc else f"Latest development in AI video ({category})."
        
        # Get source from URL
        url_val = r["url"]
        domain = urlparse(url_val).netloc
        source = r.get("source", domain.replace("www.", "").split(".")[0].title())
        
        stories.append({
            "title": r["title"],
            "description": desc,
            "url": url_val,
            "source": source,
            "image_url": "",
        })
    
    all_data[category] = stories
    
    for s in stories:
        print(f"    - {s['title'][:80]}")

# Write to file
output_path = "/home/faith/tech-pulse-server/ai-video-data.json"
with open(output_path, "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"Data written to {output_path}")
total = sum(len(v) for v in all_data.values())
print(f"Total stories: {total}")
for cat, stories in all_data.items():
    print(f"  {cat}: {len(stories)} stories")
