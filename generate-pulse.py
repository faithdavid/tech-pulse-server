#!/usr/bin/env python3
"""
Pulse Generator — Unified
Generates HTML briefings for Tech Pulse & AI Video Pulse.
Archives dated files, updates latest symlinks, deploys to Surge.

Usage:
  python3 generate-pulse.py --type tech --file data.json
  python3 generate-pulse.py --type video --file data.json
  python3 generate-pulse.py --type tech --file data.json --data '{"key":...}'  # quick override
"""
import json, sys, os, re, glob, shutil
from datetime import datetime, timezone, timedelta
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SURGE_DOMAIN = "tech-pulse-trillion.surge.sh"
SURGE_PATH = os.environ.get("SURGE_PATH") or os.path.expanduser("~/.npm-global/bin/surge")
_SURGE = shutil.which("surge")
if _SURGE:
    SURGE_PATH = _SURGE

PULSE_CONFIGS = {
    "tech": {
        "template": "tech-pulse-template.html",
        "archive_dir": "tech-pulse",
        "latest_file": "latest-tech-pulse.html",
        "sections_order": ["ai", "funding", "tools", "industry", "oss"],
        "tag_map": {
            "ai": ("ai", "🤖 AI Breakthroughs", "#a29bfe"),
            "funding": ("funding", "💰 Startup Funding", "#00b894"),
            "tools": ("tools", "🔧 Dev Tools", "#fd79a8"),
            "industry": ("industry", "🏭 Industry", "#74b9ff"),
            "oss": ("oss", "📦 Open Source", "#fdcb6e"),
        },
        "spotlight_badge": "★ Top Story",
        "footer_nav": '<a href="/index.html">View All Pulses</a> · <a href="/latest-ai-video-pulse.html">AI Video Pulse →</a>',
        "stat_labels": {"ai": "AI & Research", "funding": "Funding Rounds", "tools": "Dev Tools", "industry": "Industry", "oss": "Open Source"},
    },
    "video": {
        "template": "ai-video-pulse-template.html",
        "archive_dir": "ai-video-pulse",
        "latest_file": "latest-ai-video-pulse.html",
        "sections_order": ["filmschool", "industry", "tools", "niches", "offers", "inspire"],
        "tag_map": {
            "filmschool": ("filmschool", "🎬 Film School", "#fdcb6e"),
            "industry": ("industry", "📰 Industry News", "#a29bfe"),
            "tools": ("tools", "🔧 Tools & Tech", "#00b894"),
            "niches": ("niches", "📈 Trends & Niches", "#fd79a8"),
            "offers": ("offers", "💼 Offers & Selling", "#74b9ff"),
            "inspire": ("inspire", "✨ Inspiration", "#fab1a0"),
        },
        "spotlight_badge": "🎓 Film School Tip of the Day",
        "footer_nav": '<a href="/index.html">View All Pulses</a> · <a href="/latest-tech-pulse.html">Tech Pulse →</a>',
        "stat_labels": {"filmschool": "Film Tips", "industry": "Industry", "tools": "Tools", "niches": "Trends", "offers": "Offers", "inspire": "Inspiration"},
    }
}

def escape_html(s):
    s = str(s or "")
    for a, b in [('&','&amp;'), ('<','&lt;'), ('>','&gt;'), ('"','&quot;'), ("'",'&#39;')]:
        s = s.replace(a, b)
    return s

def build_card(item, category_tag, category_name):
    tag_class = category_tag
    img_url = item.get('image_url', '')
    img_html = ''
    if img_url:
        img_html = '\n    <img class="card-image" src="' + escape_html(img_url) + '" alt="" loading="lazy">'
    card = f'''  <div class="card" data-type="{tag_class}">
    <div class="card-tag {tag_class}">{category_name}</div>{img_html}
    <h3>{escape_html(item.get('title', 'Untitled'))}</h3>
    <p>{escape_html(item.get('description', ''))}</p>'''
    url = item.get('url', '')
    source = item.get('source', '')
    source_html = f'<span class="card-source">{escape_html(source)}</span>' if source else ''
    card += '\n  <div class="card-footer">'
    card += f'\n    {source_html}'
    if url:
        card += f'\n    <a class="card-link" href="{escape_html(url)}" target="_blank">Read more →</a>'
    card += '\n  </div>'
    card += '\n  </div>'
    return card

