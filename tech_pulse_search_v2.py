#!/usr/bin/env python3
"""Tech Pulse 24/7 v2 — Better queries for fresher, more specific results."""
import json, sys, time, os, re
from urllib.parse import urlparse
from ddgs import DDGS

BASE = os.path.dirname(os.path.abspath(__file__))

def ddg_search(q, max_results=10):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results))
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return []

SOURCE_MAP = {
    'nytimes.com': 'The New York Times', 'bloomberg.com': 'Bloomberg',
    'techcrunch.com': 'TechCrunch', 'reuters.com': 'Reuters',
    'cnbc.com': 'CNBC', 'theverge.com': 'The Verge',
    'wired.com': 'Wired', 'arstechnica.com': 'Ars Technica',
    'forbes.com': 'Forbes', 'bbc.com': 'BBC', 'bbc.co.uk': 'BBC',
    'theguardian.com': 'The Guardian', 'venturebeat.com': 'VentureBeat',
    'zdnet.com': 'ZDNet', 'infoq.com': 'InfoQ',
    'github.com': 'GitHub', 'huggingface.co': 'HuggingFace',
    'anthropic.com': 'Anthropic', 'openai.com': 'OpenAI',
    'mistral.ai': 'Mistral AI', 'blog.google': 'Google Blog',
    'microsoft.com': 'Microsoft', 'devblogs.microsoft.com': 'Microsoft',
    'oracle.com': 'Oracle', 'nvidia.com': 'NVIDIA',
    'linuxfoundation.org': 'Linux Foundation', 'crunchbase.com': 'Crunchbase',
    'fortune.com': 'Fortune', 'sciencedaily.com': 'ScienceDaily',
    'nature.com': 'Nature', 'mit.edu': 'MIT',
    'axios.com': 'Axios', 'wsj.com': 'The Wall Street Journal',
    'ft.com': 'Financial Times', 'engadget.com': 'Engadget',
    'thenextweb.com': 'TNW', 'sdxcentral.com': 'SDxCentral',
}

def extract_source(url):
    domain = urlparse(url).netloc
    domain = re.sub(r'^www\.', '', domain)
    return SOURCE_MAP.get(domain, domain.split('.')[0].title() if domain else '')

def search_category(queries, max_per_query=8):
    combined = []
    seen_urls = set()
    skip_domains = ['youtube.com', 'youtu.be', 'instagram.com', 'facebook.com', 
                    'twitter.com', 'x.com', 'tiktok.com', 'pinterest.com', 
                    'amazon.com', 'reddit.com', 'ebay.com', 'wikipedia.org',
                    'linkedin.com']
    for q in queries:
        results = ddg_search(q, max_results=max_per_query)
        for r in results:
            url = r.get("href", r.get("link", "")).split("?")[0].split("#")[0]
            if not url or url in seen_urls:
                continue
            domain = urlparse(url).netloc
            if any(sd in domain for sd in skip_domains):
                continue
            seen_urls.add(url)
            title = re.sub(r'\s+', ' ', r.get("title", "")).strip()
            snippet = r.get("body", r.get("snippet", ""))
            if title and len(title) > 15:
                combined.append({
                    "title": title,
                    "description": snippet,
                    "url": url,
                    "source": extract_source(url),
                })
        time.sleep(1.2)
    return combined[:6]

UNSPLASH = {
    "ai": "https://images.unsplash.com/photo-1677442136019?w=600&q=60",
    "funding": "https://images.unsplash.com/photo-1611974789855?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1461749280684?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1519389950473?w=600&q=60",
    "oss": "https://images.unsplash.com/photo-1558494949?w=600&q=60",
}

CATEGORIES = {
    "ai": [
        "AI model release GPT Claude Gemini breakthrough May 2026",
        "AI research paper advancement reasoning agents latest 2026",
        "machine learning breakthrough energy efficiency benchmark 2026",
        "frontier AI model safety capability news 2026",
    ],
    "funding": [
        "AI startup funding round series billion 2026",
        "artificial intelligence company raises million funding latest 2026",
        "AI unicorn valuation acquisition deal news 2026",
        "venture capital AI investment mega round May 2026",
    ],
    "tools": [
        "developer tool framework launch release May 2026",
        "AI coding assistant tool IDE update latest 2026",
        "new programming language runtime infrastructure 2026",
        "software development kit AI integration launch 2026",
    ],
    "industry": [
        "AI regulation policy government act law 2026",
        "Big Tech Google Microsoft Meta AI strategy 2026",
        "AI data center investment chip infrastructure 2026",
        "AI safety ethics policy industry news 2026",
    ],
    "oss": [
        "open source AI model release launch 2026",
        "new open source project framework GitHub trending 2026",
        "open source AI library toolkit update 2026",
        "HuggingFace new model open source release 2026",
    ],
}

print("=" * 60, file=sys.stderr)
print("TECH PULSE SEARCH v2 — May 24, 2026", file=sys.stderr)
print("=" * 60, file=sys.stderr)

all_data = {}
for cat, queries in CATEGORIES.items():
    print(f"\n--- {cat.upper()} ---", file=sys.stderr)
    results = search_category(queries, max_per_query=8)
    img = UNSPLASH.get(cat, "")
    for item in results:
        item["image_url"] = img
    all_data[cat] = results
    print(f"  Got {len(results)} results", file=sys.stderr)
    for r in results[:3]:
        print(f"  • {r['title'][:90]}", file=sys.stderr)
        if r['source']:
            print(f"    └ {r['source']}", file=sys.stderr)

output_path = os.path.join(BASE, "pulse-data.json")
with open(output_path, "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)
print(f"\n✅ Wrote {sum(len(v) for v in all_data.values())} articles to pulse-data.json", file=sys.stderr)
