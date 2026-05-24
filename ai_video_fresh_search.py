#!/usr/bin/env python3
"""AI Video Pulse Fresh Search - Phase 1 research via DuckDuckGo."""
import json, time, re, sys, random
from duckduckgo_search import DDGS

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

def search_ddg(query, max_results=8):
    try:
        with DDGS() as ddgs:
            results = []
            for r in ddgs.text(query, max_results=max_results):
                title = r.get('title', '')
                href = r.get('href', '')
                body = r.get('body', '')
                if title and href and title.strip():
                    results.append({'title': title, 'url': href, 'snippet': body})
            return results
    except Exception as e:
        print(f"    DDG error: {e}", file=sys.stderr)
        return []

def extract_text_simple(url):
    import requests
    from bs4 import BeautifulSoup
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
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
            if len(s) > 30 and len(summary) < 900:
                summary += s + ' '
        return summary.strip() if len(summary) > 80 else None
    except:
        return None

# Fresh 2026 queries
queries = {
    'filmschool': [
        'AI filmmaking techniques workflow cinema 2026',
        'AI video storytelling cinematography tutorial 2026',
        'generative AI film production pipeline 2026',
        'AI film school training program 2026',
    ],
    'industry': [
        'Runway Gen-4 Kling Google Veo AI video news May 2026',
        'AI video generation company platform update 2026',
        'OpenAI video AI startup funding 2026',
        'AI video advertising platform launch 2026',
    ],
    'tools': [
        'new AI video generator editor release May 2026',
        'Pika Labs Dreamina Kling AI video tool update 2026',
        'open source AI video model 2026',
        'AI video editing software features 2026',
    ],
    'niches': [
        'AI video social media marketing trends 2026',
        'AI generated video content demand niches 2026',
        'AI short form video platform trends 2026',
        'AI video art style emerging 2026',
    ],
    'offers': [
        'AI video freelancing income pricing 2026',
        'sell AI video services monetization strategy 2026',
        'AI video creator business opportunities 2026',
    ],
    'inspire': [
        'AI generated film festival winner showcase 2026',
        'viral AI video project creative breakthrough 2026',
        'AI film director notable project 2026',
        'AI video art exhibition gallery 2026',
    ]
}

# Unsplash photo IDs for visual variety
unsplash_ids = {
    'filmschool': [
        '1485846234645',
        '1523050854058-8df90110c7f1',
        '1536240478700-b869070f9279',
        '1478720568477-152d9b164e26',
    ],
    'industry': [
        '1611974789855-9c2a0a7236a3',
        '1519389950473-47ba0277781c',
        '1460925895917-afdab827c52f',
        '1551288049-bebda4e38f71',
    ],
    'tools': [
        '1558494949-ef010cbdcc31',
        '1461749280684-dccba630e2f6',
        '1518770660439-4636190af475',
        '1558618666-fcd25c85f82e',
    ],
    'niches': [
        '1558618666-fcd25c85f82e',
        '1551288049-bebda4e38f71',
        '1519389950473-47ba0277781c',
        '1460925895917-afdab827c52f',
    ],
    'offers': [
        '1554224155-8d04cb21cd6c',
        '1454165804606-c3d57bc86b40',
        '1460925895917-afdab827c52f',
        '1551288049-bebda4e38f71',
    ],
    'inspire': [
        '1478720568477-152d9b164e26',
        '1487180144351-b8472da7d491',
        '1492691527719-9d1e07e534b4',
        '1536240478700-b869070f9279',
    ]
}

