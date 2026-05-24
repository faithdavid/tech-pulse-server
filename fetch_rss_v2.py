#!/usr/bin/env python3
"""Fetch tech news via RSS feeds using feedparser."""
import json, time, sys
import feedparser

feeds = [
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("TechCrunch Startups", "https://techcrunch.com/category/startups/feed/"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ("Hacker News", "https://hnrss.org/frontpage?count=30"),
    ("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
]

all_items = []
seen_urls = set()

for name, url in feeds:
    print(f"Fetching: {name}...", file=sys.stderr)
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            link = entry.get("link", "")
            title = entry.get("title", "")
            if link and link not in seen_urls and title:
                seen_urls.add(link)
                desc = entry.get("summary", entry.get("description", ""))
                # Strip HTML
                import re
                desc = re.sub(r'<[^>]+>', '', desc)
                desc = desc[:300]
                all_items.append({
                    "title": title,
                    "description": desc,
                    "url": link,
                    "source": link.split("/")[2] if link else name,
                    "feed": name
                })
        print(f"  Got {len(feed.entries[:15])} entries", file=sys.stderr)
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
    time.sleep(0.3)

# Save all items
with open("/home/faith/tech-pulse-server/rss_raw.json", "w") as f:
    json.dump(all_items, f, indent=2)

print(f"\n=== TOTAL RSS ITEMS: {len(all_items)} ===", file=sys.stderr)

# Categorize items based on content
categories = {
    "ai": [],
    "funding": [],
    "tools": [],
    "industry": [],
    "oss": []
}

ai_keywords = r'\b(AI|artificial intelligence|machine learning|deep learning|LLM|GPT|Claude|Gemini|neural network|transformer|language model|openAI|anthropic|Hugging Face)\b'
funding_keywords = r'\b(raised|funding|series [A-Z]|million|billion|valuation|investor|venture capital|startup|IPO|acquire)\b'
tools_keywords = r'\b(developer tool|IDE|framework|VS Code|copilot|Cursor|Windsurf|programming|coding|developer|library|SDK|API|platform)\b'
industry_keywords = r'\b(regulation|policy|EU AI Act|law|government|antitrust|earnings|revenue|layoff|hire|partnership|Microsoft|Google|Apple|Meta|Amazon)\b'
oss_keywords = r'\b(open source|Llama|Mistral|PyTorch|TensorFlow|kubernetes|docker|linux|git|github|repository|MIT license|Apache license)\b'

import re
for item in all_items:
    text = (item['title'] + " " + item['description']).lower()
    
    # Score each category
    scores = {
        "ai": len(re.findall(ai_keywords, text, re.I)),
        "funding": len(re.findall(funding_keywords, text, re.I)),
        "tools": len(re.findall(tools_keywords, text, re.I)),
        "industry": len(re.findall(industry_keywords, text, re.I)),
        "oss": len(re.findall(oss_keywords, text, re.I))
    }
    
    # Assign to best category (min score threshold of 1)
    best_cat = max(scores, key=scores.get)
    if scores[best_cat] >= 1:
        categories[best_cat].append(item)

# Deduplicate within categories by URL
for cat in categories:
    seen = set()
    unique = []
    for item in categories[cat]:
        if item['url'] not in seen:
            seen.add(item['url'])
            unique.append(item)
    categories[cat] = unique

# Print categorized results
for cat, items in categories.items():
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  {cat.upper()} ({len(items)} articles)", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    for item in items[:8]:
        print(f"  • {item['title'][:120]}", file=sys.stderr)
        print(f"    {item['url'][:80]}", file=sys.stderr)
        print(f"    [{item['feed']}]", file=sys.stderr)

# Save categorized
with open("/home/faith/tech-pulse-server/rss_categorized.json", "w") as f:
    json.dump(categories, f, indent=2)
