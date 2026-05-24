#!/usr/bin/env python3
"""Fetch tech news via RSS feeds using feedparser or direct requests."""
import json, time, sys
from urllib.request import urlopen, Request
from html.parser import HTMLParser
import re

feeds = [
    # TechCrunch
    "https://techcrunch.com/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/startups/feed/",
    # Ars Technica
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    # The Verge
    "https://www.theverge.com/rss/index.xml",
    "https://www.theverge.com/ai-artificial-intelligence/rss.xml",
    # Wired
    "https://www.wired.com/feed/rss",
    "https://www.wired.com/feed/category/tech/latest",
    # HN
    "https://hnrss.org/frontpage?count=20",
    # VentureBeat
    "https://venturebeat.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    # MIT Tech Review
    "https://www.technologyreview.com/feed/",
]

def try_fetch(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urlopen(req, timeout=15)
        data = resp.read().decode('utf-8', errors='replace')
        return data
    except Exception as e:
        return None

def parse_rss_simple(xml_text):
    """Very basic RSS/Atom parser using regex."""
    items = []
    # Try to find items - both RSS <item> and Atom <entry>
    entries = re.findall(r'<(?:item|entry)>(.*?)</(?:item|entry)>', xml_text, re.DOTALL)
    for entry in entries:
        title = re.search(r'<title[^>]*>(.*?)</title>', entry, re.DOTALL)
        link = re.search(r'<link[^>]*href="([^"]+)"', entry) or re.search(r'<link>(.*?)</link>', entry, re.DOTALL)
        desc = re.search(r'<description[^>]*>(.*?)</description>', entry, re.DOTALL) or re.search(r'<summary[^>]*>(.*?)</summary>', entry, re.DOTALL)
        pubdate = re.search(r'<pubDate>(.*?)</pubDate>', entry, re.DOTALL) or re.search(r'<updated>(.*?)</updated>', entry, re.DOTALL)
        
        title_text = title.group(1).strip() if title else ""
        link_text = link.group(1).strip() if link else ""
        desc_text = desc.group(1).strip() if desc else ""
        
        # Clean HTML tags from description
        desc_text = re.sub(r'<[^>]+>', '', desc_text)
        desc_text = desc_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
        title_text = title_text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
        
        if title_text and link_text:
            items.append({
                "title": title_text,
                "description": desc_text[:300],
                "url": link_text,
                "source": link_text.split("/")[2] if link_text else "",
                "pubdate": pubdate.group(1).strip() if pubdate else ""
            })
    return items

all_items = []
seen_urls = set()

for url in feeds:
    print(f"Fetching: {url[:60]}...", file=sys.stderr)
    data = try_fetch(url)
    if data:
        items = parse_rss_simple(data)
        for item in items:
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                all_items.append(item)
        print(f"  Got {len(items)} items", file=sys.stderr)
    else:
        print(f"  Failed", file=sys.stderr)
    time.sleep(0.5)

# Save all raw items
with open("/home/faith/tech-pulse-server/rss_raw.json", "w") as f:
    json.dump(all_items, f, indent=2)

print(f"\nTotal RSS items fetched: {len(all_items)}", file=sys.stderr)

# Print top items
for item in all_items[:30]:
    print(f"  • {item['title'][:100]}")
    print(f"    {item['url'][:80]}")
