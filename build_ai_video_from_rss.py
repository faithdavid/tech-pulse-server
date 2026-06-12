#!/usr/bin/env python3
"""RSS harvest for AI Video Pulse when web_search is down."""
import json
import re
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse

IMAGES = {
    "filmschool": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1558494949-ef0d38d3f9e2?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=60",
    "niches": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=600&q=60",
    "offers": "https://images.unsplash.com/photo-1607083206869-4c6d35b4c5f3?w=600&q=60",
    "inspire": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&q=60",
}

QUERIES = {
    "filmschool": "AI filmmaking film school video generation",
    "industry": "AI video Hollywood studio Runway Kling",
    "tools": "AI video generator software 2026",
    "niches": "AI video YouTube creator marketing",
    "offers": "AI video startup funding deal",
    "inspire": "AI film festival generative video art",
}


def gnews_url(q):
    enc = urllib.parse.quote(q)
    return (
        f"https://news.google.com/rss/search?q={enc}&hl=en-US&gl=US&ceid=US:en"
    )


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", errors="replace")


def clean_title(t):
    t = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", t or "")
    t = re.sub(r"\s+-\s+[^-]+$", "", t)  # trim trailing " - Source"
    return re.sub(r"\s+", " ", t).strip()


def parse_rss(xml_text, limit=12):
    root = ET.fromstring(xml_text)
    items = []
    for item in root.findall(".//item")[:limit]:
        title = clean_title(item.findtext("title", ""))
        link = (item.findtext("link") or "").strip()
        desc = item.findtext("description", "") or ""
        desc = re.sub(r"<[^>]+>", " ", desc)
        desc = re.sub(r"\s+", " ", desc).strip()[:400]
        src = item.findtext("source", "") or ""
        if not src and " - " in title:
            parts = title.rsplit(" - ", 1)
            if len(parts) == 2:
                title, src = parts[0].strip(), parts[1].strip()
        if title and link:
            items.append({"title": title, "link": link, "desc": desc, "source": src})
    return items


def mk(entry, cat):
    source = entry.get("source") or "Google News"
    return {
        "title": entry["title"],
        "description": entry.get("desc", entry["title"]),
        "url": entry["link"],
        "source": source,
        "image_url": IMAGES[cat],
    }


def main():
    out = {k: [] for k in QUERIES}
    seen = set()
    for cat, q in QUERIES.items():
        try:
            items = parse_rss(fetch(gnews_url(q)), 15)
        except Exception as e:
            print("warn", cat, e)
            continue
        for it in items:
            if it["link"] in seen:
                continue
            if len(out[cat]) >= 4:
                break
            seen.add(it["link"])
            out[cat].append(mk(it, cat))

    path = "/home/ubuntu/tech-pulse-server/ai-video-data.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", path, {k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()