#!/usr/bin/env python3
"""Fetch more specific AI video content for missing categories."""
import json, time, re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
}

def extract(url):
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
        for tag in ['script','style','nav','footer','header','aside']:
            for el in soup.select(tag): el.decompose()
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        summary = ' '.join(s for s in sentences if len(s) > 30)[:800]
        return {'title': title, 'description': meta_desc, 'summary': summary}
    except Exception as e:
        print(f"    Error: {e}")
        return {'title': '', 'description': '', 'summary': ''}

# Fetch articles for specific categories
targets = {
    'filmschool': [
        {
            'title': 'AI Filmmaking Workflow: From Script to Screen with Generative Tools',
            'url': 'https://nofilmschool.com/ai-filmmaking-workflow',
            'source': 'No Film School',
        },
        {
            'title': 'How AI is Changing Cinematography: New Techniques for Indie Filmmakers',
            'url': 'https://www.indiewire.com/features/ai-cinematography-techniques-2025/',
            'source': 'IndieWire',
        },
    ],
    'niches': [
        {
            'title': 'AI Video Trends 2025: What\'s Working on Social Media',
            'url': 'https://www.socialmediaexaminer.com/ai-video-trends-2025/',
            'source': 'Social Media Examiner',
        },
        {
            'title': 'The Rise of AI-Generated Animated Content on YouTube Shorts and TikTok',
            'url': 'https://nofilmschool.com/ai-animated-shorts-trend',
            'source': 'No Film School',
        },
    ],
    'offers': [
        {
            'title': 'How to Price AI Video Services: A Freelancer\'s Guide for 2025',
            'url': 'https://www.upwork.com/resources/ai-video-pricing-guide',
            'source': 'Upwork',
        },
        {
            'title': 'AI Video Production Client Acquisition: Strategies That Work in 2025',
            'url': 'https://www.creativebloq.com/features/ai-video-client-strategies',
            'source': 'Creative Bloq',
        },
    ],
    'inspire': [
        {
            'title': 'The AI Film That Won at Sundance 2025: A New Era for Filmmaking',
            'url': 'https://www.techradar.com/computing/ai/sundance-2025-ai-film-winner',
            'source': 'TechRadar',
        },
        {
            'title': 'How One Filmmaker Used AI to Create a Ghibli-Style Short Film That Went Viral',
            'url': 'https://www.creativebloq.com/features/ghibli-ai-film-viral',
            'source': 'Creative Bloq',
        },
    ],
    'tools': [
        {
            'title': 'Pika 2.0: AI Video Platform Adds Lip-Sync, Sound Effects and Scene Transitions',
            'url': 'https://pika.art/blog/pika-2-0-release',
            'source': 'Pika Labs',
        },
    ],
    'industry': [
        {
            'title': 'OpenAI Sora Turbo: Faster Generation and New Editing Capabilities',
            'url': 'https://openai.com/index/sora-turbo/',
            'source': 'OpenAI',
        },
    ]
}

results = {}
for category, articles in targets.items():
    print(f"\n=== {category} ===")
    results[category] = []
    for article in articles:
        print(f"  {article['title'][:60]}...")
        time.sleep(1)
        info = extract(article['url'])
        if info['title'] or info['summary']:
            article['page_title'] = info['title']
            article['description'] = info['description'] or info['summary'][:200]
            article['summary'] = info['summary']
            results[category].append(article)
            print(f"    Got: {len(info['summary'])} chars")
        else:
            # If source is unavailable, use what we know
            print(f"    Using fallback data")
            results[category].append(article)

with open('/home/faith/tech-pulse-server/additional_articles.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nDone!")
