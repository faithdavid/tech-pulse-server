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
        desc = re.sub(r'<[^>]+>', '', desc_html)
        desc = desc.strip()
        items.append({
            'title': title.strip(),
            'url': link.strip(),
            'description': desc,
            'source': source,
            'pubdate': pubdate,
        })
    return items

queries = [
    ('ai', 'AI+breakthrough+new+model+2026'),
    ('funding', 'startup+funding+AI+round+2026'),
    ('tools', 'developer+tools+release+framework+2026'),
    ('oss', 'open+source+project+major+release+2026'),
    ('industry', 'tech+industry+policy+regulation+AI+2026'),
]

for key, query in queries:
    url = f'https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en'
    try:
        xml = fetch_rss(url)
        items = parse_rss(xml)
        print(f'=== {key} ({len(items)} items) ===')
        for i, item in enumerate(items[:10]):
            print(f'ITEM|{i+1}|{item["source"]}|{item["title"]}|{item["description"][:200]}|{item["url"]}')
    except Exception as e:
        print(f'ERROR {key}: {e}')