def generate(data, pulse_type):
    config = PULSE_CONFIGS[pulse_type]
    
    # Read template
    template_path = os.path.join(BASE_DIR, config["template"])
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Timestamp
    now_et = datetime.now(timezone(timedelta(hours=-4)))
    timestamp = now_et.strftime('%A, %B %d, %Y at %I:%M %p ET')
    file_date = now_et.strftime('%Y-%m-%d')
    
    # Build section data
    sections = {}
    counts = {}
    for section_key in config["sections_order"]:
        items = data.get(section_key, [])
        counts[section_key] = len(items)
        tag_class, display_name, _ = config["tag_map"][section_key]
        if items:
            sections[section_key] = '\n'.join(build_card(item, tag_class, display_name) for item in items)
        else:
            sections[section_key] = '<div class="empty-section">No items this cycle</div>'
    
    total_items = sum(counts.values())
    
    # Spotlight / Film School Tip
    all_items = [(cat, item) for cat in config["sections_order"] for item in data.get(cat, [])]
    spotlight_html = ''
    
    if pulse_type == "video" and all_items:
        # For video: look for filmschool items first, else best story
        fs_items = data.get('filmschool', [])
        if fs_items:
            best = fs_items[0]
            title = escape_html(best.get('title', ''))
            desc = escape_html(best.get('description', ''))
            url = best.get('url', '')
            link = '<a class="card-link" href="%s" target="_blank">Deep dive \u2192</a>' % escape_html(url) if url else ''
            spotlight_html = (
                '<div class="filmschool-spotlight">\n'
                '  <div class="badge">' + config["spotlight_badge"] + '</div>\n'
                '  <div class="tip-box">\n'
                '    <div class="tip-label">\U0001f4d6 Learn This</div>\n'
                '    <h2>' + title + '</h2>\n'
                '    <p>' + desc + '</p>\n'
                '  </div>\n'
                '  ' + link + '\n'
                '</div>'
            )
        elif all_items:
            best = max(all_items, key=lambda x: len(x[1].get('description', '')))
            title = escape_html(best[1].get('title', ''))
            desc = escape_html(best[1].get('description', ''))
            url = best[1].get('url', '')
            link = '<a class="card-link" href="%s" target="_blank">Read more \u2192</a>' % escape_html(url) if url else ''
            spotlight_html = (
                '<div class="filmschool-spotlight">\n'
                '  <div class="badge">\u2605 Top Story</div>\n'
                '  <h2>' + title + '</h2>\n'
                '  <p>' + desc + '</p>\n'
                '  ' + link + '\n'
                '</div>'
            )
    elif pulse_type == "tech" and all_items:
        best = max(all_items, key=lambda x: len(x[1].get('description', '')))
        title = escape_html(best[1].get('title', ''))
        desc = escape_html(best[1].get('description', ''))
        url = best[1].get('url', '')
        # Map spotlight image to its category
        spotlight_cat = best[0]
        spotlight_imgs = {
            'ai': 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=640&q=60',
            'funding': 'https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=640&q=60',
            'tools': 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=640&q=60',
            'industry': 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=640&q=60',
            'oss': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=640&q=60',
        }
        img_url = spotlight_imgs.get(spotlight_cat, 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=640&q=60')
        link = ''
        if url:
            link = '<a class="read-more" href="%s" target="_blank">Read full story →</a>' % escape_html(url)
        spotlight_html = '<div class="spotlight">\n'
        spotlight_html += '  <div class="spotlight-visual">\n'
        spotlight_html += '    <img src="%s" alt="" width="640" height="360" loading="lazy">\n' % img_url
        spotlight_html += '  </div>\n'
        spotlight_html += '  <div class="spotlight-content">\n'
        spotlight_html += '    <div class="spotlight-badge">%s</div>\n' % config["spotlight_badge"]
        spotlight_html += '    <h2>%s</h2>\n' % title
        spotlight_html += '    <p>%s</p>\n' % desc
        spotlight_html += '    %s\n' % link
        spotlight_html += '  </div>\n'
        spotlight_html += '</div>'
    
    # Build replacements
    replacements = {
        '{timestamp}': timestamp,
        '{total_items}': str(total_items),
        '{spotlight_section}': spotlight_html if pulse_type == "tech" else '',
        '{filmschool_spotlight}': spotlight_html if pulse_type == "video" else '',
        '{footer_nav}': config["footer_nav"],
    }
    
    # Section cards & counts
    for section_key in config["sections_order"]:
        replacements[f'{{{section_key}_cards}}'] = sections[section_key]
        replacements[f'{{{section_key}_count}}'] = str(counts[section_key])
    
    # Stats
    for section_key, label in config["stat_labels"].items():
        replacements[f'{{{section_key}_stat}}'] = str(counts.get(section_key, 0))
    
    # Fill template
    for key, val in replacements.items():
        template = template.replace(key, val)
    
    # Determine archive filename with sequence number
    archive_dir = os.path.join(BASE_DIR, config["archive_dir"])
    os.makedirs(archive_dir, exist_ok=True)
    
    existing = sorted(glob.glob(os.path.join(archive_dir, f"{file_date}-*.html")))
    seq = 1
    if existing:
        last = os.path.basename(existing[-1])
        try:
            seq = int(last.split('-')[-1].replace('.html', '')) + 1
        except:
            seq = len(existing) + 1
    
    archive_filename = f"{file_date}-{seq:03d}-{pulse_type}.html"
    archive_path = os.path.join(archive_dir, archive_filename)
    
    # Write archive
    with open(archive_path, 'w') as f:
        f.write(template)
    
    # Write latest file (overwrite)
    latest_path = os.path.join(BASE_DIR, config["latest_file"])
    with open(latest_path, 'w') as f:
        f.write(template)
    
    return archive_path, latest_path, archive_filename

def update_index():
    """Regenerate index.html with full pulse history"""
    index_path = os.path.join(BASE_DIR, "index.html")
    index_template_path = os.path.join(BASE_DIR, "index-template.html")
    
    # Always read from template to preserve placeholders
    if not os.path.exists(index_template_path):
        sys.stderr.write("ERROR: index-template.html not found\n")
        return
    
    # Gather all archived pulses
    entries = []
    for pulse_type, config in [("tech", PULSE_CONFIGS["tech"]), ("video", PULSE_CONFIGS["video"]), ("empire", {"archive_dir": "empire-pulse"})]:
        archive_dir = os.path.join(BASE_DIR, config["archive_dir"])
        if not os.path.isdir(archive_dir):
            continue
        for f in sorted(glob.glob(os.path.join(archive_dir, "*-%s.html" % pulse_type)), reverse=True):
            basename = os.path.basename(f)
            # Filename: YYYY-MM-DD-SEQ-TYPE.html
            date = basename[:10] if len(basename) >= 10 else basename
            seq = ""
            rest = basename[11:]  # after YYYY-MM-DD-
            dash_pos = rest.find('-')
            if dash_pos > 0:
                seq = rest[:dash_pos]
            entries.append({
                "type": pulse_type,
                "date": date,
                "seq": seq,
                "filename": basename,
                "filepath": os.path.join(config["archive_dir"], basename)
            })
    
    sys.stderr.write("Index: found %d archived entries\n" % len(entries))
    
    # Build history HTML
    history_lines = []
    for e in entries:
        if e["type"] == "empire":
            badge_type = "empire"
            label = "EMPIRE"
            title = "Empire Pulse"
        else:
            badge_type = "tech" if e["type"] == "tech" else "video"
            label = "TECH" if e["type"] == "tech" else "VIDEO"
            title = "Tech Pulse" if e["type"] == "tech" else "AI Video Pulse"
        history_lines.append(
            '<a class="entry" href="%s">'
            '  <span class="type-badge %s">%s</span>'
            '  <span class="date">%s</span>'
            '  <span class="title">%s #%s</span>'
            '  <span class="arrow">→</span>'
            '</a>' % (e["filepath"], badge_type, label, e["date"], title, e["seq"])
        )
    
    history_html = '\n'.join(history_lines) if history_lines else (
        '<div class="empty-state">No pulses generated yet. Waiting for first run...</div>'
    )
    
    # Read index template
    with open(index_template_path, 'r') as f:
        index_content = f.read()
    
    index_content = index_content.replace('{total_entries}', str(len(entries)))
    index_content = index_content.replace('{history_entries}', history_html)
    
    with open(index_path, 'w') as f:
        f.write(index_content)
    
    sys.stderr.write("Index: updated %s\n" % index_path)

def deploy_surge():
    """Deploy entire server directory to Surge"""
    result = subprocess.run(
        [SURGE_PATH, BASE_DIR, SURGE_DOMAIN],
        capture_output=True, text=True, timeout=30,
        env={**os.environ, "PATH": f"{os.environ.get('PATH', '')}:{os.path.dirname(SURGE_PATH)}"}
    )
    return result.returncode == 0, result.stderr.strip()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', choices=['tech', 'video'], required=True, help='Pulse type')
    parser.add_argument('--file', help='JSON data file path')
    parser.add_argument('--no-deploy', action='store_true', help='Skip Surge deploy')
    args = parser.parse_args()
    
    # Load data
    if args.file:
        with open(args.file) as f:
            data = json.load(f)
    elif not sys.stdin.isatty():
        data = json.load(sys.stdin)
    else:
        print("ERROR: No data provided. Use --file or pipe JSON to stdin.")
        sys.exit(1)
    
    # Generate
    archive_path, latest_path, filename = generate(data, args.type)
    
    # Update index.html with full history
    update_index()
    
    # Deploy
    if not args.no_deploy:
        ok, err = deploy_surge()
        status = "OK" if ok else f"WARNING: {err}"
    else:
        status = "SKIPPED (--no-deploy)"
    
    pulse_name = {"tech": "Tech Pulse", "video": "AI Video Pulse"}[args.type]
    print(f"[{pulse_name}] Generated: {archive_path}")
    print(f"[{pulse_name}] Latest: {latest_path}")
    print(f"[{pulse_name}] Published: https://{SURGE_DOMAIN}/{filename}")
    print(f"[{pulse_name}] Surge: {status}")
