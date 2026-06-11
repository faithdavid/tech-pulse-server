#!/usr/bin/env python3
"""One-shot RSS harvest for tech pulse when web_search is down."""
import json
import re
import xml.etree.ElementTree as ET
import urllib.request

IMAGES = {
    "ai": "https://images.unsplash.com/photo-1677442136019?w=600&q=60",
    "funding": "https://images.unsplash.com/photo-1611974789855?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1461749280684?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1519389950473?w=600&q=60",
    "oss": "https://images.unsplash.com/photo-1558494949?w=600&q=60",
}


def fetch(url):
    with urllib.request.urlopen(url, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def clean_title(t):
    t = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", t or "")
    return re.sub(r"\s+", " ", t).strip()


def parse_rss(xml_text, limit=20):
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall(".//item")[:limit]:
        title = clean_title(item.findtext("title", ""))
        link = (item.findtext("link") or "").strip()
        desc = item.findtext("description", "") or ""
        desc = re.sub(r"<[^>]+>", " ", desc)
        desc = re.sub(r"\s+", " ", desc).strip()[:400]
        if title and link:
            items.append({"title": title, "link": link, "desc": desc})
    return items


def mk(entry, source, cat):
    return {
        "title": entry["title"],
        "description": entry.get("desc", ""),
        "url": entry["link"],
        "source": source,
        "image_url": IMAGES[cat],
    }


def main():
    tc = parse_rss(fetch("https://techcrunch.com/feed/"), 30)
    by_cat = {"ai": [], "funding": [], "tools": [], "industry": [], "oss": []}

    ai_kw = ("ai", "anthropic", "openai", "xai", "grok", "claude", "chatbot", "generative", "doordash", "pool")
    fund_kw = ("ipo", "raises", "funding", "spac", "bond", "$", "million", "billion", "invest", "prices shares")
    tool_kw = ("tool", "app", "coinbase", "mcp", "agent", "homebrew", "coding", "developer", "bluesky")
    ind_kw = ("meta", "microsoft", "oracle", "google", "deezer", "regulation", "social media", "amazon", "security")

    for it in tc:
        t = it["title"].lower()
        if any(k in t for k in ai_kw) and len(by_cat["ai"]) < 4:
            by_cat["ai"].append(mk(it, "TechCrunch", "ai"))
        elif any(k in t for k in fund_kw) and len(by_cat["funding"]) < 4:
            by_cat["funding"].append(mk(it, "TechCrunch", "funding"))
        elif any(k in t for k in tool_kw) and len(by_cat["tools"]) < 4:
            by_cat["tools"].append(mk(it, "TechCrunch", "tools"))
        elif any(k in t for k in ind_kw) and len(by_cat["industry"]) < 4:
            by_cat["industry"].append(mk(it, "TechCrunch", "industry"))

    for it in tc:
        if len(by_cat["industry"]) >= 4:
            break
        if not any(x["url"] == it["link"] for x in by_cat["industry"]):
            by_cat["industry"].append(mk(it, "TechCrunch", "industry"))

    hn = parse_rss(fetch("https://hnrss.org/newest?q=AI&count=20"), 15)
    for it in hn:
        if len(by_cat["ai"]) >= 4:
            break
        if it["link"] not in {x["url"] for x in by_cat["ai"]}:
            by_cat["ai"].append(mk(it, "Hacker News", "ai"))

    hf = parse_rss(fetch("https://huggingface.co/blog/feed.xml"), 8)
    for it in hf[:4]:
        by_cat["oss"].append(mk(it, "Hugging Face", "oss"))

    gh = parse_rss(fetch("https://hnrss.org/newest?q=github.com&count=15"), 10)
    for it in gh:
        if len(by_cat["oss"]) >= 4:
            break
        if "github.com" in it["link"]:
            by_cat["oss"].append(mk(it, "GitHub", "oss"))

    for cat in by_cat:
        while len(by_cat[cat]) < 4 and tc:
            for it in tc:
                if len(by_cat[cat]) >= 4:
                    break
                if it["link"] not in {x["url"] for x in by_cat[cat]}:
                    by_cat[cat].append(mk(it, "TechCrunch", cat))

    out = {k: v[:4] for k, v in by_cat.items()}
    path = "/home/ubuntu/tech-pulse-server/pulse-data.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", path, {k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()