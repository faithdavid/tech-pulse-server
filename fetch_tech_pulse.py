#!/usr/bin/env python3
"""Tech Pulse — Bing search scraper (no web_search MCP)."""
import json, time, requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, quote

OUT = "/home/ubuntu/tech-pulse-server/pulse-data.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/125.0.0.0 Safari/537.36"}
session = requests.Session()
session.headers.update(HEADERS)

IMAGES = [
    "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&q=60",
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=600&q=60",
    "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=600&q=60",
    "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&q=60",
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=60",
    "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&q=60",
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=600&q=60",
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&q=60",
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=60",
    "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=600&q=60",
]

QUERIES = {
    "ai": [
        "AI model breakthrough research June 2026",
        "Anthropic OpenAI Google AI release 2026",
    ],
    "funding": [
        "AI startup funding round 2026 million",
        "AI company IPO acquisition 2026",
    ],
    "tools": [
        "developer tools AI framework release 2026",
        "GitHub Copilot VS Code AI coding 2026",
    ],
    "industry": [
        "AI regulation Big Tech 2026 news",
        "EU AI Act Microsoft Google AI 2026",
    ],
    "oss": [
        "open source LLM Hugging Face 2026",
        "Meta Llama Mistral open weights 2026",
    ],
}


def bing(q, n=5):
    url = f"https://www.bing.com/search?q={quote(q)}&count=12"
    r = session.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for li in soup.select("#b_results > li.b_algo"):
        h2 = li.select_one("h2 a")
        p = li.select_one(".b_caption p")
        if not h2:
            continue
        title = h2.get_text(strip=True)
        href = h2.get("href", "")
        snip = p.get_text(strip=True) if p else ""
        if href.startswith("http"):
            out.append({"title": title, "url": href, "snippet": snip})
        if len(out) >= n:
            break
    return out


def source_from(url):
    d = urlparse(url).netloc.replace("www.", "")
    return d.split(".")[0].title() if d else "Web"


def main():
    data = {k: [] for k in QUERIES}
    seen = {k: set() for k in QUERIES}
    img_i = 0
    for cat, ql in QUERIES.items():
        for q in ql:
            for r in bing(q, 4):
                u = r["url"]
                if u in seen[cat]:
                    continue
                seen[cat].add(u)
                desc = (r["snippet"] or r["title"])[:320]
                data[cat].append(
                    {
                        "title": r["title"],
                        "description": desc,
                        "url": u,
                        "source": source_from(u),
                        "image_url": IMAGES[img_i % len(IMAGES)],
                    }
                )
                img_i += 1
                if len(data[cat]) >= 4:
                    break
            if len(data[cat]) >= 4:
                break
            time.sleep(0.6)

    # Fallback if Bing returns thin results
    with open(OUT.replace(".json", "-backup-prev.json"), "w") as bf:
        try:
            with open(OUT) as pf:
                bf.write(pf.read())
        except OSError:
            pass

    for cat in data:
        if len(data[cat]) < 3:
            try:
                with open(OUT) as f:
                    old = json.load(f)
                for item in old.get(cat, []):
                    if item["url"] not in seen[cat] and len(data[cat]) < 4:
                        seen[cat].add(item["url"])
                        data[cat].append(item)
            except (OSError, json.JSONDecodeError):
                pass

    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(json.dumps({k: len(v) for k, v in data.items()}))


if __name__ == "__main__":
    main()