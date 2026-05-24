#!/usr/bin/env python3
"""Fetch article details for selected stories and build final pulse-data.json."""
import json, time, sys, re
from urllib.request import urlopen, Request

# Selected stories with URLs to enrich
stories_to_enrich = [
    # AI
    {"cat": "ai", "title": "OpenAI launches ChatGPT for Personal Finance, lets you connect bank accounts", "url": "https://techcrunch.com/2026/05/15/openai-launches-chatgpt-for-personal-finance-w"},
    {"cat": "ai", "title": "Runway started by helping filmmakers — now wants to beat Google at AI", "url": "https://techcrunch.com/2026/05/15/runway-started-by-helping-filmmakers-now-it-wa"},
    {"cat": "ai", "title": "OpenAI says Codex is coming to your phone", "url": "https://techcrunch.com/2026/05/14/openai-says-codex-is-coming-to-your-phone/"},
    {"cat": "ai", "title": "What happens when AI starts building itself?", "url": "https://techcrunch.com/2026/05/14/what-happens-when-ai-starts-building-itself/"},
    # Funding
    {"cat": "funding", "title": "Cerebras raises $5.5B, stock pops 108% — first huge tech IPO of 2026", "url": "https://techcrunch.com/2026/05/14/cerebras-raises-5-5b-kicking-off-2026s-ipo-sea"},
    {"cat": "funding", "title": "Anduril raises $5B, doubles valuation to $61B", "url": "https://techcrunch.com/2026/05/13/anduril-raises-5b-doubles-valuation-to-61b/"},
    {"cat": "funding", "title": "Kevin Hartz's A* closes third fund with $450M", "url": "https://techcrunch.com/2026/05/12/kevin-hartzs-a-just-closed-its-third-fund-with"},
    {"cat": "funding", "title": "Lovable backs company bringing vibe coding to hardware", "url": "https://techcrunch.com/2026/05/14/lovable-just-backed-a-company-thats-looking-to"},
    # Tools
    {"cat": "tools", "title": "Clawdmeter turns Claude Code usage into desktop dashboard", "url": "https://techcrunch.com/2026/05/14/clawdmeter-turns-your-claude-code-usage-stats-"},
    {"cat": "tools", "title": "Osaurus brings local and cloud AI models to your Mac", "url": "https://techcrunch.com/2026/05/15/osaurus-brings-both-local-and-cloud-ai-models-"},
    # Industry
    {"cat": "industry", "title": "Cisco cuts nearly 4,000 jobs to spend more on AI", "url": "https://techcrunch.com/2026/05/14/cisco-cuts-nearly-4000-jobs-to-spend-more-on-a"},
    {"cat": "industry", "title": "OpenAI feels burned by Apple's crappy ChatGPT integration", "url": "https://arstechnica.com/tech-policy/2026/05/openai-feels-burned-by-apples-crappy"},
    {"cat": "industry", "title": "SV vacationland needs new energy provider as AI drives prices up", "url": "https://techcrunch.com/2026/05/15/silicon-valleys-vacationland-needs-a-new-energ"},
    {"cat": "industry", "title": "US DOJ demands Apple and Google unmask over 100k users", "url": "https://macdailynews.com/2026/05/15/u-s-doj-demands-apple-and-google-unmask-over"},
    # OSS
    {"cat": "oss", "title": "Image-blaster creates 3D environments from single image", "url": "https://github.com/neilsonnn/image-blaster"},
    {"cat": "oss", "title": "Linux bitten by second severe vulnerability in as many weeks", "url": "https://arstechnica.com/security/2026/05/linux-bitten-by-second-severe-vulnerabi"},
]

def fetch_text(url):
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; TechPulseBot)'})
        resp = urlopen(req, timeout=15)
        data = resp.read().decode('utf-8', errors='replace')
        # Extract text content roughly
        text = re.sub(r'<script[^>]*>.*?</script>', '', data, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:2000]  # First 2000 chars
    except Exception as e:
        return f"Error: {e}"

for s in stories_to_enrich:
    print(f"Fetching: {s['title'][:60]}...", file=sys.stderr)
    content = fetch_text(s['url'])
    s['content'] = content[:1500]
    time.sleep(0.5)

# Save enriched data
with open("/home/faith/tech-pulse-server/enriched_stories.json", "w") as f:
    json.dump(stories_to_enrich, f, indent=2)

print(f"\nEnriched {len(stories_to_enrich)} stories", file=sys.stderr)
