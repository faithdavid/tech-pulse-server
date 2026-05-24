#!/usr/bin/env python3
"""Phase 3 - Fill gaps: filmschool, niches, offers, inspire categories."""
import json, sys, re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

results = {}

def fetch(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        return None

def extract_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    return soup.get_text(separator=' ', strip=True)

# FILMSCHOOL - search for AI video techniques/education
print("=== FILMSCHOOL ===", file=sys.stderr)

# Runway Academy / tutorials
for url in [
    "https://runwayml.com/academy/",
    "https://runwayml.com/learn/",
]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:5000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        relevant = [s for s in sentences if len(s) > 20 and ('video' in s.lower() or 'ai' in s.lower() or 'learn' in s.lower() or 'technique' in s.lower() or 'guide' in s.lower())]
        for s in relevant[:10]:
            print(f"  Runway Learn: {s[:150]}", file=sys.stderr)
        break

# Pika tutorials
for url in ["https://pika.art/learn", "https://pika.art/tutorials"]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:4000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        relevant = [s for s in sentences if len(s) > 20]
        for s in relevant[:8]:
            print(f"  Pika Learn: {s[:150]}", file=sys.stderr)
        break

# Google Veo prompting guide
for url in ["https://deepmind.google/technologies/veo/prompting/"]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:4000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences[:15]:
            s = s.strip()
            if len(s) > 20:
                print(f"  Veo Prompt: {s[:150]}", file=sys.stderr)

# Try to find AI video filmmaking tutorials
for url in [
    "https://www.descript.com/blog/ai-video-editing-tutorials",
    "https://www.descript.com/blog",
]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:3000]
        if 'video' in text.lower() and ('ai' in text.lower() or 'edit' in text.lower()):
            print(f"  Descript: {text[:200]}", file=sys.stderr)

# NICHE - search for AI video market niches
print("\n=== NICHES ===", file=sys.stderr)
for url in [
    "https://www.entrepreneur.com/topic/ai-video",
    "https://explodingtopics.com/blog/ai-generated-content",
]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:5000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences[:15]:
            s = s.strip()
            if len(s) > 25 and ('video' in s.lower() or 'content' in s.lower() or 'trend' in s.lower() or 'niche' in s.lower() or 'demand' in s.lower()):
                print(f"  Niche: {s[:150]}", file=sys.stderr)

# OFFERS - selling/monetizing AI video
print("\n=== OFFERS ===", file=sys.stderr)
for url in [
    "https://www.shopify.com/blog/ai-video-generator",
    "https://neilpatel.com/blog/ai-video-marketing/",
]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:5000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences[:12]:
            s = s.strip()
            if len(s) > 25 and ('video' in s.lower() or 'sell' in s.lower() or 'monetize' in s.lower() or 'marketing' in s.lower() or 'business' in s.lower()):
                print(f"  Offer: {s[:150]}", file=sys.stderr)

# INSPIRE - creative AI video projects
print("\n=== INSPIRE ===", file=sys.stderr)
for url in [
    "https://runwayml.com/showcase/",
    "https://pika.art/showcase",
]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:4000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences[:10]:
            s = s.strip()
            if len(s) > 20:
                print(f"  Showcase: {s[:150]}", file=sys.stderr)

# More specific attempts
# Runway film festival winners
for url in ["https://runwayml.com/ai-film-festival/"]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:3000]
        print(f"  FilmFest: {text[:300]}", file=sys.stderr)

# Pika 2.0 - scene kitchen feature (AI video editing)
print("\n=== Pika Scene Kitchen ===", file=sys.stderr)
# Pika's scene kitchen / scene creation
for url in ["https://pika.art/"]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:5000]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for s in sentences[:20]:
            s = s.strip()
            if len(s) > 20 and ('scene' in s.lower() or 'kitchen' in s.lower() or 'pika' in s.lower() or 'video' in s.lower()):
                print(f"  Pika Main: {s[:150]}", file=sys.stderr)

# Try Pika Discord blog for Pika 2.0 details
for url in ["https://discord.com/blog/pika-labs-ai-video-generation"]:
    html = fetch(url)
    if html:
        text = extract_text(html)[:3000]
        print(f"  Pika Discord: {text[:300]}", file=sys.stderr)

# Runway Gen-4 details - check news articles
print("\n=== Runway Gen-4 News ===", file=sys.stderr)
for url in [
    "https://www.theverge.com/2025/12/runway-gen-4",
    "https://techcrunch.com/2025/runway-gen-4/",
]:
    html = fetch(url)
    if html:
        # extract title
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('title')
        if title:
            print(f"  Title: {title.get_text(strip=True)[:100]}", file=sys.stderr)
        text = extract_text(html)[:3000]
        if 'gen' in text.lower() or 'runway' in text.lower():
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences[:5]:
                print(f"  News: {s[:150]}", file=sys.stderr)

print("\n=== Done ===", file=sys.stderr)
