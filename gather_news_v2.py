#!/usr/bin/env python3
"""Tech Pulse 24/7 v2 — Improved news gathering"""
import json
import sys
import re
from datetime import datetime, timezone
from urllib.parse import urlparse
from duckduckgo_search import DDGS

CATEGORY_QUERIES = {
    "ai": [
        "new AI model released 2026 breakthrough",
        "AI research announcement milestone 2026",
        "latest GPT Claude Gemini model update 2026",
        "generative AI news this week 2026"
    ],
    "funding": [
        "AI startup raises funding round 2026",
        "tech startup valuation funding news 2026",
        "venture capital AI investment 2026",
        "Series A B C funding tech AI 2026"
    ],
    "tools": [
        "new developer tool launch 2026 programming",
        "AI coding assistant tool release 2026",
        "IDE framework release 2026 developer",
        "software engineering tool new 2026"
    ],
    "industry": [
        "big tech company news 2026 latest",
        "AI legislation regulation update 2026",
        "tech industry antitrust policy 2026",
        "cloud AWS Azure Google announcement 2026"
    ],
    "oss": [
        "open source AI project launch 2026 GitHub",
        "open source release notable 2026",
        "new open source foundation project 2026",
        "open source LLM model release 2026"
    ]
}

# Sites to prefer for tech news
PREFERRED_DOMAINS = [
    "techcrunch.com", "theverge.com", "arstechnica.com", "wired.com",
    "zdnet.com", "venturebeat.com", "9to5google.com", "9to5mac.com",
    "cnbc.com", "bloomberg.com", "reuters.com", "axios.com",
    "theinformation.com", "analyticsindiamag.com", "marktechpost.com",
    "github.com", "huggingface.co", "pytorch.org", "tensorflow.org",
    "news.ycombinator.com", "theregister.com", "infoworld.com",
    "dev.to", "stackoverflow.blog", "github.blog",
    "openai.com", "anthropic.com", "google.ai", "meta.ai",
    "mistral.ai", "cohere.com", "databricks.com"
]

def is_preferred(result):
    url = result.get("url", "")
    for domain in PREFERRED_DOMAINS:
        if domain in url:
            return True
    return False

def is_good_result(result):
    """Filter out non-news results like Wikipedia, dictionaries, etc."""
    url = result.get("url", "")
    title = result.get("title", "")
    body = result.get("body", "")
    
    # Skip if too short
    if len(title) < 10 and len(body) < 20:
        return False
    
    # Skip generic/definition pages
    skip_domains = [
        "wikipedia.org", "wiktionary.org", "merriam-webster.com",
        "collinsdictionary.com", "dictionary.com", "britannica.com",
        "thesaurus.com", "cambridge.org", "oxford.com",
        "deepai.org/chat"
    ]
    for skip in skip_domains:
        if skip in url:
            return False
    
    # Skip generic "What is X" pages
    if re.match(r'^(what|what is|what are|define|definition|meaning of)', title.lower()):
        return False
    
    return True

def search_category(queries, max_per_query=8):
    """Search for news across multiple queries per category"""
    results = []
    seen_urls = set()
    
    try:
        with DDGS() as ddgs:
            for query in queries:
                try:
                    for r in ddgs.text(
                        query,
                        max_results=max_per_query,
                        region="wt-wt",  # worldwide
                        safesearch="moderate",
                        timelimit="m"  # past month
                    ):
                        url = r.get("href", "")
                        if not url or url in seen_urls:
                            continue
                        seen_urls.add(url)
                        title = r.get("title", "").strip()
                        body = r.get("body", "").strip()
                        
                        # Extract source
                        domain = urlparse(url).netloc
                        source = domain.replace("www.", "")
                        
                        results.append({
                            "title": title,
                            "description": body,
                            "url": url,
                            "source": source
                        })
                except Exception as e:
                    print(f"  Query '{query[:50]}...' error: {e}", file=sys.stderr)
    except Exception as e:
        print(f"DDGS init error: {e}", file=sys.stderr)
    
    return results

def score_and_sort(results):
    """Score results by relevance and prefer tech news sources"""
    for r in results:
        score = 0
        if is_preferred(r):
            score += 3
        if is_good_result(r):
            score += 2
        desc = r.get("description", "")
        # Prefer results with longer descriptions (more substantive)
        score += min(len(desc) / 200, 2)
        r["_score"] = score
    
    # Sort by score descending
    results.sort(key=lambda x: x["_score"], reverse=True)
    return results

def try_fetch_titles(urls):
    """Try to get better titles/descriptions from pages we can access"""
    import requests
    from bs4 import BeautifulSoup
    
    enriched = []
    for item in urls:
        url = item["url"]
        if not url.startswith("http"):
            enriched.append(item)
            continue
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9"
            }
            resp = requests.get(url, timeout=8, headers=headers, allow_redirects=True)
            if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                soup = BeautifulSoup(resp.text, "html.parser")
                
                # Try to get a better title
                og_title = soup.find("meta", property="og:title")
                if og_title and og_title.get("content"):
                    item["title"] = og_title["content"].strip()
                
                # Try to get a better description
                og_desc = soup.find("meta", property="og:description")
                if og_desc and og_desc.get("content"):
                    item["description"] = og_desc["content"].strip()
                else:
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        item["description"] = meta_desc["content"].strip()
        except:
            pass
        enriched.append(item)
    
    return enriched

def main():
    all_data = {}
    
    for category, queries in CATEGORY_QUERIES.items():
        print(f"\n=== Searching: {category} ===", file=sys.stderr)
        results = search_category(queries)
        print(f"  Raw results: {len(results)}", file=sys.stderr)
        
        results = score_and_sort(results)
        
        # Take top 8 after scoring
        results = results[:8]
        
        # Try to fetch better metadata from the actual pages (only for top 4)
        # results = try_fetch_titles(results)
        
        for r in results:
            print(f"  [{r.get('_score', 0):.1f}] {r['source']:30s} | {r['title'][:70]}", file=sys.stderr)
            del r["_score"]
        
        all_data[category] = results
    
    print(json.dumps(all_data, indent=2))

if __name__ == "__main__":
    main()