def guess_source(url):
    """Extract source name from URL."""
    from urllib.parse import urlparse
    netloc = urlparse(url).netloc
    domain = netloc.replace('www.', '')
    # Map common domains
    mapping = {
        'youtube.com': 'YouTube',
        'techcrunch.com': 'TechCrunch',
        'theverge.com': 'The Verge',
        'venturebeat.com': 'VentureBeat',
        'reuters.com': 'Reuters',
        'variety.com': 'Variety',
        'hollywoodreporter.com': 'The Hollywood Reporter',
        'deadline.com': 'Deadline',
        'bloomberg.com': 'Bloomberg',
        '9to5mac.com': '9to5Mac',
        'wired.com': 'Wired',
        'arstechnica.com': 'Ars Technica',
        'theinformation.com': 'The Information',
        'nikkei.com': 'Nikkei',
        'markets.businessinsider.com': 'Business Insider',
        'businessinsider.com': 'Business Insider',
        'cnbc.com': 'CNBC',
        'forbes.com': 'Forbes',
        'fastcompany.com': 'Fast Company',
        'axios.com': 'Axios',
        'theguardian.com': 'The Guardian',
        'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC',
        'npr.org': 'NPR',
        'pcmag.com': 'PCMag',
        'techradar.com': 'TechRadar',
        'tomshardware.com': 'Tom\'s Hardware',
        'pctechmag.com': 'PC Tech Magazine',
        'spacecoastdaily.com': 'Space Coast Daily',
        'hostinger.com': 'Hostinger',
        'vocal.media': 'Vocal Media',
        'gigradar.io': 'GigRadar',
        'prweek.com': 'PR Week',
        'kotaku.com': 'Kotaku',
        'astanatimes.com': 'The Astana Times',
        'hindustantimes.com': 'Hindustan Times',
        'worldofreel.com': 'World of Reel',
        'independent.ng': 'Independent Nigeria',
        'almcorp.com': 'ALM Corp',
        'ppcland.com': 'PPC Land',
        'stocktitan.net': 'Stock Titan',
        'themediaonline.co.za': 'The Media Online',
        '24-7pressrelease.com': '24-7 Press Release',
        'github.com': 'GitHub',
        'medium.com': 'Medium',
    }
    for key, val in mapping.items():
        if key in netloc:
            return val
    # Capitalize first part
    parts = domain.split('.')
    return parts[0].capitalize() if parts else domain

all_results = {}
for category, qlist in queries.items():
    print(f"\n=== {category.upper()} ===", file=sys.stderr)
    cat_results = []
    seen = set()
    for q in qlist:
        print(f"  Query: {q[:60]}...", file=sys.stderr)
        time.sleep(random.uniform(0.8, 1.5))
        results = search_ddg(q, max_results=8)
        for r in results:
            if r['url'] not in seen:
                seen.add(r['url'])
                cat_results.append(r)
                print(f"    [{len(cat_results)}] {r['title'][:70]}", file=sys.stderr)
        if len(cat_results) >= 10:
            break
    all_results[category] = cat_results[:10]

# Save raw
with open('/tmp/fresh_ddg_results.json', 'w') as f:
    json.dump(all_results, f, indent=2)

# Phase 2: extract text and build final dataset
print("\n\n=== Phase 2: Building final dataset ===", file=sys.stderr)

final_data = {}
for category, items in all_results.items():
    print(f"\n--- {category} ---", file=sys.stderr)
    final_items = []
    used_photos = set()
    photo_pool = unsplash_ids.get(category, unsplash_ids['filmschool'])
    
    for idx, item in enumerate(items[:6]):
        title = item['title']
        url = item['url']
        snippet = item.get('snippet', '')
        
        # Try to get more text
        print(f"  [{idx+1}] Extracting: {title[:50]}...", file=sys.stderr)
        time.sleep(0.5)
        full_text = extract_text_simple(url)
        
        if full_text:
            description = full_text[:500]
        elif snippet:
            description = snippet[:500]
        else:
            description = f"Article about {title[:80]}"
        
        # Clean description
        description = re.sub(r'\s+', ' ', description).strip()
        
        # Pick unsplash photo
        photo_id = photo_pool[idx % len(photo_pool)]
        while photo_id in used_photos and len(used_photos) < len(photo_pool):
            photo_id = random.choice(photo_pool)
        used_photos.add(photo_id)
        
        final_items.append({
            'title': title,
            'description': description,
            'url': url,
            'source': guess_source(url),
            'image_url': f"https://images.unsplash.com/photo-{photo_id}?w=600&q=60"
        })
    
    final_data[category] = final_items

# Write output
output_path = '/home/ubuntu/tech-pulse-server/ai-video-data.json'
with open(output_path, 'w') as f:
    json.dump(final_data, f, indent=2)

print(f"\n\nWritten to {output_path}", file=sys.stderr)
print(f"Categories: {list(final_data.keys())}", file=sys.stderr)
for cat, items in final_data.items():
    print(f"  {cat}: {len(items)} items", file=sys.stderr)

# Also output as JSON to stdout for the pipeline
print(json.dumps({"status": "ok", "categories": list(final_data.keys()), "total": sum(len(v) for v in final_data.values())}))
