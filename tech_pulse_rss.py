#!/usr/bin/env python3
"""Tech Pulse 24/7 — RSS Fetcher + Keyword Categorizer for fresh news."""
import json, sys, time, os, re
from urllib.request import urlopen, Request
from urllib.parse import urlparse
import html

BASE = os.path.dirname(os.path.abspath(__file__))

# ===== CONFIGURATION =====
FEEDS = [
    "https://techcrunch.com/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://techcrunch.com/category/startups/feed/",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.theverge.com/rss/index.xml",
    "https://www.theverge.com/ai-artificial-intelligence/rss.xml",
    "https://www.wired.com/feed/rss",
    "https://venturebeat.com/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/feed/",
    "https://hnrss.org/frontpage?count=20",
    "https://hnrss.org/newest?count=20",
    "https://www.zdnet.com/news/rss.xml",
    "https://feeds.feedburner.com/oreilly/radar/atom",
    "https://blog.google/technology/ai/rss/",
    "https://aws.amazon.com/blogs/machine-learning/feed/",
    "https://github.blog/feed/",
    "https://stackoverflow.blog/feed/",
]

SOURCE_MAP = {
    'techcrunch.com': 'TechCrunch', 'arstechnica.com': 'Ars Technica',
    'theverge.com': 'The Verge', 'wired.com': 'Wired',
    'venturebeat.com': 'VentureBeat', 'technologyreview.com': 'MIT Tech Review',
    'news.ycombinator.com': 'Hacker News', 'zdnet.com': 'ZDNet',
    'oreilly.com': "O'Reilly", 'blog.google': 'Google Blog',
    'aws.amazon.com': 'AWS', 'github.blog': 'GitHub Blog',
    'stackoverflow.blog': 'Stack Overflow Blog',
    'anthropic.com': 'Anthropic', 'openai.com': 'OpenAI',
    'mistral.ai': 'Mistral AI', 'deepmind.com': 'DeepMind',
    'microsoft.com': 'Microsoft', 'devblogs.microsoft.com': 'Microsoft',
    'nvidia.com': 'NVIDIA', 'forbes.com': 'Forbes',
    'bloomberg.com': 'Bloomberg', 'reuters.com': 'Reuters',
    'cnbc.com': 'CNBC', 'nytimes.com': 'The New York Times',
    'wsj.com': 'Wall Street Journal', 'ft.com': 'Financial Times',
    'axios.com': 'Axios', 'engadget.com': 'Engadget',
    'thenextweb.com': 'TNW', 'sciencedaily.com': 'ScienceDaily',
    'nature.com': 'Nature', 'arxiv.org': 'arXiv',
    'huggingface.co': 'HuggingFace', 'github.com': 'GitHub',
    'gitlab.com': 'GitLab', 'pytorch.org': 'PyTorch',
    'tensorflow.org': 'TensorFlow', 'keras.io': 'Keras',
}

UNSPLASH = {
    "ai": "https://images.unsplash.com/photo-1677442136019?w=600&q=60",
    "funding": "https://images.unsplash.com/photo-1611974789855?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1461749280684?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1519389950473?w=600&q=60",
    "oss": "https://images.unsplash.com/photo-1558494949?w=600&q=60",
}

