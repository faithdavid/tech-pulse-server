#!/usr/bin/env python3
"""Merge existing + fresh DDG results into cleaned ai-video-data.json."""
import json, re, random

# Load existing data
with open('/home/ubuntu/tech-pulse-server/ai-video-data.json') as f:
    existing = json.load(f)

# Load fresh results
with open('/tmp/fresh_ddg_results.json') as f:
    fresh = json.load(f)

# Unsplash photo pools per category
photos = {
    'filmschool': ['1485846234645', '1523050854058-8df90110c7f1', '1536240478700-b869070f9279', '1478720568477-152d9b164e26', '1492691527719-9d1e07e534b4'],
    'industry': ['1611974789855-9c2a0a7236a3', '1519389950473-47ba0277781c', '1460925895917-afdab827c52f', '1551288049-bebda4e38f71', '1518770660439-4636190af475'],
    'tools': ['1558494949-ef010cbdcc31', '1461749280684-dccba630e2f6', '1518770660439-4636190af475', '1558618666-fcd25c85f82e', '1519389950473-47ba0277781c'],
    'niches': ['1558618666-fcd25c85f82e', '1551288049-bebda4e38f71', '1519389950473-47ba0277781c', '1460925895917-afdab827c52f', '1518770660439-4636190af475'],
    'offers': ['1554224155-8d04cb21cd6c', '1454165804606-c3d57bc86b40', '1460925895917-afdab827c52f', '1551288049-bebda4e38f71', '1519389950473-47ba0277781c'],
    'inspire': ['1478720568477-152d9b164e26', '1487180144351-b8472da7d491', '1492691527719-9d1e07e534b4', '1536240478700-b869070f9279', '1485846234645'],
}

def guess_source(url):
    """Extract source name from URL."""
    from urllib.parse import urlparse
    try:
        netloc = urlparse(url).netloc
    except:
        return 'Web'
    domain = netloc.replace('www.', '')
    mapping = {
        'youtube.com': 'YouTube', 'techcrunch.com': 'TechCrunch', 'theverge.com': 'The Verge',
        'venturebeat.com': 'VentureBeat', 'reuters.com': 'Reuters', 'variety.com': 'Variety',
        'hollywoodreporter.com': 'The Hollywood Reporter', 'deadline.com': 'Deadline',
        'bloomberg.com': 'Bloomberg', '9to5mac.com': '9to5Mac', 'wired.com': 'Wired',
        'arstechnica.com': 'Ars Technica', 'nikkei.com': 'Nikkei',
        'markets.businessinsider.com': 'Business Insider', 'businessinsider.com': 'Business Insider',
        'cnbc.com': 'CNBC', 'forbes.com': 'Forbes', 'fastcompany.com': 'Fast Company',
        'axios.com': 'Axios', 'theguardian.com': 'The Guardian', 'bbc.com': 'BBC',
        'bbc.co.uk': 'BBC', 'npr.org': 'NPR', 'pcmag.com': 'PCMag', 'techradar.com': 'TechRadar',
        'tomshardware.com': "Tom's Hardware", 'pctechmag.com': 'PC Tech Magazine',
        'spacecoastdaily.com': 'Space Coast Daily', 'hostinger.com': 'Hostinger',
        'vocal.media': 'Vocal Media', 'gigradar.io': 'GigRadar', 'prweek.com': 'PR Week',
        'kotaku.com': 'Kotaku', 'astanatimes.com': 'The Astana Times',
        'hindustantimes.com': 'Hindustan Times', 'worldofreel.com': 'World of Reel',
        'independent.ng': 'Independent Nigeria', 'almcorp.com': 'ALM Corp',
        'ppcland.com': 'PPC Land', 'stocktitan.net': 'Stock Titan',
        'themediaonline.co.za': 'The Media Online', '24-7pressrelease.com': '24-7 Press Release',
        'github.com': 'GitHub', 'medium.com': 'Medium',
        'cinemadrop.com': 'CinemaDrop', 'vo3ai.com': 'VO3 AI', 'seedance.tv': 'Seedance',
        'genra.ai': 'GenRA AI', 'anyapi.ai': 'AnyAPI', 'digen.ai': 'Digen AI',
        'imagine.art': 'ImagineArt', 'story2vid.com': 'Story2Vid',
        'cscestudiodigital.com': 'CSC Estudio Digital',
        'pumpitupmagazine.com': 'Pump It Up Magazine',
        'genmedialab.com': 'GenMedia Lab', 'digitalapplied.com': 'Digital Applied',
        'resource.digen.ai': 'Digen AI',
    }
    for key, val in mapping.items():
        if key in netloc:
            return val
    parts = domain.split('.')
    return parts[0].capitalize() if parts else domain

