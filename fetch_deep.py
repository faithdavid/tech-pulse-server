import urllib.request, xml.etree.ElementTree as ET, ssl, json, re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def fetch_rss(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'})
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    return resp.read().decode('utf-8')

def parse_rss(xml_data):
    items = []
    root = ET.fromstring(xml_data)
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        desc_html = item.findtext('description', '')
        source = item.findtext('source', '')
        pubdate = item.findtext('pubDate', '')
        desc = re.sub(r'<[^>]+>', '', desc_html).strip()
        items.append({
            'title': title.strip(),
            'url': link.strip(),
            'description': desc,
            'source': source,
            'pubdate': pubdate,
        })
    return items

# Phase 2 - more targeted deep dives
queries = [
    # AI - deep dives
    ('ai', 'Anthropic+Mythos+AI+model+security+2026'),
    ('ai', 'DeepSeek+flagship+AI+model+flagship+2026'),
    ('ai', 'AI+energy+efficiency+100x+breakthrough+2026'),
    ('ai', 'Stanford+AI+Index+2026+report'),
    # Funding - deep dives
    ('funding', 'Anduril+$60+billion+valuation+defense+2026'),
    ('funding', 'Wirestock+$23+million+funding+AI+data+2026'),
    ('funding', 'US+AI+companies+raised+$100+million+2026'),
    ('funding', 'Sarvam+AI+$300+million+HCLTech+funding+2026'),
    # Tools - deep dives
    ('tools', 'TanStack+AI+toolkit+framework+agnostic+2026'),
    ('tools', 'Oracle+Java+26+release+2026'),
    ('tools', 'Google+natively+adaptive+interfaces+AI+accessibility+2026'),
    ('tools', 'Meta+ranking+engineer+agent+REA+AI+2026'),
    # OSS - deep dives
    ('oss', 'Anthropic+Project+Glasswing+open+source+security+2026'),
    ('oss', 'NVIDIA+GPU+dynamic+resource+allocation+Kubernetes+2026'),
    ('oss', 'Mistral+Leanstral+open+source+vibe+coding+2026'),
    ('oss', 'open+source+security+73%+rise+malicious+2026'),
    # Industry - deep dives
    ('industry', 'White+House+vetting+AI+models+before+release+2026'),
    ('industry', 'EU+AI+Act+failed+deal+2026'),
    ('industry', 'White+House+National+AI+Policy+Framework+2026'),
    ('industry', 'California+tech+giants+spending+politics+2026'),
]

all_results = {}
for key, query in queries:
    url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
    try:
        xml = fetch_rss(url)
        items = parse_rss(xml)
        if key not in all_results:
            all_results[key] = []
        all_results[key].extend(items[:3])
    except Exception as e:
        pass

for key, items in all_results.items():
    print(f'=== {key} ({len(items)} items) ===')
    for i, item in enumerate(items[:5]):
        print(f'ITEM|{i+1}|{item["source"]}|{item["title"][:120]}|{item["url"]}')
    print()
