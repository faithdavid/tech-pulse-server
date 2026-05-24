#!/usr/bin/env python3
"""Fetch AI video news from multiple sources."""
import json, time, sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def fetch_hn():
    """Fetch AI video stories from Hacker News Algolia API."""
    results = []
    try:
        resp = requests.get(
            'https://hn.algolia.com/api/v1/search',
            params={'query': 'AI video', 'tags': 'story', 'hitsPerPage': 15},
            timeout=15
        )
        data = resp.json()
        for hit in data.get('hits', []):
            url = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            title = hit.get('title', '')
            if title and 'AI' in title.upper() and ('video' in title.lower() or 'film' in title.lower() or 'gen' in title.lower()):
                results.append({'title': title, 'url': url, 'source': 'HN'})
        return results
    except Exception as e:
        print(f"  HN error: {e}")
        return []

def fetch_rss_feed(url):
    """Fetch and parse an RSS/Atom feed."""
    results = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'xml')
        for item in soup.select('item') or soup.select('entry'):
            title = item.find('title')
            link = item.find('link')
            if title and link:
                href = link.get('href') or link.text.strip()
                if href and not href.startswith('http'):
                    continue
                t = title.text.strip()
                results.append({'title': t, 'url': href, 'source': url})
        return results
    except Exception as e:
        print(f"  RSS error: {e}")
        return []

# Hacker News
print("=== Hacker News AI video stories ===")
hn_stories = fetch_hn()
for s in hn_stories:
    print(f"  {s['title'][:70]}")

# Try fetching some known AI blogs directly
print("\n=== Fetching known AI video news articles ===")

def extract_article(url):
    """Get article content."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.get_text(strip=True) if soup.title else ''
        meta_desc = ''
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'description' or meta.get('property') == 'og:description':
                meta_desc = meta.get('content', '')
                break
        for tag in ['script', 'style', 'nav', 'footer', 'header', 'aside']:
            for el in soup.select(tag):
                el.decompose()
        text = soup.get_text(separator=' ', strip=True)
        import re
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = ' '.join(s for s in sentences if len(s) > 30)[:800]
        return {'title': title, 'description': meta_desc, 'summary': summary}
    except Exception as e:
        return {'title': '', 'description': '', 'summary': ''}

# Collect all known articles
articles_to_fetch = [
    {
        'title': 'Google launches Veo 3, an AI video generator that incorporates audio',
        'url': 'https://www.cnbc.com/2025/05/20/google-ai-video-generator-audio-veo-3.html',
        'category': 'industry',
        'source': 'CNBC'
    },
    {
        'title': 'Google debuts an AI-powered video tool called Flow',
        'url': 'https://techcrunch.com/2025/05/20/google-debuts-an-ai-powered-video-tool-called-flow/',
        'category': 'industry',
        'source': 'TechCrunch'
    },
    {
        'title': 'Text-to-video AI blossoms with new metamorphic video capabilities',
        'url': 'https://www.sciencedaily.com/releases/2025/05/250505170633.htm',
        'category': 'filmschool',
        'source': 'ScienceDaily'
    },
    {
        'title': 'Top 10 AI Video Tools (2025 Edition)',
        'url': 'https://creativepool.com/magazine/features/top-10-ai-video-tools-2025-edition.33137',
        'category': 'tools',
        'source': 'Creativepool'
    },
    {
        'title': 'Runway Gen-4: AI Video Generation with World Consistency',
        'url': 'https://runwayml.com/gen-4',
        'category': 'tools',
        'source': 'Runway'
    },
    {
        'title': 'Runway rolls out Gen 4.5 AI video model that beats Google, OpenAI',
        'url': 'https://arstechnica.com/ai/2025/05/runway-rolls-out-gen-4-5-ai-video-model/',
        'category': 'industry',
        'source': 'Ars Technica'
    },
    {
        'title': 'Kling 3.0 - The Most Advanced AI Video Model with Native Audio',
        'url': 'https://klingai.com/',
        'category': 'tools',
        'source': 'Kling'
    },
    {
        'title': 'AI Video Creation Just Leveled Up: What\'s New in May 2025?',
        'url': 'https://ithy.com/article/ai-video-creation-news-may-2025-w0irorw4',
        'category': 'industry',
        'source': 'Ithy'
    },
]

# Fetch all articles
for article in articles_to_fetch:
    print(f"  Fetching: {article['title'][:60]}...")
    time.sleep(0.5)
    extra = extract_article(article['url'])
    article['page_title'] = extra['title']
    article['description'] = extra['description']
    article['summary'] = extra['summary']
    print(f"    OK ({len(extra['summary'])} chars)")

# Also search for more specific stories using available data
# Let's also try HN API for more results
print("\n=== More HN results ===")
try:
    resp = requests.get(
        'https://hn.algolia.com/api/v1/search',
        params={'query': 'Runway OR "Veo 3" OR "Kling" OR "Pika" AI video', 'tags': 'story', 'hitsPerPage': 20},
        timeout=15
    )
    data = resp.json()
    for hit in data.get('hits', []):
        url = hit.get('url') or ''
        title = hit.get('title', '')
        if title and url:
            print(f"  {title[:70]}")
            articles_to_fetch.append({
                'title': title,
                'url': url,
                'category': 'industry',
                'source': 'HN',
                'page_title': title,
                'description': '',
                'summary': ''
            })
except Exception as e:
    print(f"  HN batch error: {e}")

# Save all fetched data
output = {
    'articles': articles_to_fetch,
    'hn_stories': hn_stories
}

with open('/home/faith/tech-pulse-server/all_articles.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nTotal articles: {len(articles_to_fetch)}")
print("Done!")
