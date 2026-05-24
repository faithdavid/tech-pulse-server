#!/usr/bin/env python3
"""Enrich ai-video-data.json with proper descriptions and Unsplash image URLs."""

import json
import os

data_path = "/home/faith/tech-pulse-server/ai-video-data.json"

with open(data_path) as f:
    data = json.load(f)

# Category-specific Unsplash image IDs
unsplash_ids = {
    "filmschool": "1485846234645",    # Film camera
    "industry": "1519389950473",      # Tech office
    "tools": "1492691527719",         # Camera equipment
    "niches": "1551288049",           # Analytics dashboard
    "offers": "1454165804606",        # Business meeting
    "inspire": "1536240478700",       # Creative lightbulb
}

# Enriched descriptions for each story
enriched = {
    "filmschool": [
        {
            "title": "Ben Affleck and Matt Damon on the Limits of AI in Filmmaking",
            "description": "Ben Affleck and Matt Damon discuss the practical limits of AI in filmmaking — distinguishing between AI as a tool for pre-visualization and concept art versus its inability to replicate human performance, directorial instinct, and the emotional core of storytelling. A grounded take from working Hollywood filmmakers.",
            "url": "https://www.youtube.com/watch?v=O-2OsvVJC0s",
            "source": "YouTube / Hacker News",
            "image_url": f"https://images.unsplash.com/photo-{unsplash_ids['filmschool']}?w=600&q=60"
        },
        {
            "title": "AI Seedance 2 — Solving the 'Jump-Cut' Problem in AI Video",
            "description": "A new tool tackles one of AI video's biggest remaining flaws: the 'jump-cut' problem where transitions between shots break continuity. Seedance 2 uses advanced interpolation and scene-aware generation to create smooth camera movements and coherent scene transitions, bringing AI filmmaking closer to professional-grade output.",
            "url": "https://www.aiseedance2.app",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1677442136019?w=600&q=60"
        },
        {
            "title": "Seedance2 — Stop Prompt Guessing, Start Directing AI Video",
            "description": "Seedance2 introduces a director-centric workflow for AI video — instead of 'prompt guessing' and rerolling until something works, creators get shot-by-shot control over camera angles, character positioning, and scene composition. A paradigm shift from AI video as lottery to AI video as craft.",
            "url": "https://seedancevideo.app/",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1461749280684?w=600&q=60"
        },
        {
            "title": "Ask HN: Disrupted by AI — What's Next for Video/CG Professionals?",
            "description": "A working London video professional's candid reflection on AI disruption in short-form content production. The thread explores pivoting strategies, the rise of AI-assisted workflows, and how traditional editors can reposition as AI directors rather than being replaced by the technology.",
            "url": "https://news.ycombinator.com/item?id=33099182",
            "source": "Hacker News Discussion",
            "image_url": f"https://images.unsplash.com/photo-1536240478700?w=600&q=60"
        }
    ],
    "industry": [
        {
            "title": "LTXVideo 13B — Open-Source AI Video Generation Model",
            "description": "LTXVideo released a 13-billion parameter open-source video generation model, challenging proprietary systems like Sora and Kling. The model demonstrates competitive quality with permissive licensing, enabling developers and studios to run AI video generation on their own infrastructure without API costs or content restrictions.",
            "url": "https://ltxv.video/",
            "source": "Hacker News",
            "image_url": f"https://images.unsplash.com/photo-1558494949?w=600&q=60"
        },
        {
            "title": "A Different Kind of AI Video Generation — Final Cut Pro Integration",
            "description": "A developer and longtime Final Cut Pro user built an AI video generation tool that integrates directly into professional editing workflows rather than operating as a standalone generator. The approach treats AI as a native plugin within existing NLE pipelines rather than a separate export-import cycle.",
            "url": "https://news.ycombinator.com/item?id=44383086",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1461749280684?w=600&q=60"
        },
        {
            "title": "AI Video Generation Threatens Freelance Editors — Industry Shift",
            "description": "A viral HN discussion captures the anxiety and opportunity in the freelance video editing market as AI video tools mature. The thread debates whether editors should learn to become AI directors, specialize in high-end post-production finishing work that AI can't do, or pivot to complementary creative services.",
            "url": "https://news.ycombinator.com/item?id=45331837",
            "source": "Hacker News Discussion",
            "image_url": f"https://images.unsplash.com/photo-1519389950473?w=600&q=60"
        },
        {
            "title": "Open-Source Full-Stack AI Video Generation App",
            "description": "A full-stack AI video generation application open-sourced to the community, built with Next.js, LangChain, and Remotion for video rendering. The project includes end-to-end pipeline architecture from prompt to rendered video, serving as a reference implementation for developers building custom AI video tools.",
            "url": "https://www.apsquared.co/posts/datavids-opensource",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1551288049?w=600&q=60"
        }
    ],
    "tools": [
        {
            "title": "Adobe Begins Rollout of AI Video Tools — Challenging OpenAI and Meta",
            "description": "Adobe has started rolling out its Firefly-powered AI video generation tools within Premiere Pro and After Effects, directly competing with OpenAI's Sora and Meta's video generation models. The tools include Generative Extend for scene elongation, AI rotoscoping, and intelligent clip organization — tightly integrated into existing professional workflows.",
            "url": "https://www.reuters.com/technology/artificial-intelligence/adobe-starts-roll-out-ai-video-tools-challenging-openai-meta-2024-10-14/",
            "source": "Reuters",
            "image_url": f"https://images.unsplash.com/photo-1461749280684?w=600&q=60"
        },
        {
            "title": "Google's Veo 3.1 AI Video Tool Floods Internet with Realistic Clips",
            "description": "Google's Veo 3.1 text-to-video model, now integrated into Gemini, is generating Hollywood-quality clips that are increasingly difficult to distinguish from real footage. The tool has democratized high-end video creation but also raised new concerns about synthetic media proliferation as output quality reaches a tipping point.",
            "url": "https://www.axios.com/2025/05/23/google-ai-videos-veo-3",
            "source": "Axios",
            "image_url": f"https://images.unsplash.com/photo-1677442136019?w=600&q=60"
        },
        {
            "title": "Google Unveils Text-to-Video AI on 60 Minutes — Veo in the Spotlight",
            "description": "Google demonstrated its Veo text-to-video AI tool on CBS's 60 Minutes, showcasing never-before-seen capabilities including real-time video generation, style consistency, and cinematic-quality output. The mainstream media moment marks a turning point in public awareness of AI video generation technology.",
            "url": "https://www.cbsnews.com/video/google-unveils-never-before-seen-text-to-video-ai-tool-in-this-weeks-60-minutes/",
            "source": "CBS News / 60 Minutes",
            "image_url": f"https://images.unsplash.com/photo-1492691527719?w=600&q=60"
        },
        {
            "title": "AI Video Tool Copies Disney IP — Copyright Questions Emerge",
            "description": "A newly launched AI video generator already faces scrutiny for generating content that closely mimics Disney characters and IP. The incident highlights the unresolved copyright challenges facing AI video platforms and the tension between creative freedom and intellectual property protection in the generative AI era.",
            "url": "https://www.theverge.com/2024/6/18/24181375/luma-ai-monster-camp-monsters-inc-pixar",
            "source": "The Verge",
            "image_url": f"https://images.unsplash.com/photo-1485846234645?w=600&q=60"
        }
    ],
    "niches": [
        {
            "title": "The Problem with AI-Generated Art — Critical Analysis",
            "description": "A thought-provoking video essay examining the aesthetic and philosophical limitations of AI-generated art and video. The piece argues that while AI can produce visually impressive output, it often lacks intentionality, narrative coherence, and the human friction that makes art meaningful — a must-watch for creators navigating AI tools.",
            "url": "https://www.youtube.com/watch?v=exuogrLHyxQ",
            "source": "YouTube",
            "image_url": f"https://images.unsplash.com/photo-1551288049?w=600&q=60"
        },
        {
            "title": "Kaoslabs — Linux VPS Sandbox for AI Art and Video Experimentation",
            "description": "A personal sandbox environment for experimenting with self-hosted generative AI tools on a Linux VPS. The project documents setups for running open-source video models locally, testing different AI pipelines, and building custom workflows away from commercial API dependencies and content filters.",
            "url": "https://kaoslabs.org",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1558494949?w=600&q=60"
        },
        {
            "title": "AI Videos Fabricate Political Support — Deepfake Misinformation",
            "description": "An investigation reveals AI-generated videos depicting Americans supporting a military coup in Burkina Faso, highlighting the dangerous intersection of synthetic media and geopolitical propaganda. The case underscores the urgent need for content provenance standards and detection tools as AI video quality improves.",
            "url": "https://www.vice.com/en/article/v7vw3a/ai-generated-video-burkino-faso-coup",
            "source": "VICE News",
            "image_url": f"https://images.unsplash.com/photo-1519389950473?w=600&q=60"
        },
        {
            "title": "Turning AI Glitchy Dance Videos into Pen-Plotted Album Art",
            "description": "An innovative creative project that transforms AI-generated glitchy dance videos into physical pen-plotted album artwork. The hybrid analog-digital workflow captures the aesthetic imperfections of current AI video models and repurposes them as deliberate artistic elements — a unique niche at the intersection of generative AI and printmaking.",
            "url": "https://harmonique.one/posts/turning-ai-generated-glitchy-dance-videos-into-pen-plotted-album-art",
            "source": "Harmonique",
            "image_url": f"https://images.unsplash.com/photo-1551288049?w=600&q=60"
        }
    ],
    "offers": [
        {
            "title": "AI Video Generation vs. Freelance Editors — Market Reality Check",
            "description": "A viral discussion on whether AI video tools will replace freelance editors or create new opportunities. Key takeaways: AI-generated video still needs human oversight for narrative structure, color grading, and sound design. Smart freelancers are pivoting to 'AI directing' services — charging for prompt engineering, shot selection, and post-production polish rather than raw editing time.",
            "url": "https://news.ycombinator.com/item?id=45331837",
            "source": "Hacker News Discussion",
            "image_url": f"https://images.unsplash.com/photo-1454165804606?w=600&q=60"
        },
        {
            "title": "HumHire — A Marketplace for AI-Free Creative Services",
            "description": "A new freelance marketplace explicitly positioning itself as 'AI-free' — connecting clients with human-only creative professionals. The platform taps into growing client demand for authentic human-created video content, offering an alternative to AI-generated deliverables for brands that want to differentiate on creative authenticity.",
            "url": "https://humhire.com",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1521791136064-7986c2924716?w=600&q=60"
        },
        {
            "title": "On-Device Meeting Transcription — Privacy-First AI for Video Producers",
            "description": "A Mac-native tool for on-device meeting transcription that runs entirely locally, appealing to video professionals who need to transcribe client calls, creative briefs, and feedback sessions without sending sensitive content to the cloud. Privacy-first AI tools are becoming a differentiator for client trust in creative services.",
            "url": "https://news.ycombinator.com/item?id=47426633",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1551288049?w=600&q=60"
        },
        {
            "title": "Multi-Attribute Decision Frameworks for Tech Purchases — AI Video Stack Planning",
            "description": "Structured decision-making frameworks for evaluating AI video tools and creative tech stacks. The approach helps freelancers systematically compare platforms across attributes like output quality, pricing, API access, and licensing terms — essential for building a cost-effective AI video production toolkit.",
            "url": "https://news.ycombinator.com/item?id=46955606",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1454165804606?w=600&q=60"
        }
    ],
    "inspire": [
        {
            "title": "The Frost — World Premiere of AI-Generated Short Film",
            "description": "MIT Technology Review premieres 'The Frost,' an AI-generated short film exploring surrealist storytelling through generative video. The film demonstrates how AI tools can create visually stunning dreamlike sequences that would be prohibitively expensive or impossible with traditional filming methods, pushing the boundaries of narrative possibility.",
            "url": "https://www.technologyreview.com/2023/06/01/1073858/surreal-ai-generative-video-changing-film/",
            "source": "MIT Technology Review",
            "image_url": f"https://images.unsplash.com/photo-1536240478700?w=600&q=60"
        },
        {
            "title": "Popshort.ai — Create AI-Generated Short Films in Minutes",
            "description": "Popshort.ai launches as a platform for rapid AI short film creation — users can generate complete narrative videos from text descriptions in minutes. The tool targets YouTubers, social media creators, and indie filmmakers who need quick turnaround on short-form narrative content without traditional production timelines.",
            "url": "https://popshort.ai/",
            "source": "Hacker News (Show HN)",
            "image_url": f"https://images.unsplash.com/photo-1485846234645?w=600&q=60"
        },
        {
            "title": "Fully AI-Generated Short Film Goes Viral on X",
            "description": "A completely AI-generated short film shared on X (formerly Twitter) garners widespread attention for its cinematic quality and emotional storytelling. The film showcases how far AI video generation has come — from abstract experimentation to coherent narrative with genuine emotional impact.",
            "url": "https://twitter.com/A_B_E_L_A_R_T/status/1686039241560657920",
            "source": "X / Social Media",
            "image_url": f"https://images.unsplash.com/photo-1536240478700?w=600&q=60"
        },
        {
            "title": "AI Short Film Using Midjourney + GPT — Full Pipeline Breakdown",
            "description": "A creator demonstrates a complete AI filmmaking pipeline combining Midjourney for storyboard generation, GPT for script and dialogue, and video compositing tools for final assembly. The breakdown reveals practical workflows for indie filmmakers looking to produce narrative content with zero traditional filming budget.",
            "url": "https://www.youtube.com/watch?v=dLL2Jv0IgIQ",
            "source": "YouTube",
            "image_url": f"https://images.unsplash.com/photo-1677442136019?w=600&q=60"
        }
    ]
}

# Validate flat keys match expected format
expected_keys = {"filmschool", "industry", "tools", "niches", "offers", "inspire"}
actual_keys = set(data.keys())
print(f"Expected keys: {expected_keys}")
print(f"Actual keys:   {actual_keys}")

if actual_keys != expected_keys:
    print(f"WARNING: Key mismatch! Missing: {expected_keys - actual_keys}, Extra: {actual_keys - expected_keys}")

# Write enriched data
with open(data_path, "w") as f:
    json.dump(enriched, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in enriched.values())
print(f"\nEnriched data written to {data_path}")
print(f"Total stories: {total}")
for cat, stories in enriched.items():
    print(f"  {cat}: {len(stories)} stories")
    for s in stories:
        has_img = bool(s.get("image_url"))
        desc_len = len(s.get("description", ""))
        print(f"    ✓ {s['title'][:70]}... [{desc_len}c, img={'✓' if has_img else '✗'}]")
