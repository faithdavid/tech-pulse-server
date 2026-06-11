#!/usr/bin/env python3
"""Harvest AI Video Pulse data from HN Algolia + RSS when web_search/DDG fail."""
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

OUT = "/home/ubuntu/tech-pulse-server/ai-video-data.json"

IMAGES = {
    "filmschool": "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&q=60",
    "industry": "https://images.unsplash.com/photo-1558494949-ef0d38d3f9e2?w=600&q=60",
    "tools": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&q=60",
    "niches": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=600&q=60",
    "offers": "https://images.unsplash.com/photo-1607083206869-4c6d35b4c5f3?w=600&q=60",
    "inspire": "https://images.unsplash.com/photo-1478720568477-152d9b164e26?w=600&q=60",
}

CATEGORY_QUERIES = {
    "filmschool": ["Runway AI film", "AI filmmaking", "generative video cinema", "Sora filmmaking"],
    "industry": ["Sora OpenAI video", "Runway video AI", "AI video generation", "Veo Google video"],
    "tools": ["text to video AI", "Kling video", "Pika video AI", "Synthesia video"],
    "niches": ["AI YouTube video", "faceless YouTube AI", "AI video marketing", "AI short video"],
    "offers": ["AI video freelance", "AI video production business", "HeyGen", "Invideo AI"],
    "inspire": ["AI generated film", "Runway film festival", "AI short film", "generative video art"],
}

CAT_KEYWORDS = {
    "filmschool": ("film", "filmmak", "cinema", "storyboard", "director", "festival", "workflow", "tutorial", "hybrid"),
    "industry": ("openai", "runway", "google", "veo", "sora", "funding", "studio", "platform", "market", "hollywood"),
    "tools": ("tool", "generator", "editor", "launch", "release", "api", "software", "kling", "pika", "heygen"),
    "niches": ("youtube", "niche", "marketing", "vertical", "creator", "shorts", "faceless", "advertis"),
    "offers": ("pricing", "freelance", "monetiz", "upwork", "agency", "sell", "coupon", "business", "client"),
    "inspire": ("award", "festival", "viral", "showcase", "creative", "art", "winner", "cinematic"),
}


def hn_search(query, hits=12):
    url = (
        "https://hn.algolia.com/api/v1/search?"
        + urllib.parse.urlencode({"query": query, "tags": "story", "hitsPerPage": hits})
    )
    req = urllib.request.Request(url, headers={"User-Agent": "AIVideoPulse/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []
    out = []
    for h in data.get("hits", []):
        title = (h.get("title") or "").strip()
        story_url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID', '')}"
        if not title:
            continue
        parsed = urlparse(story_url)
        source = parsed.netloc.replace("www.", "") if parsed.netloc else "Hacker News"
        out.append(
            {
                "title": title,
                "url": story_url,
                "source": source.split(".")[0].title() if source != "Hacker News" else "Hacker News",
                "points": h.get("points", 0),
            }
        )
    return out


def score_for_cat(title, cat):
    t = title.lower()
    return sum(1 for kw in CAT_KEYWORDS[cat] if kw in t)


def mk_story(item, cat, desc=""):
    return {
        "title": item["title"],
        "description": desc or f"Recent discussion: {item['title'][:200]}",
        "url": item["url"],
        "source": item["source"],
        "image_url": IMAGES[cat],
    }


def fetch_meta_desc(url):
    if "news.ycombinator.com" in url:
        return ""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AIVideoPulse/1.0)"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return ""
    for pat in [
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)',
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)',
    ]:
        m = re.search(pat, html, re.I)
        if m:
            d = re.sub(r"\s+", " ", m.group(1)).strip()
            return d[:320] if d else ""
    return ""


def parse_rss(url, limit=25):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            xml = r.read().decode("utf-8", errors="replace")
        root = ET.fromstring(xml)
    except Exception:
        return []
    items = []
    for item in root.findall(".//item")[:limit]:
        title = re.sub(r"\s+", " ", (item.findtext("title") or "")).strip()
        link = (item.findtext("link") or "").strip()
        desc = item.findtext("description", "") or ""
        desc = re.sub(r"<[^>]+>", " ", desc)
        desc = re.sub(r"\s+", " ", desc).strip()[:320]
        if title and link:
            items.append({"title": title, "url": link, "description": desc, "source": "TechCrunch"})
    return items


def main():
    by_cat = {c: [] for c in CATEGORY_QUERIES}
    seen = {c: set() for c in CATEGORY_QUERIES}

    for cat, queries in CATEGORY_QUERIES.items():
        pool = []
        for q in queries:
            for hit in hn_search(q, 10):
                if hit["url"] in seen[cat]:
                    continue
                hit["_score"] = score_for_cat(hit["title"], cat) + (hit.get("points", 0) / 50)
                pool.append(hit)
        pool.sort(key=lambda x: x["_score"], reverse=True)
        for hit in pool:
            if len(by_cat[cat]) >= 4:
                break
            if hit["url"] in seen[cat]:
                continue
            seen[cat].add(hit["url"])
            desc = fetch_meta_desc(hit["url"])
            by_cat[cat].append(mk_story(hit, cat, desc))

    # RSS top-up for industry/tools
    video_kw = ("video", "sora", "runway", "veo", "kling", "generative", "filmm", "heygen")
    try:
        for entry in parse_rss("https://techcrunch.com/feed/", 40):
            t = entry["title"].lower()
            if not any(k in t for k in video_kw):
                continue
            for cat in ("industry", "tools", "filmschool"):
                if len(by_cat[cat]) >= 4:
                    continue
                if entry["url"] in seen[cat]:
                    continue
                if score_for_cat(entry["title"], cat) >= 1 or cat == "industry":
                    seen[cat].add(entry["url"])
                    by_cat[cat].append(
                        {
                            "title": entry["title"],
                            "description": entry.get("description") or entry["title"],
                            "url": entry["url"],
                            "source": "TechCrunch",
                            "image_url": IMAGES[cat],
                        }
                    )
    except Exception:
        pass

    # Fallback: merge curated rows from previous pulse if category thin
    fallback_path = OUT
    try:
        with open(fallback_path) as f:
            prev = json.load(f)
    except Exception:
        prev = {}

    for cat in by_cat:
        while len(by_cat[cat]) < 4 and prev.get(cat):
            for story in prev[cat]:
                if story["url"] not in seen[cat]:
                    seen[cat].add(story["url"])
                    by_cat[cat].append(story)
                    if len(by_cat[cat]) >= 4:
                        break
            break

    out = {k: v[:4] for k, v in by_cat.items()}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print("wrote", OUT, {k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()