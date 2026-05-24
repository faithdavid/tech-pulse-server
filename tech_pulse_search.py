#!/usr/bin/env python3
"""Tech Pulse 24/7 — Search all 5 categories via DuckDuckGo."""
import json, sys, time, os, re
from ddgs import DDGS

BASE = os.path.dirname(os.path.abspath(__file__))

def ddg_search(q, max_results=10):
    try:
        with DDGS() as ddgs:
            return list(ddgs.text(q, max_results=max_results))
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return []

def clean_title(title):
    title = re.sub(r'\s+', ' ', title or '').strip()
    for suffix in [' - YouTube', ' - Reddit', ' - Medium', ' | Hacker News', ' - CNN', ' - CNBC', ' - TechCrunch', ' - The Verge', ' - Bloomberg', ' - Reuters', ' - NYTimes', ' - Ars Technica', ' - Wired', ' - Forbes', ' - BBC News', ' - The Guardian', ' - MIT Technology Review']:
        if title.endswith(suffix):
            title = title[:-len(suffix)]
    return title.strip()

def extract_source(url):
    # Extract source domain name
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    domain = re.sub(r'^www\.', '', domain)
    # Map common domains to clean names
    mapping = {
        'nytimes.com': 'The New York Times',
        'bloomberg.com': 'Bloomberg',
        'techcrunch.com': 'TechCrunch',
        'reuters.com': 'Reuters',
        'cnbc.com': 'CNBC',
        'theverge.com': 'The Verge',
        'wired.com': 'Wired',
        'arstechnica.com': 'Ars Technica',
        'forbes.com': 'Forbes',
        'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC',
        'theguardian.com': 'The Guardian',
        'mit.edu': 'MIT',
        'nature.com': 'Nature',
        'sciencedaily.com': 'ScienceDaily',
        'venturebeat.com': 'VentureBeat',
        'zdnet.com': 'ZDNet',
        'infoq.com': 'InfoQ',
        'dev.to': 'Dev.to',
        'github.com': 'GitHub',
        'huggingface.co': 'HuggingFace',
        'anthropic.com': 'Anthropic',
        'openai.com': 'OpenAI',
        'mistral.ai': 'Mistral AI',
        'google.com': 'Google',
        'blog.google': 'Google',
        'microsoft.com': 'Microsoft',
        'devblogs.microsoft.com': 'Microsoft',
        'oracle.com': 'Oracle',
        'nvidia.com': 'NVIDIA',
        'linuxfoundation.org': 'Linux Foundation',
        'crunchbase.com': 'Crunchbase News',
        'fortune.com': 'Fortune',
        'linkedin.com': 'LinkedIn',
        'news.ycombinator.com': 'Hacker News',
        'stackoverflow.com': 'Stack Overflow',
        'pytorch.org': 'PyTorch',
        'tensorflow.org': 'TensorFlow',
        'aws.amazon.com': 'AWS',
        'cloud.google.com': 'Google Cloud',
    }
    return mapping.get(domain, domain.capitalize() if domain else '')

def search_category(queries, max_per_query=8):
    combined = []
    seen_urls = set()
    for q in queries:
        results = ddg_search(q, max_results=max_per_query)
        for r in results:
            url = r.get("href", r.get("link", "")).split("?")[0].split("#")[0]
            if not url or url in seen_urls:
                continue
            # Skip social media, video sites, and shopping
            skip_domains = ['youtube.com', 'youtu.be', 'instagram.com', 'facebook.com', 'twitter.com', 
                           'tiktok.com', 'pinterest.com', 'amazon.com', 'reddit.com', 'ebay.com',
                           'wikipedia.org']
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if any(sd in domain for sd in skip_domains):
                continue
            seen_urls.add(url)
            title = clean_title(r.get("title", ""))
            snippet = r.get("body", r.get("snippet", ""))
            if title and len(title) > 10:
                combined.append({
                    "title": title,
                    "description": snippet,
                    "url": url,
                    "source": extract_source(url),
                })
        time.sleep(1.5)  # rate limit
    return combined[:6]

# Real Unsplash photo IDs for each category
UNSPLASH = {
    "ai": "https://images.unsplash.com/photo-1677442136019?w=600&q=60",
    "funding": "https://images.unsplash.com/photo-1611974789855?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1461749280684?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1519389950473?w=600&q=60",
    "oss": "https://images.unsplash.com/photo-1558494949?w=600&q=60",
}

CATEGORIES = {
    "ai": [
        "AI breakthrough new model release May 2026",
        "machine learning research advancement latest 2026",
        "large language model frontier AI news 2026",
        "AI reasoning agent autonomous capabilities 2026",
    ],
    "funding": [
        "AI startup funding round investment May 2026",
        "artificial intelligence company acquisition 2026",
        "AI unicorn valuation fundraising 2026",
        "tech startup venture capital mega round 2026",
    ],
    "tools": [
        "developer tools framework release launch 2026",
        "AI software development tool new 2026",
        "programming language IDE release update 2026",
        "infrastructure cloud DevOps tool launch 2026",
    ],
    "industry": [
        "AI regulation policy government law 2026",
        "Big Tech AI strategy Google Meta Microsoft 2026",
        "data center AI infrastructure investment 2026",
        "AI safety ethics policy news 2026",
    ],
    "oss": [
        "open source AI model release HuggingFace 2026",
        "open source software project update 2026",
        "new open source tool framework GitHub 2026",
        "open source AI library toolkit launch 2026",
    ],
}

print("=" * 60, file=sys.stderr)
print("TECH PULSE SEARCH — May 24, 2026", file=sys.stderr)
print("=" * 60, file=sys.stderr)

all_data = {}
for cat, queries in CATEGORIES.items():
    print(f"\n--- {cat.upper()} ---", file=sys.stderr)
    results = search_category(queries, max_per_query=8)
    # Add image_url
    img = UNSPLASH.get(cat, "")
    for item in results:
        item["image_url"] = img
    all_data[cat] = results
    print(f"  Got {len(results)} results", file=sys.stderr)
    for r in results[:3]:
        print(f"  • {r['title'][:80]}", file=sys.stderr)

# Write pulse-data.json
output_path = os.path.join(BASE, "pulse-data.json")
with open(output_path, "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)
print(f"\n✅ Wrote to {output_path}", file=sys.stderr)

# Print summary as JSON for parsing
print(json.dumps({k: len(v) for k, v in all_data.items()}))
