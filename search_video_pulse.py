#!/usr/bin/env python3
"""AI Video Pulse — Web search scraper for all 6 categories using DuckDuckGo HTML."""

import urllib.request
import urllib.parse
import json
import re
import time

# Each category with its search queries
CATEGORY_QUERIES = {
    "filmschool": [
        "AI filmmaking techniques workflow 2026",
        "AI cinema camera movement storytelling 2026",
        "generative AI film production tutorial 2026",
        "Runway Kling Pika filmmaking tips 2026",
    ],
    "industry": [
        "AI video platform news May 2026",
        "AI video generation funding investment 2026",
        "OpenAI Sora update 2026",
        "Runway Gen-4 AI video release 2026",
    ],
    "tools": [
        "new AI video generator editor 2026",
        "AI video editing tool launch 2026",
        "text to video AI tool May 2026",
        "AI video creation software review 2026",
    ],
    "niches": [
        "AI video art trends 2026",
        "AI generated music video style 2026",
        "cinematic AI video aesthetic 2026",
        "AI short film viral trend 2026",
    ],
    "offers": [
        "AI video freelance pricing 2026",
        "AI filmmaker client strategy Upwork 2026",
        "selling AI video production services 2026",
        "AI video creator business rates 2026",
    ],
    "inspire": [
        "best AI generated short films 2026",
        "AI filmmaker notable work 2026",
        "award winning AI film 2026",
        "viral AI video creator 2026",
    ],
}

def search_duckduckgo(query, max_results=5):
    """Search DuckDuckGo HTML and parse results."""
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Error searching '{query}': {e}")
        return []
    
    results = []
    
    # Parse result blocks
    # Each result is in a div with class "result" or "result results_links_deep"
    # Title in h2 class="result__title" > a
    # URL in a class="result__url"
    # Snippet in a class="result__snippet"
    
    # Find all result blocks
    result_blocks = re.findall(
        r'<div[^>]*class="result[^"]*"[^>]*>(.*?)</div>\s*</div>',
        html, re.DOTALL
    )
    
    if not result_blocks:
        # Try alternate pattern (deeper results)
        result_blocks = re.findall(
            r'<div[^>]*class="result\b[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>',
            html, re.DOTALL
        )
    
    if not result_blocks:
        # Fallback: find all links with result__a class
        result_blocks = re.findall(
            r'<a[^>]*class="result__a"[^>]*>(.*?)</a>\s*<a[^>]*class="result__url"[^>]*href="([^"]*)"',
            html, re.DOTALL
        )
        for title_html, url_str in result_blocks[:max_results]:
            title = re.sub(r'<[^>]+>', '', title_html).strip()
            title = re.sub(r'\s+', ' ', title)
            results.append({"title": title, "url": url_str, "snippet": ""})
        
        if results:
            return results
    
    seen_urls = set()
    for block in result_blocks[:max_results * 2]:
        # Extract title from result__a
        title_match = re.search(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', block)
        if not title_match:
            continue
        
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        title = re.sub(r'\s+', ' ', title)
        
        # Extract URL from result__url
        url_match = re.search(r'<a[^>]*class="result__url"[^>]*href="([^"]*)"', block)
        if not url_match:
            continue
        url = url_match.group(1)
        
        # Skip duplicates and non-http URLs
        if url in seen_urls or not url.startswith("http"):
            continue
        seen_urls.add(url)
        
        # Extract snippet
        snippet_match = re.search(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', block)
        snippet = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip() if snippet_match else ""
        snippet = re.sub(r'\s+', ' ', snippet)
        
        results.append({
            "title": title,
            "url": url,
            "snippet": snippet
        })
        
        if len(results) >= max_results:
            break
    
    return results

def deduplicate(results):
    """Remove near-duplicate results by URL domain+title similarity."""
    seen = set()
    unique = []
    for r in results:
        key = r["url"].split("//")[-1].split("/")[0] + "|" + r["title"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique

def categorize_story(result, category):
    """Convert a raw search result into a story dict for our data format."""
    title = result["title"]
    snippet = result.get("snippet", "")
    url = result["url"]
    
    # Derive source from URL
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    source = domain.replace("www.", "").split(".")[0].title()
    
    return {
        "title": title,
        "description": snippet[:300] if snippet else f"Latest development in AI video ({category}).",
        "url": url,
        "source": source,
        "image_url": ""
    }

# === MAIN ===
all_data = {cat: [] for cat in CATEGORY_QUERIES}

for category, queries in CATEGORY_QUERIES.items():
    print(f"\n{'='*60}")
    print(f"CATEGORY: {category}")
    print(f"{'='*60}")
    
    all_results = []
    for query in queries:
        print(f"  Searching: {query}")
        results = search_duckduckgo(query, max_results=4)
        print(f"    Found {len(results)} results")
        all_results.extend(results)
        time.sleep(0.3)  # Be polite
    
    # Deduplicate
    all_results = deduplicate(all_results)
    print(f"  Total unique results: {len(all_results)}")
    
    # Convert to story format (take top 4)
    stories = [categorize_story(r, category) for r in all_results[:4]]
    all_data[category] = stories

# Write the data file
output_path = "/home/faith/tech-pulse-server/ai-video-data.json"
with open(output_path, "w") as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"Data written to {output_path}")
print(f"Total stories: {sum(len(v) for v in all_data.values())}")
for cat, stories in all_data.items():
    print(f"  {cat}: {len(stories)} stories")
