#!/usr/bin/env python3
"""AI Video Pulse - using googlesearch library + direct news sources."""

import json, time, re, os
import requests
from bs4 import BeautifulSoup
from googlesearch import search

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def google_search(query, num=10):
    """Search using googlesearch library."""
    results = []
    try:
        for url in search(query, num_results=num, sleep_interval=1, timeout=10):
            results.append(url)
        return results
    except Exception as e:
        print(f"    Google search error: {e}")
        return []

def extract_page_info(url):
    """Extract title and description from a page."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        title = soup.title.get_text(strip=True) if soup.title else ''
        # Get meta description
        desc = ''
        meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta:
            desc = meta.get('content', '')
        # Clean text for summary
        for tag in ['script', 'style', 'nav', 'footer', 'header', 'aside']:
            for el in soup.select(tag):
                el.decompose()
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = ''
        for s in sentences:
            if len(s) > 30 and len(summary) < 600:
                summary += s + ' '
        return {
            'title': title or url,
            'description': desc or summary[:300] if summary else '',
            'summary': summary[:1000] if summary else '',
        }
    except Exception as e:
        return {'title': url, 'description': '', 'summary': ''}

def search_cached_urls():
    """Use known news sources directly."""
    # Known articles from earlier curl results
    known_articles = {
        'cnbc_veo3': {
            'title': 'Google launches Veo 3, an AI video generator that incorporates audio',
            'url': 'https://www.cnbc.com/2025/05/20/google-ai-video-generator-audio-veo-3.html',
        },
        'techcrunch_flow': {
            'title': 'Google debuts an AI-powered video tool called Flow',
            'url': 'https://techcrunch.com/2025/05/20/google-debuts-an-ai-powered-video-tool-called-flow/',
        },
        'sciencedaily_metamorphic': {
            'title': 'Text-to-video AI blossoms with new metamorphic video capabilities',
            'url': 'https://www.sciencedaily.com/releases/2025/05/250505170633.htm',
        },
        'ithy_levelup': {
            'title': 'AI Video Creation Just Leveled Up: What\'s New in May 2025?',
            'url': 'https://ithy.com/article/ai-video-creation-news-may-2025-w0irorw4',
        },
        'creativepool_top10': {
            'title': 'Top 10 AI Video Tools (2025 Edition)',
            'url': 'https://creativepool.com/magazine/features/top-10-ai-video-tools-2025-edition.33137',
        },
        'runway_gen4': {
            'title': 'Runway Gen-4: AI Video Generation with World Consistency',
            'url': 'https://runwayml.com/gen-4',
        },
        'runway_gen45': {
            'title': 'Runway rolls out Gen 4.5 AI video model that beats Google, OpenAI',
            'url': 'https://arstechnica.com/ai/2025/05/runway-rolls-out-gen-4-5-ai-video-model/',
        },
        'kling30': {
            'title': 'Kling 3.0 - The Most Advanced AI Video Model',
            'url': 'https://klingai.com/',
        },
    }
    return known_articles

# Direct fetch from known sources
print("=== Fetching known AI video news sources ===")
known = search_cached_urls()
articles = []
for key, info in known.items():
    print(f"  Fetching: {info['title'][:60]}...")
    time.sleep(1)
    extra = extract_page_info(info['url'])
    articles.append({
        'key': key,
        'title': info['title'],
        'url': info['url'],
        'page_title': extra['title'],
        'description': extra['description'],
        'summary': extra['summary'],
    })
    print(f"    Got: {len(extra.get('summary', ''))} chars")

# Also search for specific topics using Google
print("\n\n=== Google searches for specific categories ===")
search_queries = {
    'filmschool': [
        'AI filmmaking techniques workflow 2025',
        'AI video production tutorial cinema 2025',
    ],
    'industry': [
        'Google Veo 3 AI video generator 2025',
        'Runway Gen-4 AI video platform latest 2025',
        'Sora OpenAI video generation 2025',
    ],
    'tools': [
        'Pika Labs AI video new features 2025',
        'Kling AI video generator 3.0 2025',
        'best AI video editor 2025',
    ],
    'niches': [
        'AI video trends 2025 emerging styles',
        'AI generated video advertising 2025',
    ],
    'offers': [
        'AI video freelance pricing 2025',
        'AI filmmaking business strategy 2025',
    ],
    'inspire': [
        'AI generated short film award 2025',
        'AI film festival winner 2025',
    ]
}

search_results = {}
for category, qlist in search_queries.items():
    print(f"\n--- {category} ---")
    cat_urls = []
    for q in qlist:
        print(f"  Google: {q[:60]}...")
        urls = google_search(q, num=5)
        for url in urls:
            cat_urls.append(url)
        time.sleep(1)
    # Deduplicate and extract info
    seen = set()
    for url in cat_urls:
        if url not in seen:
            seen.add(url)
            time.sleep(0.5)
            info = extract_page_info(url)
            search_results.setdefault(category, []).append({
                'url': url,
                'title': info['title'],
                'description': info['description'],
                'summary': info['summary'],
            })
            print(f"    {info['title'][:70]}")

combined = {
    'known_articles': articles,
    'search_results': search_results,
}

with open('/home/faith/tech-pulse-server/all_fetched.json', 'w') as f:
    json.dump(combined, f, indent=2)

print("\nDone!")
