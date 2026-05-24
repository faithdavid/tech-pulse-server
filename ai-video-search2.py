#!/usr/bin/env python3
"""Phase 1 + Phase 2 search for AI Video Pulse using requests-based search."""
import json, sys, time, urllib.parse
import requests

def ddg_search(q, max_results=10):
    """Search DuckDuckGo using the Lite HTML version."""
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": q}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.post(url, data=data, headers=headers, timeout=10)
        r.raise_for_status()
        # Parse HTML results
        results = []
        import re
        # Find all result links in the DDG lite HTML
        lines = r.text.split('\n')
        current = {}
        for line in lines:
            if 'class="result-link"' in line or 'class="result-snippet"' in line:
                continue
        # Simpler approach - use text search
        # Extract links from <a> tags with result class
        html = r.text
        # Find result blocks
        blocks = re.findall(r'<tr[^>]*class="(?:result|result--more)"[^>]*>(.*?)</tr>', html, re.DOTALL)
        if not blocks:
            # Try alternate DDG layout
            blocks = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
        
        # Actually let's try the JSON API
        return ddg_json_api(q, max_results)
    except Exception as e:
        print(f"  ERROR Lite search '{q}': {e}", file=sys.stderr)
        return ddg_json_api(q, max_results)

def ddg_json_api(q, max_results=10):
    """Search DuckDuckGo using their instant answer API."""
    url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(q)}&format=json&no_html=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        results = []
        # RelatedTopics and Results
        for topic in data.get("RelatedTopics", []):
            if "Text" in topic and "FirstURL" in topic:
                results.append({
                    "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", "")[:80],
                    "body": topic.get("Text", ""),
                    "href": topic.get("FirstURL", "")
                })
            elif "Topics" in topic:
                for subtopic in topic.get("Topics", []):
                    if "Text" in subtopic and "FirstURL" in subtopic:
                        results.append({
                            "title": subtopic.get("Text", "").split(" - ")[0][:80],
                            "body": subtopic.get("Text", ""),
                            "href": subtopic.get("FirstURL", "")
                        })
        # Also search HTML
        if len(results) < max_results:
            results += ddg_html_search(q, max_results - len(results))
        return results[:max_results]
    except Exception as e:
        print(f"  ERROR JSON API '{q}': {e}", file=sys.stderr)
        return ddg_html_search(q, max_results)

def ddg_html_search(q, max_results=10):
    """HTML scraping fallback."""
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        import re
        html = r.text
        results = []
        # Find result links
        link_pattern = re.compile(r'<a[^>]*class="result__a"[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
        snippet_pattern = re.compile(r'class="result__snippet"[^>]*>(.*?)</(?:a|td|div)>', re.DOTALL)
        
        links = link_pattern.findall(html)
        snippets = snippet_pattern.findall(html)
        
        for i, (href, title_html) in enumerate(links):
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            snippet = ""
            if i < len(snippets):
                snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            if title:
                results.append({
                    "title": title[:100],
                    "body": snippet[:200],
                    "href": href
                })
        return results[:max_results]
    except Exception as e:
        print(f"  ERROR HTML search '{q}': {e}", file=sys.stderr)
        return []

# Phase 1: Broad searches
queries = {
    "filmschool": [
        "AI video filmmaking techniques 2026",
        "text to video AI cinematography 2026",
        "AI video creation workflow guide",
    ],
    "industry": [
        "Sora Runway AI video generation news",
        "AI video startup funding 2026",
        "Google Veo OpenAI Sora latest update",
    ],
    "tools": [
        "Runway Gen-4 AI video tool",
        "Pika Labs AI video update 2026",
        "Kling AI video generator new features",
    ],
    "niches": [
        "AI video content niche trends 2026",
        "demand for AI generated videos",
        "AI video creation market trends",
    ],
    "offers": [
        "monetize AI generated videos 2026",
        "sell AI video content freelance",
        "AI video creator income",
    ],
    "inspire": [
        "AI generated short film award 2026",
        "creative AI video projects showcase",
        "AI film festival 2026",
    ],
}

# Additional Phase 2 deep-dive queries
phase2_queries = {
    "filmschool": [
        "HailuoAI film techniques Runway director mode",
        "AI video prompt engineering camera movement",
    ],
    "industry": [
        "Runway Gen-4 release features",
        "Pika 2.0 PikaLabs updates",
        "Kling 1.6 Kling AI video latest",
    ],
    "tools": [
        "ElevenLabs video AI new tool",
        "AI video editor software 2026 launch",
    ],
    "niches": [
        "AI video ads marketing 2026",
        "AI short form video content creators",
    ],
    "offers": [
        "AI video production agency pricing",
        "sell AI videos stock footage",
    ],
    "inspire": [
        "best AI generated video 2026 viral",
        "AI music video generated 2026",
    ],
}

all_queries = {}
for cat in queries:
    all_queries[cat] = queries[cat] + phase2_queries.get(cat, [])

all_results = {}
for category, qlist in all_queries.items():
    print(f"\n=== {category} ===", file=sys.stderr)
    all_results[category] = []
    seen_urls = set()
    for q in qlist:
        print(f"  Searching: {q}", file=sys.stderr)
        results = ddg_search(q, max_results=5)
        fresh = 0
        for r in results:
            if r.get("href") and r["href"] not in seen_urls:
                seen_urls.add(r["href"])
                all_results[category].append(r)
                fresh += 1
        print(f"  Got {len(results)} results, {fresh} new", file=sys.stderr)
        time.sleep(0.3)
    
    # Print top results for this category
    print(f"\n  --- Top {category} results ---", file=sys.stderr)
    for r in all_results[category][:8]:
        print(f"  • {r.get('title','?')[:90]}", file=sys.stderr)
        print(f"    {r.get('body','?')[:130]}", file=sys.stderr)
        print(f"    {r.get('href','?')}", file=sys.stderr)
        print(file=sys.stderr)

# Save all results
with open("/tmp/phase2_results.json", "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print("\n\nAll results saved to /tmp/phase2_results.json", file=sys.stderr)
