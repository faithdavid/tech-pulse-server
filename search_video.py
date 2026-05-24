#!/usr/bin/env python3
"""AI Video Pulse search — uses DuckDuckGo HTML search + direct page fetching"""
import urllib.request, urllib.parse, json, re, html, ssl, time, sys

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def search_ddg(query, max_results=5):
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    try:
        with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
            text = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return [{'error': str(e)}]
    
    results = []
    blocks = re.split(r'<div class=\"result results_links[^\"]*\">', text)
    for block in blocks[1:max_results+1]:
        url_m = re.search(r'<a rel=\"nofollow\" class=\"result__a\" href=\"(.*?)\"', block)
        title_m = re.search(r'class=\"result__a\".*?>(.*?)</a>', block, re.DOTALL)
        snippet_m = re.search(r'class=\"result__snippet[^\"]*\".*?>(.*?)</(?:a|span|div)', block, re.DOTALL)
        if url_m and title_m:
            raw_url = html.unescape(url_m.group(1))
            real_url_m = re.search(r'uddg=(https?%3A[^&]+)', raw_url)
            real_url = urllib.parse.unquote(real_url_m.group(1)) if real_url_m else raw_url
            results.append({
                'title': html.unescape(re.sub(r'<[^>]+>', '', title_m.group(1))).strip(),
                'url': real_url,
                'snippet': html.unescape(re.sub(r'<[^>]+>', '', snippet_m.group(1))).strip() if snippet_m else ''
            })
    return results

def fetch_page_text(url, timeout=10):
    """Fetch a page and extract readable text"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            text = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f"ERR: {e}"
    
    # Extract title
    title = ""
    tm = re.search(r'<title>(.*?)</title>', text, re.DOTALL)
    if tm: title = html.unescape(re.sub(r'<[^>]+>', '', tm.group(1))).strip()
    
    # Extract meta description
    desc = ""
    dm = re.search(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']', text)
    if dm: desc = html.unescape(dm.group(1)).strip()
    
    # Extract paragraphs
    paras = []
    for p in re.findall(r'<p[^>]*>(.*?)</p>', text, re.DOTALL):
        clean = html.unescape(re.sub(r'<[^>]+>', '', p)).strip()
        if len(clean) > 40:
            paras.append(clean)
    
    return {'title': title, 'description': desc, 'paragraphs': paras[:10]}

# === SEARCH ALL CATEGORIES ===
all_categories = {
    'filmschool': [
        'AI video filmmaking complete hybrid workflow guide 2026',
        'AI video creation tutorial learning best practices 2026',
        'site:youtube.com AI filmmaking workflow tutorial 2026'
    ],
    'industry': [
        'Sora OpenAI video generation update May 2026',
        'Runway Gen-4 AI video model release features 2026',
        'AI video generation market news milestone 2026'
    ],
    'tools': [
        'Pika Kling HailuoAI video tool update launch 2026',
        'ElevenLabs video AI new tool release 2026',
        'Synthesia Runway AI video software 2026'
    ],
    'niches': [
        'AI video content creator niche profitable 2026',
        'AI video marketing advertising trend 2026',
        'AI generated video demand industry 2026'
    ],
    'offers': [
        'sell AI video production service freelance 2026',
        'AI video monetization creator economy 2026',
        'AI video agency pricing model 2026'
    ],
    'inspire': [
        'AI generated short film award festival winner 2026',
        'best AI video viral creative 2026',
        'AI filmmaking breakthrough cinematic 2026'
    ]
}

all_results = {}
for cat, queries in all_categories.items():
    cat_results = []
    for q in queries:
        res = search_ddg(q)
        for r in res:
            if 'error' not in r and r not in cat_results:
                cat_results.append(r)
        time.sleep(0.5)
    all_results[cat] = cat_results
    print(f"\n=== {cat.upper()} ({len(cat_results)} results) ===")
    for r in cat_results[:4]:
        print(f"  TITLE: {r['title'][:100]}")
        print(f"  SNIPPET: {r['snippet'][:200]}")
        print(f"  URL: {r['url'][:100]}")
        print()

# Try to fetch a few pages for details
print("\n\n=== FETCHING DETAILS ===")
fetch_urls = []
for cat, items in all_results.items():
    for item in items[:2]:
        fetch_urls.append((cat, item['url'], item['title']))

for cat, url, title in fetch_urls[:6]:
    print(f"\n--- {cat}: {title[:60]} ---")
    page = fetch_page_text(url)
    if isinstance(page, dict):
        print(f"  DESC: {page['description'][:300]}")
        for p in page['paragraphs'][:3]:
            print(f"  P: {p[:200]}")
    else:
        print(f"  {page}")
    time.sleep(1)
