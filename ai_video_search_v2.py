#!/usr/bin/env python3
"""AI Video Pulse - comprehensive search and data collection script."""

import json, re, time, os, sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

session = requests.Session()
session.headers.update(HEADERS)

def bing_search(query, max_results=8):
    """Search Bing and return (title, url) pairs."""
    url = f"https://www.bing.com/search?q={requests.utils.quote(query)}&count=15"
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        if 'captcha' in resp.text.lower() or 'verify' in resp.text.lower():
            print(f"    Bing: CAPTCHA blocked")
            return []
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for li in soup.select('#b_results > li.b_algo'):
            h2 = li.select_one('h2 a')
            if h2:
                title = h2.get_text(strip=True)
                href = h2.get('href', '')
                if title and href and href.startswith('http'):
                    results.append((title, href))
        return results[:max_results]
    except Exception as e:
        print(f"    Bing search error: {e}")
        return []

def google_search(query, max_results=8):
    """Search Google and return (title, url) pairs."""
    url = f"https://www.google.com/search?q={requests.utils.quote(query)}&num=15"
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        results = []
        for g in soup.select('div.g'):
            a = g.select_one('a[href^="http"]')
            h3 = g.select_one('h3')
            if a and h3:
                title = h3.get_text(strip=True)
                href = a.get('href', '')
                if href.startswith('/url?q='):
                    href = href.split('/url?q=')[1].split('&')[0]
                if title and href.startswith('http'):
                    results.append((title, href))
        return results[:max_results]
    except Exception as e:
        print(f"    Google search error: {e}")
        return []

def extract_page_text(url):
    """Extract readable text from a page."""
    try:
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in ['script', 'style', 'nav', 'footer', 'header']:
            for el in soup.select(tag):
                el.decompose()
        text = soup.get_text(separator=' ', strip=True)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Build summary from first meaningful sentences
        summary = ''
        for s in sentences:
            if len(s) > 30 and len(summary) < 600:
                summary += s + ' '
        return summary.strip()
    except Exception as e:
        return None

# Phase 1: Search all categories
queries = {
    'filmschool': [
        'AI filmmaking techniques tutorial 2025',
        'AI video production workflow cinema 2025',
        'generative AI film direction storytelling 2025',
    ],
    'industry': [
        'Veo 3 Google AI video generator audio 2025',
        'Runway Gen-4 AI video platform update 2025',
        'Pika Labs AI video new features 2025',
    ],
    'tools': [
        'new AI video generator editor launch 2025',
        'Kling AI video MiniMax Sora update 2025',
        'best AI video tools comparison 2025',
    ],
    'niches': [
        'AI video trends emerging styles 2025',
        'AI generated video art advertising 2025',
        'AI short form video content creation 2025',
    ],
    'offers': [
        'AI video freelance pricing rates 2025',
        'Upwork AI filmmaker gig strategy 2025',
        'AI video production business selling 2025',
    ],
    'inspire': [
        'notable AI generated short film 2025 award',
        'Runway AI film festival winners 2025',
        'viral AI video creator artist 2025',
    ]
}

all_results = {}
for category, qlist in queries.items():
    print(f"\n=== {category.upper()} ===")
    cat_results = []
    seen = set()
    for q in qlist:
        print(f"  Query: {q[:60]}...")
        time.sleep(1)
        results = bing_search(q)
        if not results:
            results = google_search(q)
        for title, url in results:
            if url not in seen:
                seen.add(url)
                cat_results.append({'title': title, 'url': url})
                print(f"    [{len(cat_results)}] {title[:70]}")
    all_results[category] = cat_results

with open('/home/faith/tech-pulse-server/raw_search_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)

# Phase 2: Deep-dive extraction
print("\n\n=== Phase 2: Deep-dive ===")
deep_results = {}
for category, items in all_results.items():
    print(f"\n--- {category} ---")
    deep = []
    for item in items[:6]:
        url = item['url']
        print(f"  Extracting: {item['title'][:60]}...")
        time.sleep(0.5)
        text = extract_page_text(url)
        if text and len(text) > 50:
            # Get first 1000 chars as summary
            summary = text[:1000]
            deep.append({'title': item['title'], 'url': url, 'summary': summary})
            print(f"    Got {len(text)} chars")
        else:
            print(f"    Failed/skipped")
    deep_results[category] = deep

with open('/home/faith/tech-pulse-server/deep_results.json', 'w') as f:
    json.dump(deep_results, f, indent=2)

print("\nDone!")
