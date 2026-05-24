#!/usr/bin/env python3
"""Tech Pulse 24/7 v3 — RSS + Smart Categorizer + CDATA fix."""
import json, sys, time, os, re
from urllib.request import urlopen, Request
from urllib.parse import urlparse
import html

BASE = os.path.dirname(os.path.abspath(__file__))

FEEDS = [
    "https://techcrunch.com/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/startups/feed/",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://venturebeat.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/feed/",
    "https://hnrss.org/frontpage?count=20",
    "https://www.zdnet.com/news/rss.xml",
    "https://blog.google/technology/ai/rss/",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://github.blog/feed/",
]

SOURCE_MAP = {
    'techcrunch.com': 'TechCrunch', 'arstechnica.com': 'Ars Technica',
    'theverge.com': 'The Verge', 'wired.com': 'Wired',
    'venturebeat.com': 'VentureBeat', 'technologyreview.com': 'MIT Tech Review',
    'news.ycombinator.com': 'Hacker News', 'zdnet.com': 'ZDNet',
    'blog.google': 'Google Blog', 'aws.amazon.com': 'AWS',
    'github.blog': 'GitHub Blog', 'anthropic.com': 'Anthropic',
    'openai.com': 'OpenAI', 'mistral.ai': 'Mistral AI',
    'microsoft.com': 'Microsoft', 'devblogs.microsoft.com': 'Microsoft',
    'nvidia.com': 'NVIDIA', 'forbes.com': 'Forbes',
    'bloomberg.com': 'Bloomberg', 'reuters.com': 'Reuters',
    'cnbc.com': 'CNBC', 'nytimes.com': 'The New York Times',
    'wsj.com': 'WSJ', 'ft.com': 'Financial Times',
    'axios.com': 'Axios', 'engadget.com': 'Engadget',
    'sciencedaily.com': 'ScienceDaily', 'nature.com': 'Nature',
    'huggingface.co': 'HuggingFace', 'github.com': 'GitHub',
    'pytorch.org': 'PyTorch', 'tensorflow.org': 'TensorFlow',
}

UNSPLASH = {
    "ai": "https://images.unsplash.com/photo-1677442136019?w=600&q=60",
    "funding": "https://images.unsplash.com/photo-1611974789855?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1461749280684?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1519389950473?w=600&q=60",
    "oss": "https://images.unsplash.com/photo-1558494949?w=600&q=60",
}