# Category keyword classifiers (title + description matching)
CATEGORY_KEYWORDS = {
    "ai": [
        r'\b(gpt|claude|gemini|llama|deepseek|mistral|openai|anthropic|google\s*ai)\b',
        r'\b(llm|large\s*language\s*model|foundation\s*model|frontier\s*model)\b',
        r'\b(ai\s*model|ml\s*model|machine\s*learning|deep\s*learning|neural\s*network)\b',
        r'\b(reasoning|agent|autonomous|multimodal|token|context\s*window)\b',
        r'\b(generative\s*ai|gen\s*ai|diffusion|transformer|attention)\b',
        r'\b(benchmark|gpqa|mmlu|human\s*eval|chatbot|arena|elo)\b',
        r'\b(ai\s*safety|alignment|red\s*teaming|jailbreak|guardrail)\b',
        r'\b(ai\s*research|paper|breakthrough|advancement|state\s*of\s*the\s*art)\b',
    ],
    "funding": [
        r'\b(funding|fundraise|series\s*[a-z]|venture\s*capital|vc|investor)\b',
        r'\b(valuation|unicorn|billion|million.*(?:raise|funding|round|investment))\b',
        r'\b(acquisition|acquired|buyout|merger|ipo|spac|public\s*offering)\b',
        r'\b(startup.*(?:fund|raise|invest)|invest.*(?:ai|startup|tech))\b',
        r'\b(mega.?round|seed|angel|accelerator|incubator)\b',
    ],
    "tools": [
        r'\b(developer\s*tool|dev\s*tool|framework|sdk|api|library|toolkit)\b',
        r'\b(release\s*(?:notes|new|launch)|new\s*release|version\s*\d+\.\d+)\b',
        r'\b(ide|editor|compiler|debugger|linter|formatter|language\s*server)\b',
        r'\b(programming\s*language|runtime|interpreter|vm|container)\b',
        r'\b(coding|programming|software\s*development|devops|ci/cd|deployment)\b',
        r'\b(cloud|kubernetes|docker|terraform|ansible|pulumi|serverless)\b',
        r'\b(database|cache|queue|stream|storage|nosql|sql|postgres|redis|kafka)\b',
        r'\b(observability|monitoring|logging|tracing|metrics|apm)\b',
        r'\b(vscode|jetbrains|intellij|pycharm|webstorm|visual\s*studio)\b',
    ],
    "industry": [
        r'\b(regulation|regulatory|policy|legislation|law|act|bill|compliance|governance)\b',
        r'\b(white\s*house|congress|senate|eu|european\s*commission|fcc|ftc)\b',
        r'\b(big\s*tech|google|meta|microsoft|apple|amazon|nvidia|oracle|ibm)\b',
        r'\b(data\s*center|infrastructure|chip|semiconductor|gpu|tpu|server|compute)\b',
        r'\b(ai\s*.*(?:law|regulation|policy|ban|restrict|oversight|review))\b',
        r'\b(layoff|hire|workforce|talent|salary|job|employment|relocation)\b',
        r'\b(antitrust|monopoly|competition|market\s*dominance|investigation)\b',
        r'\b(energy|power|electricity|grid|sustainability|emission|carbon|climate)\b',
    ],
    "oss": [
        r'\b(open\s*source|oss|free\s*software|mit\s*license|apache\s*license|gpl)\b',
        r'\b(hugging.?face|pypi|npm|crates\.io|maven|nuget|rubygems)\b',
        r'\b(github|gitlab|gitee|sourceforge|codeberg)\b',
        r'\b(open.?source\s*(?:ai|model|llm|release|project|tool|library))\b',
        r'\b(released\s*(?:on|under)\s*(?:open.?source|mit|apache|github))\b',
        r'\b(community|contributor|maintainer|pull\s*request|issue|fork|star)\b',
        r'\b(model.*(?:open.?source|weights|checkpoint|release|download))\b',
        r'\b(linux|gnu|kde|gnome|systemd|wayland|pipewire|flatpak|snap)\b',
    ],
}

def extract_domain(url):
    return urlparse(url).netloc.lower().replace('www.', '')

def get_source(url):
    domain = extract_domain(url)
    for key, val in SOURCE_MAP.items():
        if key in domain:
            return val
    parts = domain.split('.')
    return parts[0].title() if parts else ''

def categorize(article):
    """Score article against each category and return best match."""
    text = (article['title'] + ' ' + article['description']).lower()
    scores = {}
    for cat, patterns in CATEGORY_KEYWORDS.items():
        score = 0
        for p in patterns:
            matches = re.findall(p, text)
            score += len(matches)
        scores[cat] = score
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None

