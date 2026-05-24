#!/usr/bin/env python3
"""AI Video Pulse - using duckduckgo_search library."""

import json, time, re, os
from duckduckgo_search import DDGS

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def search_ddg(query, max_results=8):
    """Search using DuckDuckGo Python library."""
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                title = r.get('title', '')
                href = r.get('href', '')
                body = r.get('body', '')
                if title and href:
                    results.append({
                        'title': title,
                        'url': href,
                        'snippet': body
                    })
            return results
    except Exception as e:
        print(f"    DDG error: {e}")
        return []

def extract_text_simple(url):
    """Extract text using requests + bs4."""
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in ['script', 'style', 'nav', 'footer', 'header', 'aside']:
            for el in soup.select(tag):
                el.decompose()
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = ''
        for s in sentences:
            if len(s) > 30 and len(summary) < 800:
                summary += s + ' '
        return summary.strip() if len(summary) > 50 else None
    except Exception as e:
        return None

# Phase 1 queries
queries = {
    'filmschool': [
        'AI filmmaking techniques workflow cinema 2025',
        'AI video production storytelling tutorial 2025',
        'generative AI film direction cinematography 2025',
    ],
    'industry': [
        'Google Veo 3 AI video generator audio 2025',
        'Runway Gen-4 AI video platform 2025',
        'Pika Labs AI video features update 2025',
        'Kling AI video generator MiniMax 2025',
    ],
    'tools': [
        'new AI video editor generator release 2025',
        'Sora OpenAI video generation update 2025',
        'best AI video tools comparison 2025',
    ],
    'niches': [
        'AI video style trends emerging 2025',
        'AI generated video advertising marketing 2025',
        'AI short form video content creation trends 2025',
    ],
    'offers': [
        'AI video freelance pricing rates 2025',
        'Upwork AI video freelancer tips 2025',
        'AI video production business strategy selling 2025',
    ],
    'inspire': [
        'notable AI generated short film 2025 award',
        'AI film festival winners Runway 2025',
        'viral AI video creator artist breakthrough 2025',
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
        results = search_ddg(q, max_results=10)
        for r in results:
            if r['url'] not in seen:
                seen.add(r['url'])
                cat_results.append(r)
                print(f"    [{len(cat_results)}] {r['title'][:70]}")
    all_results[category] = cat_results

with open('/home/faith/tech-pulse-server/raw_search_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)

# Phase 2: deep-dive
print("\n\n=== Phase 2: Deep-dive extraction ===")
deep_results = {}
for category, items in all_results.items():
    print(f"\n--- {category} ---")
    deep = []
    for item in items[:6]:
        url = item['url']
        print(f"  Extracting: {item['title'][:60]}...")
        time.sleep(0.5)
        text = extract_text_simple(url)
        if text:
            summary = text[:1000]
            deep.append({
                'title': item['title'],
                'url': url,
                'snippet': item.get('snippet', ''),
                'summary': summary
            })
            print(f"    Got {len(text)} chars")
        else:
            print(f"    Failed, using snippet only")
            deep.append({
                'title': item['title'],
                'url': url,
                'snippet': item.get('snippet', ''),
                'summary': item.get('snippet', '')
            })
    deep_results[category] = deep

with open('/home/faith/tech-pulse-server/deep_results.json', 'w') as f:
    json.dump(deep_results, f, indent=2)

print("\nDone!")
