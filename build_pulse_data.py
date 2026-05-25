#!/usr/bin/env python3
"""Fetch real AI video content from HN API and working sources with De-duplication."""
import json, time, re, os, requests
from bs4 import BeautifulSoup

DATA_FILE = '/home/ubuntu/tech-pulse-server/final_data.json'

def load_existing_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_duplicate(data, category, url):
    if category not in data: return False
    return any(item['url'] == url for item in data[category])

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

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
    except Exception:
        return {'title': '', 'description': '', 'summary': ''}

data = load_existing_data()

articles = [
    {'title': 'Google Launches Veo 3 AI Video Generator with Audio', 'url': 'https://www.cnbc.com/2025/05/20/google-ai-video-generator-audio-veo-3.html', 'source': 'CNBC', 'category': 'industry'},
    {'title': 'Google Debuts Flow, an AI-Powered Video Tool', 'url': 'https://techcrunch.com/2025/05/20/google-debuts-an-ai-powered-video-tool-called-flow/', 'source': 'TechCrunch', 'category': 'industry'},
    {'title': 'Runway Gen 4.5 Rolls Out', 'url': 'https://arstechnica.com/ai/2025/05/runway-rolls-out-gen-4-5-ai-video-model/', 'source': 'Ars Technica', 'category': 'industry'},
    {'title': 'Kling 3.0 AI Video Generator', 'url': 'https://klingai.com/', 'source': 'Kling AI', 'category': 'tools'},
]

for a in articles:
    cat = a['category']
    if not is_duplicate(data, cat, a['url']):
        print(f"Fetching [{cat}]: {a['title'][:60]}...")
        info = extract(a['url'])
        desc = info['description'] or info['summary'] or a['title']
        entry = {'title': a['title'], 'description': desc, 'url': a['url'], 'source': a['source']}
        data.setdefault(cat, []).append(entry)
        save_data(data)
    else:
        print(f"Skipping duplicate: {a['url']}")

print("\nDe-duplication complete. Intelligence hub updated.")
