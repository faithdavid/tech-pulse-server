#!/usr/bin/env python3
"""Fetch descriptions for key stories + build final data"""
import json
import sys
import re
import urllib.request
from urllib.parse import urlparse

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,*/*'
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            encoding = resp.headers.get_content_charset() or 'utf-8'
            return data.decode(encoding, errors='replace')
    except:
        return None

def extract_og(html, prop):
    if not html: return ""
    m = re.search(rf'<meta[^>]*(?:property|name)=["\'](?:og:)?{prop}["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m: return m.group(1).strip()
    m = re.search(rf'<meta[^>]*name=["\']{prop}["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m: return m.group(1).strip()
    return ""

def extract_title(html):
    t = extract_og(html, "title")
    if t: return t
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
    if m: return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    return ""

def extract_desc(html):
    d = extract_og(html, "description")
    if d: return d
    m = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
    if m: return m.group(1).strip()
    return ""

# Stories to fetch details for
stories = {
    # AI Breakthroughs
    "chatgpt_5.5": "https://gowers.wordpress.com/2026/05/08/a-recent-experience-with-chatgpt-5-5-pro/",
    "needle_model": "https://github.com/cactus-compute/needle",
    "socher_ai": "https://techcrunch.com/2026/05/14/what-happens-when-ai-starts-building-itself/",
    "claude_small_biz": "https://www.anthropic.com/news/claude-for-small-business",
    "local_ai_norm": "https://unix.foo/posts/local-ai-needs-to-be-norm/",
    "codex_mobile": "https://openai.com/index/codex-chatgpt-mobile/",
    
    # Funding
    "openai_122b": "https://www.cnbc.com/2026/03/31/openai-funding-round-ipo.html",
    "anthropic_30b": "https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation",
    "cerebras_ipo": "https://techcrunch.com/2026/05/14/cerebras-ipo-makes-billions-for-benchmark-but-vc-eric-vishria-almost-didnt-take-the-meeting/",
    
    # Dev Tools
    "bun_rust": "https://github.com/oven-sh/bun/pull/30412",
    "claude_code_html": "https://twitter.com/trq212/status/2052809885763747935",
    "ai_code_why_python": "https://medium.com/@NMitchem/if-ai-writes-your-code-why-use-python-bf8c4ba1a055",
    "local_llm_benchmark": "https://news.ycombinator.com/item?id=47680922",
    
    # Industry
    "openai_apple": "https://techcrunch.com/2026/05/14/openai-is-reportedly-preparing-legal-action-against-apple-it-wouldnt-be-the-first-partner-to-feel-burned/",
    "eu_addictive_design": "https://www.cnbc.com/2026/05/12/tiktok-instagram-social-media-addictive-eu-crack-down.html",
    "macos_m5_exploit": "https://news.ycombinator.com/item?id=47682237",
    "ngnix_exploit": "https://news.ycombinator.com/item?id=47682185",
    "gitlab_reduction": "https://about.gitlab.com/blog/gitlab-act-2/",
    "uk_palantir_replaced": "https://news.ycombinator.com/item?id=47682417",
    
    # Open Source
    "bambu_lab": "https://www.jeffgeerling.com/blog/2026/bambu-lab-abusing-open-source-social-contract/",
    "tanstack_postmortem": "https://tanstack.com/blog/npm-supply-chain-compromise-postmortem",
    "forgejo_move": "https://jorijn.com/en/blog/leaving-github-for-forgejo/",
    "internet_archive_ch": "https://blog.archive.org/2026/05/06/internet-archive-switzerland-expanding-a-global-mission-to-preserve-knowledge/",
    "ratty_term": "https://ratty-term.org/",
}

print("=== Fetching story details ===", file=sys.stderr)
details = {}
for key, url in stories.items():
    print(f"  {key}...", file=sys.stderr)
    html = fetch_url(url)
    if html:
        title = extract_title(html)
        desc = extract_desc(html)
        if not desc:
            # Try first paragraph
            m = re.search(r'<p[^>]*>(.*?)</p>', html, re.DOTALL)
            if m:
                desc = re.sub(r'<[^>]+>', '', m.group(1)).strip()[:300]
        details[key] = {"title": title, "description": desc, "url": url}
        print(f"    OK: {title[:60]}", file=sys.stderr)
    else:
        details[key] = {"title": key, "description": "", "url": url}
        print(f"    FAIL", file=sys.stderr)

print("\n=== RESULTS ===", file=sys.stderr)
print(json.dumps(details, indent=2))
