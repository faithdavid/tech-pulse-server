#!/usr/bin/env python3
"""AI Video Pulse search v2 — requests + BeautifulSoup"""
import requests, json, re, html, time, sys, urllib.parse
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
})

def search_ddg(query, max_results=5):
    """Search DuckDuckGo via HTML"""
    url = 'https://html.duckduckgo.com/html/'
    try:
        resp = session.post(url, data={'q': query}, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        return [{'error': str(e)}]
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    results = []
    for result in soup.select('.result')[:max_results]:
        a_tag = result.select_one('.result__a')
        snippet_tag = result.select_one('.result__snippet')
        if a_tag:
            raw_url = a_tag.get('href', '')
            real_url_m = re.search(r'uddg=(https?%3A[^&]+)', raw_url)
            real_url = urllib.parse.unquote(real_url_m.group(1)) if real_url_m else raw_url
            title = a_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''
            results.append({'title': title, 'url': real_url, 'snippet': snippet})
    return results

def fetch_page(url, timeout=10):
    """Fetch and parse a page"""
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        return {'error': str(e)}
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    title = soup.title.get_text(strip=True) if soup.title else ''
    
    # Meta description
    desc = ''
    meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if meta: desc = meta.get('content', '')
    
    # Get meaningful paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 60:
            paragraphs.append(text)
    
    return {'title': title, 'description': desc, 'paragraphs': paragraphs[:15], 'url': url}

# Try DuckDuckGo with requests session
print("=== Testing DuckDuckGo search ===")
res = search_ddg('AI video generation 2026', 3)
for r in res:
    print(json.dumps(r, ensure_ascii=False)[:300])
print()

# Let's try different search approaches
# Try direct scrape of known news sources
sources = [
    ('TechCrunch AI', 'https://techcrunch.com/category/artificial-intelligence/'),
    ('The Verge AI', 'https://www.theverge.com/ai-artificial-intelligence'),
    ('VentureBeat AI', 'https://venturebeat.com/category/ai/'),
]

for name, url in sources:
    print(f"\n=== {name} ===")
    page = fetch_page(url, timeout=15)
    if 'error' in page:
        print(f"  ERROR: {page['error']}")
        continue
    print(f"  TITLE: {page['title'][:80]}")
    print(f"  DESC: {page['description'][:200]}")
    # Find article links
    soup = BeautifulSoup(requests.get(url, timeout=15, headers=session.headers).text, 'html.parser')
    articles = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if len(text) > 30 and ('ai' in href.lower() or 'video' in href.lower() or 'sora' in href.lower() or 'runway' in href.lower()):
            articles.append({'title': text, 'url': href if href.startswith('http') else urllib.parse.urljoin(url, href)})
    for art in articles[:5]:
        print(f"  ARTICLE: {art['title'][:80]}")
        print(f"    URL: {art['url'][:100]}")
