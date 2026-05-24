#!/usr/bin/env python3
"""Tech Pulse v2 - Fetches recent tech news from HN and enriches with descriptions."""
import json
import urllib.request
import urllib.parse
import sys
import re
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser

class DescriptionExtractor(HTMLParser):
    """Extract meta description and title from HTML."""
    def __init__(self):
        super().__init__()
        self.description = ""
        self.title = ""
        self.in_title = False
        self.capturing = False
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'title':
            self.in_title = True
        if tag == 'meta' and attrs.get('name', '').lower() in ('description', 'og:description'):
            self.description = attrs.get('content', '')
        if tag == 'meta' and attrs.get('property', '').lower() == 'og:description':
            self.description = attrs.get('content', '')
        if tag == 'meta' and attrs.get('name', '').lower() == 'twitter:description':
            if not self.description:
                self.description = attrs.get('content', '')
                
    def handle_data(self, data):
        if self.in_title:
            self.title += data
            
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False

def fetch_url_text(url, timeout=10):
    """Fetch a URL and return text content."""
    try:
        req = urllib.request.Request(
            url, 
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; TechPulse/1.0; +https://tech-pulse-trillion.surge.sh)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content = resp.read().decode('utf-8', errors='replace')
            return content
    except Exception as e:
        return None

def extract_description(url):
    """Fetch article page and extract description."""
    content = fetch_url_text(url)
    if not content:
        return ""
    
    parser = DescriptionExtractor()
    try:
        parser.feed(content)
    except:
        pass
    
    desc = parser.description
    if not desc:
        # Try to extract first paragraph
        match = re.search(r'<p[^>]*>([^<]{50,300})</p>', content)
        if match:
            desc = match.group(1)
    
    # Clean up
    if desc:
        desc = re.sub(r'\s+', ' ', desc).strip()
        if len(desc) > 300:
            desc = desc[:297] + "..."
    
    return desc

def search_hn_recent(query, days=30, hits=20):
    """Search HN for recent stories."""
    now = int(datetime.now().timestamp())
    past = int((datetime.now() - timedelta(days=days)).timestamp())
    
    url = (
        f"https://hn.algolia.com/api/v1/search?"
        f"query={urllib.parse.quote(query)}"
        f"&tags=story"
        f"&hitsPerPage={hits}"
        f"&numericFilters=created_at_i>{past},created_at_i<{now}"
    )
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TechPulse/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        results = []
        for h in data.get("hits", []):
            title = h.get("title", "")
            story_url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
            points = h.get("points", 0)
            created = h.get("created_at", "")
            
            from urllib.parse import urlparse
            parsed = urlparse(story_url)
            source = parsed.netloc.replace("www.", "") if parsed.netloc else "Hacker News"
            
            results.append({
                "title": title,
                "url": story_url,
                "source": source,
                "points": points,
                "created_at": created,
            })
        return results
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
        return []

def search_front(page=1):
    """Get current HN front page stories."""
    url = f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30&page={page}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TechPulse/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        
        results = []
        for h in data.get("hits", []):
            title = h.get("title", "")
            story_url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
            points = h.get("points", 0)
            
            from urllib.parse import urlparse
            parsed = urlparse(story_url)
            source = parsed.netloc.replace("www.", "") if parsed.netloc else "Hacker News"
            
            results.append({
                "title": title,
                "url": story_url,
                "source": source,
                "points": points,
            })
        return results
    except Exception as e:
        print(f"  Error fetching front page: {e}", file=sys.stderr)
        return []

def classify_story(title, url, source):
    """Classify a story into one of the 5 categories."""
    title_lower = title.lower()
    url_lower = url.lower()
    
    # AI
    ai_keywords = ['ai ', 'artificial intelligence', 'machine learning', 'gpt', 'llm', 'neural',
                   'deep learning', 'openai', 'anthropic', 'claude', 'gemini', 'mistral', 'llama',
                   'model', 'transformer', 'diffusion', 'chatbot', 'copilot', 'hugging face',
                   'ai model', 'foundation model', 'agent', 'ai agent']
    for kw in ai_keywords:
        if kw in title_lower:
            return "ai"
    
    # Funding
    fund_keywords = ['funding', 'raised', 'series a', 'series b', 'series c', 'valuation',
                     'startup raises', 'venture', 'invests', 'investment', 'million funding',
                     'billion valuation', 'seed round', 'acquired', 'acquisition']
    for kw in fund_keywords:
        if kw in title_lower:
            return "funding"
    
    # Tools
    tools_keywords = ['developer tool', 'ide', 'editor', 'compiler', 'debugger', 'framework',
                      'api', 'sdk', 'cli', 'terminal', 'database', 'kubernetes', 'docker',
                      'devops', 'ci/cd', 'testing', 'code review', 'programming language',
                      'release', 'launch hn:', 'show hn:', 'open source tool', 'plugin']
    for kw in tools_keywords:
        if kw in title_lower:
            return "tools"
    
    # OSS
    oss_keywords = ['open source', 'github', 'gitlab', 'linux', 'python', 'rust', 'golang',
                    'npm', 'pypi', 'apache', 'mozilla', 'gnu', 'gpl', 'mit license']
    for kw in oss_keywords:
        if kw in title_lower:
            return "oss"
    
    # Industry
    industry_keywords = ['regulation', 'policy', 'antitrust', 'lawsuit', 'patent', 'copyright',
                         'chip', 'semiconductor', 'tariff', 'trade', 'government', 'senate',
                         'congress', 'sec', 'ftc', 'eu', 'privacy', 'security', 'cyber',
                         'layoff', 'hiring', 'ceo', 'microsoft', 'google', 'apple', 'meta',
                         'amazon', 'nvidia', 'intel', 'amd', 'tsmc', 'crisis', 'shortage',
                         'trump', 'biden', 'eu ai act']
    for kw in industry_keywords:
        if kw in title_lower:
            return "industry"
    
    # Default to tools if it's a Show HN or Launch HN (usually dev tools)
    if title_lower.startswith('show hn:') or title_lower.startswith('launch hn:'):
        return "tools"
    
    return None

def pick_descriptions(articles):
    """Try to fetch descriptions for top articles."""
    for i, article in enumerate(articles):
        if i >= 4:  # Only need descriptions for top 4
            break
        if article.get("description"):
            continue
        if not article.get("url"):
            continue
        if "news.ycombinator.com" in article["url"]:
            # Can't easily extract from HN comments page
            continue
        
        print(f"  Fetching description for: {article['title'][:60]}...", file=sys.stderr)
        desc = extract_description(article["url"])
        if desc:
            article["description"] = desc
            print(f"    Got: {desc[:80]}...", file=sys.stderr)
        else:
            article["description"] = article.get("description", "")

now = datetime.now()
print(f"Tech Pulse Fetch v2 - {now.strftime('%Y-%m-%d %H:%M UTC')}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Phase 1: Get front page stories (most recent and relevant)
print("\n--- Fetching HN front page ---", file=sys.stderr)
front_stories = search_front(page=1)
front_stories2 = search_front(page=2)
all_front = front_stories + front_stories2
print(f"  Got {len(all_front)} front page stories", file=sys.stderr)

# Phase 2: Search recent stories by category
print("\n--- Searching recent stories by category ---", file=sys.stderr)
category_queries = {
    "ai": ["AI", "GPT", "Claude", "Gemini", "neural network", "deep learning"],
    "funding": ["startup funding", "raised", "valuation", "Series A", "venture capital"],
    "tools": ["developer tools", "programming", "database", "API", "code", "IDE"],
    "industry": ["tech regulation", "chip", "semiconductor", "AI policy", "cybersecurity"],
    "oss": ["open source", "Linux", "Python", "Rust", "GitHub"]
}

all_stories = {}
for cat, queries in category_queries.items():
    cat_stories = []
    seen_urls = set()
    
    # First check front page stories
    for s in all_front:
        cls = classify_story(s["title"], s["url"], s["source"])
        if cls == cat and s["url"] not in seen_urls:
            seen_urls.add(s["url"])
            cat_stories.append(s)
    
    # Then search recent
    for q in queries:
        print(f"  [{cat}] Searching: {q}", file=sys.stderr)
        results = search_hn_recent(q, days=14, hits=10)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                cat_stories.append(r)
    
    # Sort by points, take top 6
    cat_stories.sort(key=lambda x: x.get("points", 0), reverse=True)
    all_stories[cat] = cat_stories[:6]
    print(f"  [{cat}] {len(cat_stories)} stories collected, keeping top 6", file=sys.stderr)

# Phase 3: Get descriptions for top stories
print("\n--- Fetching descriptions for top stories ---", file=sys.stderr)
for cat, stories in all_stories.items():
    print(f"\n[{cat}] Enriching {len(stories)} stories:", file=sys.stderr)
    pick_descriptions(stories)

# Build final output
print("\n--- Building final JSON ---", file=sys.stderr)

# Map category to sections_order keys
output = {}
cat_map = {
    "ai": "ai",
    "funding": "funding", 
    "tools": "tools",
    "industry": "industry",
    "oss": "oss"
}

unsplash_images = {
    "ai": "https://images.unsplash.com/photo-1677442136019?w=600&q=60",
    "funding": "https://images.unsplash.com/photo-1611974789855?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1461749280684?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1519389950473?w=600&q=60",
    "oss": "https://images.unsplash.com/photo-1558494949?w=600&q=60"
}

for cat_key, section_key in cat_map.items():
    stories = all_stories.get(cat_key, [])
    output[section_key] = []
    for s in stories[:4]:  # 2-4 per category
        output[section_key].append({
            "title": s["title"],
            "description": s.get("description", ""),
            "url": s["url"],
            "source": s["source"],
            "image_url": unsplash_images.get(cat_key, "")
        })

# Output JSON
print(json.dumps(output, indent=2))
