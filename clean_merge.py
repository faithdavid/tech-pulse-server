#!/usr/bin/env python3
"""Clean merge: good git data + best fresh DDG results."""
import json, re

# Load good data from git
with open('/tmp/ai-video-good.json') as f:
    good = json.load(f)

# Load fresh DDG results
with open('/tmp/fresh_ddg_results.json') as f:
    fresh = json.load(f)

def guess_source(url):
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
        'markets.businessinsider.com': 'Business Insider', 'cnbc.com': 'CNBC',
        'forbes.com': 'Forbes', 'fastcompany.com': 'Fast Company', 'axios.com': 'Axios',
        'theguardian.com': 'The Guardian', 'bbc.com': 'BBC', 'bbc.co.uk': 'BBC',
        'npr.org': 'NPR', 'pcmag.com': 'PCMag', 'techradar.com': 'TechRadar',
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
        'cscestudiodigital.com': 'CSC Estudio Digital', 'pumpitupmagazine.com': 'Pump It Up Magazine',
        'genmedialab.com': 'GenMedia Lab', 'digitalapplied.com': 'Digital Applied',
        'resource.digen.ai': 'Digen AI', 'businessinsider.com': 'Business Insider',
    }
    for key, val in mapping.items():
        if key in netloc:
            return val
    parts = domain.split('.')
    return parts[0].capitalize() if parts else domain

def is_video_ai_relevant(title, snippet):
    """Check if a fresh result is actually about AI video."""
    combined = (title + ' ' + (snippet or '')).lower()
    # Must contain at least one of these signals
    signals = [
        'ai video', 'ai film', 'ai-generat', 'video generat', 'text to video',
        'runway', 'kling', 'sora', 'veo', 'pika', 'dreamina', 'seedance',
        'video tool', 'video production', 'video creation', 'video editing',
        'cinematic ai', 'ai storytell', 'ai filmmaker', 'ai cinema',
        'video market', 'ai freelanc', 'ai side hustle', 'ai business',
        'make money with ai', 'video trend', 'ai content', 'video campaign',
    ]
    return any(s in combined for s in signals)

# Build merged dataset
merged = {}
allowed_cats = ['filmschool', 'industry', 'tools', 'niches', 'offers', 'inspire']

for category in allowed_cats:
    used_urls = set()
    merged_items = []
    
    # Add all good existing data first
    for item in good.get(category, []):
        url = item.get('url', '')
        if url and url not in used_urls:
            used_urls.add(url)
            merged_items.append(item)
    
    # Try to add fresh relevant supplement
    for item in fresh.get(category, []):
        url = item.get('url', '')
        title = item.get('title', '')
        snippet = item.get('snippet', '')
        if url and url not in used_urls and is_video_ai_relevant(title, snippet):
            used_urls.add(url)
            # Create description from snippet
            desc = re.sub(r'\s+', ' ', snippet).strip() if snippet else f"Article about {title[:80]}"
            if not desc or len(desc) < 40:
                desc = f"Latest insights on {title[:80]}"
            merged_items.append({
                'title': title,
                'description': desc[:500],
                'url': url,
                'source': guess_source(url),
                'image_url': merged_items[-1]['image_url'] if merged_items else "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=600&q=60"
            })
    
    merged[category] = merged_items

# Write final output
output_path = '/home/ubuntu/tech-pulse-server/ai-video-data.json'
with open(output_path, 'w') as f:
    json.dump(merged, f, indent=2)

print("=== MERGED DATA ===")
for cat, items in merged.items():
    print(f"\n{cat}: {len(items)} items")
    for item in items:
        print(f"  • {item['title'][:70]}")
        print(f"    {item['source']} | {item['url'][:60]}")

print(f"\nTotal: {sum(len(v) for v in merged.values())} items")
print(f"File: {output_path}")
