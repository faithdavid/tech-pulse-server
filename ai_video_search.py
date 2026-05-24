#!/usr/bin/env python3
"""AI Video Pulse search script - fetches intelligence via DuckDuckGo and article extraction."""

import urllib.request, urllib.parse, json, re, html, time, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

def ddg_search(query):
    """Search DuckDuckGo lite and return list of (title, url) results."""
    params = urllib.parse.urlencode({'q': query})
    url = f"https://lite.duckduckgo.com/lite/?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ssl_ctx)
        data = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  DDG search failed: {e}")
        return []
    
    # Extract result links
    results = []
    # Find all <a> tags with href containing uddg
    for m in re.finditer(r'<a[^>]*href="([^"]*uddg=([^"&]+))"[^>]*>([^<]*)</a>', data):
        href = m.group(1)
        title = html.unescape(m.group(3)).strip()
        if title and href:
            # Decode the uddg parameter
            uddg_match = re.search(r'uddg=([^&]+)', href)
            if uddg_match:
                actual_url = urllib.parse.unquote(uddg_match.group(1))
                results.append((title, actual_url))
        if len(results) >= 8:
            break
    return results

def extract_text(url):
    """Try to extract readable text from a URL."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ssl_ctx)
        data = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None
    
    # Remove scripts and styles
    data = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.DOTALL)
    data = re.sub(r'<style[^>]*>.*?</style>', '', data, flags=re.DOTALL)
    
    # Extract text from paragraphs and headings
    texts = []
    for tag in ['h1', 'h2', 'h3', 'h4', 'p', 'li']:
        for m in re.finditer(f'<{tag}[^>]*>(.*?)</{tag}>', data, re.DOTALL):
            text = re.sub(r'<[^>]+>', '', m.group(1))
            text = html.unescape(text).strip()
            if len(text) > 30:
                texts.append(text)
    
    return '\n'.join(texts[:50]) if texts else None

# Phase 1 queries
queries = {
    'filmschool': [
        'AI filmmaking techniques 2025 new tools workflow',
        'AI video creation tips tutorial 2025',
        'generative AI film production techniques 2025'
    ],
    'industry': [
        'Veo 3 Google AI video generator 2025',
        'Runway Gen-4 AI video platform 2025',
        'AI video platform launch update 2025'
    ],
    'tools': [
        'new AI video generator editor release May 2025',
        'Pika Labs AI video new features 2025',
        'Kling MiniMax Sora AI video tool 2025'
    ],
    'niches': [
        'AI video trends styles emerging 2025',
        'AI generated video art style 2025',
        'AI video advertising marketing trends 2025'
    ],
    'offers': [
        'AI video freelance pricing Upwork 2025',
        'AI video production client rates 2025',
        'AI filmmaker business strategy 2025'
    ],
    'inspire': [
        'notable AI generated film 2025 award',
        'AI film festival winner 2025',
        'AI video creator viral 2025'
    ]
}

results = {}
for category, qlist in queries.items():
    print(f"\n=== Phase 1: {category.upper()} ===")
    cat_results = []
    seen_urls = set()
    for q in qlist:
        print(f"  Searching: {q[:60]}...")
        res = ddg_search(q)
        for title, url in res:
            if url not in seen_urls and len(seen_urls) < 15:
                seen_urls.add(url)
                cat_results.append({'title': title, 'url': url})
                print(f"    [{len(cat_results)}] {title[:70]}")
        time.sleep(0.5)
    results[category] = cat_results

# Save raw results
with open('/home/faith/tech-pulse-server/raw_search_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n\n=== Phase 2: Deep-dive extraction ===")
# For each category, try to extract content from top results
deep_results = {}
for category, items in results.items():
    print(f"\n--- {category} ---")
    deep = []
    for item in items[:5]:
        url = item['url']
        print(f"  Extracting: {item['title'][:60]}...")
        text = extract_text(url)
        if text:
            # Get first 800 chars as summary
            summary = text[:800]
            deep.append({'title': item['title'], 'url': url, 'summary': summary})
            print(f"    Got {len(text)} chars")
        else:
            print(f"    Failed to extract")
        time.sleep(0.5)
    deep_results[category] = deep

with open('/home/faith/tech-pulse-server/deep_results.json', 'w') as f:
    json.dump(deep_results, f, indent=2)

print("\nDone! Raw results saved.")
