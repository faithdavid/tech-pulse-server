#!/usr/bin/env python3
"""Search DuckDuckGo for AI video news across categories."""
import urllib.request, urllib.parse, re, html, json, ssl

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def search(q, max_results=12):
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx, timeout=15)
        content = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return [{"error": str(e)}]
    
    results = []
    # Find result blocks
    blocks = re.findall(r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', content)
    snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</(?:a|span|div)', content)
    
    for i, (url, title) in enumerate(blocks):
        title = re.sub(r'<[^>]+>', '', title)
        title = html.unescape(title).strip()
        snippet = html.unescape(snippets[i]).strip() if i < len(snippets) else ""
        if title and url and 'duckduckgo.com' not in url:
            results.append({"title": title, "url": url, "snippet": snippet})
    
    return results

# All searches
queries = {
    "filmschool": [
        "AI video creation tutorial techniques 2026",
        "AI filmmaking workflow guide 2026",
        "text to video cinematic tips 2026",
    ],
    "industry": [
        "Runway Gen-4 Alpha latest 2026",
        "Sora OpenAI video generation 2026",
        "Kling Veo AI video milestone 2026",
        "Pika Labs AI video news 2026",
        "HailuoAI video generation 2026",
    ],
    "tools": [
        "AI video software tool release 2026",
        "new AI video generator launched 2026",
        "AI video editing tool 2026",
    ],
    "niches": [
        "AI video in demand niche 2026",
        "AI generated video content trends 2026",
        "AI video marketing brand 2026",
    ],
    "offers": [
        "sell AI generated videos monetize 2026",
        "AI video creator freelance marketplace 2026",
        "make money AI video content 2026",
    ],
    "inspire": [
        "AI generated film short award 2026",
        "best AI video art creative 2026",
        "AI film festival winner 2026",
    ],
}

all_results = {}
for category, qlist in queries.items():
    combined = []
    seen_urls = set()
    for q in qlist:
        res = search(q)
        for r in res:
            if "error" in r:
                continue
            # deduplicate
            clean_url = r["url"].split("?")[0].split("#")[0]
            if clean_url not in seen_urls and len(combined) < 20:
                seen_urls.add(clean_url)
                combined.append(r)
    all_results[category] = combined[:15]
    print(f"\n=== {category.upper()} ===")
    for r in combined[:12]:
        print(f"  {r['title']}")
        print(f"  {r['url']}")
        print(f"  {r['snippet'][:120]}...")
        print()

# Save raw results
with open("/home/faith/tech-pulse-server/_search_results.json", "w") as f:
    json.dump(all_results, f, indent=2)
print("\nSaved to _search_results.json")