def clean_str(s):
    s = s or ''
    # Remove CDATA
    s = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', s, flags=re.DOTALL)
    # Remove HTML tags
    s = re.sub(r'<[^>]+>', '', s)
    s = html.unescape(s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_domain(url):
    return urlparse(url).netloc.lower().replace('www.', '')

def get_source(url):
    domain = extract_domain(url)
    for key, val in SOURCE_MAP.items():
        if key in domain:
            return val
    parts = domain.split('.')
    return parts[0].title() if parts and parts[0] else ''

def fetch_rss(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        resp = urlopen(req, timeout=15)
        return resp.read().decode('utf-8', errors='replace')
    except:
        return None

def parse_rss(xml_text):
    items = []
    entries = re.findall(r'<(?:item|entry)>(.*?)</(?:item|entry)>', xml_text, re.DOTALL)
    for entry in entries:
        title = re.search(r'<title[^>]*>(.*?)</title>', entry, re.DOTALL)
        link = re.search(r'<link[^>]*href="([^"]+)"', entry) or re.search(r'<link>(.*?)</link>', entry, re.DOTALL)
        desc = re.search(r'<description[^>]*>(.*?)</description>', entry, re.DOTALL) or re.search(r'<summary[^>]*>(.*?)</summary>', entry, re.DOTALL)
        content = re.search(r'<content:encoded>(.*?)</content:encoded>', entry, re.DOTALL)
        
        title_text = clean_str(title.group(1)) if title else ''
        link_text = link.group(1).strip() if link else ''
        # Prefer content for description, then desc
        desc_raw = content.group(1) if content else (desc.group(1) if desc else '')
        desc_text = clean_str(desc_raw)[:400]
        
        if title_text and link_text and len(title_text) > 10:
            items.append({
                "title": title_text,
                "description": desc_text,
                "url": link_text,
                "source": get_source(link_text),
            })
    return items

def categorize(article):
    """Score article against each category. Use unique keywords for better separation."""
    text = (article['title'] + ' ' + article['description']).lower()
    scores = {}
    
    # AI keywords (highest priority)
    ai_score = 0
    ai_patterns = [r'\bgpt[-\s]?\d+', r'\bclaude\b', r'\bgemini\b', r'\bllama\b', r'\bdeepseek\b',
                   r'\bmistral\b', r'\bopenai\b', r'\banthropic\b', r'\bllm\b', r'\bfrontier\s*model\b',
                   r'\breasoning\s*model\b', r'\bmultimodal\b', r'\bdiffusion\s*model\b',
                   r'\btransformer\b', r'\bchatbot\b', r'\bai\s*(?:model|agent|safety|research|breakthrough)\b',
                   r'\bmachine\s*learning\b', r'\bdeep\s*learning\b', r'\bneural\s*network\b',
                   r'\bgenerative\s*ai\b', r'\bgenai?\b', r'\bgpqa\b', r'\bhuman\s*eval\b',
                   r'\bgrok\b', r'\bx\.?ai\b', r'\bperplexity\b', r'\bcohere\b', r'\bai21\b',
                   r'\breplit\s*ai\b', r'\bcursor\b', r'\bcopilot\b', r'\bcodex\b',
                   r'\bai\s*(?:coding|code|programming)\b', r'\btext[- ]to[- ](?:video|image|code)\b',
                   r'\bopen.?source\s*(?:llm|model|ai)\b']
    for p in ai_patterns:
        ai_score += len(re.findall(p, text))
    scores['ai'] = ai_score
    
    # Funding keywords
    fund_score = 0
    fund_patterns = [r'\b(?:raises?|raising|funding|fundraise|series\s*[a-z]|venture\s*capital)\b',
                     r'\bvaluation\b', r'\bunicorn\b', r'\b(?:billion|million)\s*(?:funding|round|raise|valuation)\b',
                     r'\bacquisitions?\b', r'\bipo\b', r'\binvestment\s*round\b', r'\bseed\s*round\b',
                     r'\bstartup\s*(?:fund|raises?|valuation)\b', r'\bvc\b', r'\binvestor\b',
                     r'\bseries\s*[a-e]\s*(?:round|funding)\b']
    for p in fund_patterns:
        fund_score += len(re.findall(p, text))
    scores['funding'] = fund_score
    
    # Tools keywords
    tools_score = 0
    tools_patterns = [r'\b(?:new\s+)?(?:framework|sdk|api|library|toolkit|compiler|debugger|linter|formatter)\b',
                      r'\brelease\s*(?:notes?|v?\d+|candidate|launch|of)\b', r'\bversion\s+\d+\.\d+\b',
                      r'\bprogramming\s*language\b', r'\bruntime\b', r'\bide\b', r'\bvscode\b',
                      r'\bjetbrains\b', r'\bvisual\s*studio\b',
                      r'\bkubernetes\b', r'\bdocker\b', r'\bterraform\b', r'\bserverless\b',
                      r'\bdevops\b', r'\bci/cd\b', r'\bobservability\b',
                      r'\bdatabase\b', r'\bpostgres(?:ql)?\b', r'\bredis\b', r'\bkafka\b',
                      r'\bcloud\s*(?:computing|native|platform)\b',
                      r'\bdeveloper\s*tool\b', r'\bdev\s*tool\b', r'\bopen.?source\s*(?:tool|library|framework)\b']
    for p in tools_patterns:
        tools_score += len(re.findall(p, text))
    scores['tools'] = tools_score
    
    # Industry keywords
    ind_score = 0
    ind_patterns = [r'\bregulat(?:ion|ory|e|ion)\b', r'\bpolicy\b', r'\blegislation\b', r'\blaw\b', r'\bbill\b',
                    r'\bcompliance\b', r'\bgovernance\b', r'\b(?:white\s+house|congress|senate|eu|fcc|ftc)\b',
                    r'\bantitrust\b', r'\blayoff\b', r'\bhiring\b', r'\bworkforce\b',
                    r'\bdata\s*center\b', r'\bchip\b', r'\bsemiconductor\b', r'\bgpu\b',
                    r'\bai\s*(?:regulation|policy|law|ban|restrict)\b',
                    r'\barms\s*race\b', r'\bnational\s*security\b',
                    r'\b(?:google|meta|microsoft|apple|amazon|nvidia|oracle|ibm)\s*(?:ai|invest|data.enter)\b',
                    r'\bsanctions?\b', r'\bexport\s*controls?\b',
                    r'\bsafety\s*(?:incident|concern|risk|warning|alarm)\b',
                    r'\benergy\s*(?:consumption|grid|efficiency)\b']
    for p in ind_patterns:
        ind_score += len(re.findall(p, text))
    scores['industry'] = ind_score
    
    # OSS keywords
    oss_score = 0
    oss_patterns = [r'\bopen[- ]source\b', r'\bgithub\b', r'\bhugging\s*face\b',
                    r'\breleased\s*(?:as|under)\s*(?:open.?source|mit|apache|gpl|bsd)\b',
                    r'\blicens(?:e|ed)\s*(?:mit|apache|gpl|bsd|open)\b',
                    r'\bpypi\b', r'\bnpm\b', r'\bcrates\.io\b',
                    r'\bopen.?source\s*(?:model|llm|release|project|community)\b',
                    r'\bcommunity\s*(?:edition|contribution)\b',
                    r'\bweights?\s*(?:released|available|public)\b']
    for p in oss_patterns:
        oss_score += len(re.findall(p, text))
    scores['oss'] = oss_score
    
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

def deduplicate(articles):
    seen_urls = set()
    seen_titles = set()
    unique = []
    for a in articles:
        url_key = a['url'].split('?')[0].split('#')[0]
        title_key = a['title'].lower().strip()[:60]
        if url_key not in seen_urls and title_key not in seen_titles:
            seen_urls.add(url_key)
            seen_titles.add(title_key)
            unique.append(a)
    return unique

print("=" * 60, file=sys.stderr)
print("TECH PULSE 24/7 v3 — May 24, 2026", file=sys.stderr)
print("=" * 60, file=sys.stderr)

all_articles = []
for feed_url in FEEDS:
    print(f"📡 {feed_url[:65]}...", file=sys.stderr)
    data = fetch_rss(feed_url)
    if data:
        items = parse_rss(data)
        all_articles.extend(items)
        print(f"  → {len(items)} items", file=sys.stderr)
    else:
        print(f"  ✗ Failed", file=sys.stderr)
    time.sleep(0.3)

print(f"\n📊 Total raw: {len(all_articles)}", file=sys.stderr)
all_articles = deduplicate(all_articles)
print(f"📊 After dedup: {len(all_articles)}", file=sys.stderr)

# Categorize
categorized = {k: [] for k in ['ai', 'funding', 'tools', 'industry', 'oss']}
misc = []
for article in all_articles:
    cat = categorize(article)
    if cat:
        categorized[cat].append(article)
    else:
        misc.append(article)

# Fill misc into best matching category based on broader heuristics
for a in misc:
    text = (a['title'] + ' ' + a['description']).lower()
    if any(w in text for w in ['ai', 'artificial intelligence', 'machine learning', 'neural', 'model ']):
        categorized['ai'].append(a)
    elif any(w in text for w in ['million', 'billion', 'fund', 'startup', 'invest', 'revenue']):
        categorized['funding'].append(a)
    elif any(w in text for w in ['release', 'launch', 'update', 'tool', 'software', 'app', 'version']):
        categorized['tools'].append(a)
    else:
        categorized['industry'].append(a)

# Pick top 6 per category, prioritizing items with descriptions
for cat in categorized:
    categorized[cat] = sorted(categorized[cat], key=lambda x: len(x['description']), reverse=True)[:6]

# Build output
output_data = {}
for cat in ['ai', 'funding', 'tools', 'industry', 'oss']:
    img = UNSPLASH.get(cat, '')
    output_data[cat] = []
    for a in categorized[cat]:
        output_data[cat].append({
            "title": a['title'],
            "description": a['description'][:300],
            "url": a['url'],
            "source": a['source'] or get_source(a['url']),
            "image_url": img,
        })

# Print summary
for cat in ['ai', 'funding', 'tools', 'industry', 'oss']:
    print(f"\n--- {cat.upper()} ({len(output_data[cat])}) ---", file=sys.stderr)
    for a in output_data[cat][:4]:
        desc = a['description'][:60].replace('\n', ' ')
        print(f"  • {a['title'][:80]}", file=sys.stderr)
        print(f"    └ {a['source']} | {desc}...", file=sys.stderr)

# Write
output_path = os.path.join(BASE, "pulse-data.json")
with open(output_path, "w") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)
print(f"\n✅ Wrote {sum(len(v) for v in output_data.values())} articles to pulse-data.json", file=sys.stderr)