def fetch_rss(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
        resp = urlopen(req, timeout=15)
        data = resp.read().decode('utf-8', errors='replace')
        return data
    except Exception as e:
        return None

def parse_rss(xml_text):
    """Basic RSS/Atom parser using regex."""
    items = []
    entries = re.findall(r'<(?:item|entry)>(.*?)</(?:item|entry)>', xml_text, re.DOTALL)
    for entry in entries:
        title = re.search(r'<title[^>]*>(.*?)</title>', entry, re.DOTALL)
        link = re.search(r'<link[^>]*href="([^"]+)"', entry) or re.search(r'<link>(.*?)</link>', entry, re.DOTALL)
        desc = re.search(r'<description[^>]*>(.*?)</description>', entry, re.DOTALL) or re.search(r'<summary[^>]*>(.*?)</summary>', entry, re.DOTALL)
        
        title_text = html.unescape(title.group(1).strip()) if title else ""
        link_text = link.group(1).strip() if link else ""
        desc_text = html.unescape(re.sub(r'<[^>]+>', '', desc.group(1).strip())) if desc else ""
        
        if title_text and link_text and len(title_text) > 10:
            items.append({
                "title": title_text,
                "description": desc_text[:400],
                "url": link_text,
                "source": get_source(link_text),
            })
    return items

def deduplicate(articles):
    seen_urls = set()
    seen_titles = set()
    unique = []
    for a in articles:
        url_key = a['url'].split('?')[0].split('#')[0]
        title_key = a['title'].lower().strip()
        if url_key not in seen_urls and title_key not in seen_titles:
            seen_urls.add(url_key)
            seen_titles.add(title_key)
            unique.append(a)
    return unique

# ===== MAIN =====
print("=" * 60, file=sys.stderr)
print("TECH PULSE 24/7 — RSS+Pipeline — May 24, 2026", file=sys.stderr)
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

# Deduplicate
all_articles = deduplicate(all_articles)
print(f"📊 After dedup: {len(all_articles)}", file=sys.stderr)

# Categorize
categorized = {k: [] for k in CATEGORY_KEYWORDS}
uncategorized = []
for article in all_articles:
    cat = categorize(article)
    if cat:
        categorized[cat].append(article)
    else:
        uncategorized.append(article)

# Fill gaps: try to put uncategorized into tools or ai based on broad matching
for a in uncategorized:
    text = (a['title'] + ' ' + a['description']).lower()
    if any(w in text for w in ['ai ', ' model', ' neural', ' machine learning', ' artificial intelligence']):
        categorized['ai'].append(a)
    elif any(w in text for w in ['release', 'launch', 'update', 'new', 'tool', 'software', 'app']):
        categorized['tools'].append(a)
    elif any(w in text for w in ['company', 'ceo', 'report', 'market', 'billion', 'million', 'revenue']):
        categorized['industry'].append(a)
    else:
        categorized['tools'].append(a)  # fallback

for cat, articles in categorized.items():
    print(f"\n--- {cat.upper()} ({len(articles)} articles) ---", file=sys.stderr)
    categorized[cat] = articles[:6]  # keep top 6 per category

# Build output
output_data = {}
for cat, articles in categorized.items():
    img = UNSPLASH.get(cat, "")
    output_data[cat] = []
    for a in articles[:6]:
        output_data[cat].append({
            "title": a['title'],
            "description": a['description'][:250],
            "url": a['url'],
            "source": a['source'] or get_source(a['url']),
            "image_url": img,
        })
    for a in output_data[cat][:4]:
        print(f"  • {a['title'][:85]} [{a['source']}]", file=sys.stderr)

# Write pulse-data.json
output_path = os.path.join(BASE, "pulse-data.json")
with open(output_path, "w") as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)
print(f"\n✅ Wrote {sum(len(v) for v in output_data.values())} articles to pulse-data.json", file=sys.stderr)