def is_relevant(title, snippet):
    """Filter out irrelevant/garbage results."""
    title_lower = title.lower()
    snippet_lower = snippet.lower() if snippet else ''
    combined = title_lower + ' ' + snippet_lower
    
    # Skip generic AI homepage results
    skip_patterns = [
        'openai | research', 'google gemini', 'chatgpt', 'perplexity ai',
        'what is ai - deepai', 'meta ai', 'artificial intelligence - wikipedia',
        'les 20 meilleures', 'joaillerie', 'odace', 'sports direct',
        'amazon prime arnaque', 'amazon premium', 'débit injustifié',
        'zhihu.com', 'forum.quechoisir',
        'acceuil', 'page introuvable',
    ]
    for pat in skip_patterns:
        if pat in combined:
            return False
    
    # Must have video/AI related keywords
    video_keywords = ['ai video', 'ai film', 'video ai', 'ai-generated video', 'video generation',
                      'ai filmmaking', 'ai storytelling', 'cinematic ai', 'text to video',
                      'runway', 'kling', 'sora', 'veo', 'pika', 'dreamina', 'seedance',
                      'video generator', 'video tool', 'video creation', 'video production',
                      'video editing', 'video content', 'ai movie', 'ai cinema',
                      'video marketing', 'ai creator', 'video trend', 'video market',
                      'ai side hustle', 'ai business', 'ai freelanc', 'make money with ai']
    
    # Accept if it matches any keyword OR if it's from a known good source
    if any(kw in combined for kw in video_keywords):
        return True
    
    # Also accept if it's a long meaningful title that seems relevant
    if len(title) > 20 and any(kw in title_lower for kw in ['ai', 'video', 'film', 'cinema', 'generat']):
        return True
    
    return False

def make_description(item):
    """Create a description from available data."""
    snippet = item.get('snippet', item.get('description', ''))
    snippet = re.sub(r'\s+', ' ', snippet).strip()
    if snippet and len(snippet) > 50:
        return snippet[:500]
    return f"Article exploring {item.get('title', 'AI video topic')[:80]}"

# Build merged dataset
merged = {}
for category in ['filmschool', 'industry', 'tools', 'niches', 'offers', 'inspire']:
    print(f"\n=== {category} ===")
    used_urls = set()
    merged_items = []
    photo_pool = photos.get(category, photos['filmschool'])
    
    # First, add existing data (it's well-curated)
    for item in existing.get(category, []):
        url = item.get('url', '')
        if url and url not in used_urls:
            used_urls.add(url)
            merged_items.append(item)
            print(f"  [existing] {item['title'][:60]}")
    
    # Then, add fresh relevant results that aren't already included
    for item in fresh.get(category, []):
        url = item.get('url', '')
        title = item.get('title', '')
        snippet = item.get('snippet', '')
        if url and url not in used_urls and is_relevant(title, snippet):
            used_urls.add(url)
            source = guess_source(url)
            from hashlib import md5
            photo_id = photo_pool[len(merged_items) % len(photo_pool)]
            new_item = {
                'title': title,
                'description': make_description(item),
                'url': url,
                'source': source,
                'image_url': f"https://images.unsplash.com/photo-{photo_id}?w=600&q=60"
            }
            merged_items.append(new_item)
            print(f"  [fresh+] {title[:60]}")
    
    # Limit to 4 items per category for conciseness
    merged[category] = merged_items[:4]
    print(f"  Total: {len(merged[category])} items")

# Write merged output
output_path = '/home/ubuntu/tech-pulse-server/ai-video-data.json'
with open(output_path, 'w') as f:
    json.dump(merged, f, indent=2)

print(f"\n\nFinal written to {output_path}")
total = sum(len(v) for v in merged.values())
print(f"Total items across all categories: {total}")
