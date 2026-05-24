#!/usr/bin/env python3
"""Fetch HN stories with date filtering + current tech news"""
import json
import sys
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

def fetch_json(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)',
        'Accept': 'application/json'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except:
        return None

def fetch_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Accept': 'text/html,*/*'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            encoding = resp.headers.get_content_charset() or 'utf-8'
            return data.decode(encoding, errors='replace')
    except:
        return None

def extract_title_desc(html):
    title = ""
    desc = ""
    if not html: return title, desc
    m = re.search(r'<meta[^>]*property=["\']og:title["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m: title = m.group(1).strip()
    if not title:
        m = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
        if m: title = re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m: desc = m.group(1).strip()
    if not desc:
        m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
        if m: desc = m.group(1).strip()
    return title, desc

# Get current time for date filtering
now = datetime.now(timezone.utc)

# Fetch HN front page (current stories)
print("=== HN Front Page (firebase API) ===", file=sys.stderr)
hn_firebase = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
if hn_firebase:
    story_ids = hn_firebase[:30]  # Top 30
    hn_stories = []
    for sid in story_ids:
        story = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if story and story.get("title") and story.get("time"):
            hn_stories.append({
                "title": story.get("title", ""),
                "url": story.get("url", ""),
                "points": story.get("score", 0),
                "by": story.get("by", ""),
                "time": story.get("time", 0)
            })
    
    # Sort by points descending
    hn_stories.sort(key=lambda x: x["points"], reverse=True)
    
    for s in hn_stories[:15]:
        print(f"  [{s['points']}] {s['title'][:80]}", file=sys.stderr)

# Also fetch HN Algolia with time filter
print("\n=== HN Algolia (past week, points>20) ===", file=sys.stderr)
# Unix timestamp for 7 days ago
one_week_ago = int((now - timedelta(days=7)).timestamp())
algolia_url = f"https://hn.algolia.com/api/v1/search?hitsPerPage=40&tags=story&numericFilters=points>20,created_at_i>{one_week_ago}"
algolia_data = fetch_json(algolia_url)
if algolia_data and "hits" in algolia_data:
    for h in algolia_data["hits"]:
        url = h.get("url", "") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
        print(f"  [{h.get('points',0)}] {h.get('title','')[:80]}", file=sys.stderr)
        print(f"      {url}", file=sys.stderr)

print("\n=== DONE ===", file=sys.stderr)
