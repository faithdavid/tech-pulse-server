#!/usr/bin/env python3
"""Curate and write the final pulse-data.json with clean data."""
import json

data = {
  "ai": [
    {
      "title": "Google Chrome silently installs a 4 GB AI model on your device without consent",
      "description": "Google Chrome is downloading a 4 GB Gemini Nano model onto users' machines without consent, with no opt-in and no opt-out short of enterprise tooling. The model auto-re-downloads every time the user deletes it. Privacy advocates are sounding alarms about this pattern, identical to the recent Anthropic Claude Desktop controversy.",
      "url": "https://www.thatprivacyguy.com/blog/chrome-silent-nano-install/",
      "source": "That Privacy Guy",
      "image_url": "https://images.unsplash.com/photo-1677442136019?w=600&q=60"
    },
    {
      "title": "Local AI needs to be the norm",
      "description": "A compelling argument for why local AI models should be the default rather than cloud-dependent systems. Covers privacy, latency, offline capability, and the growing ecosystem of on-device models that can run on consumer hardware.",
      "url": "https://unix.foo/posts/local-ai-needs-to-be-norm/",
      "source": "unix.foo",
      "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=600&q=60"
    },
    {
      "title": "AI slop is killing online communities",
      "description": "A deep reflection on how AI-generated content is eroding trust and quality in online communities. The author argues that much AI-generated work should stay within the creator's walls rather than flooding public spaces, drawing parallels to crayon drawings brought home from kindergarten.",
      "url": "https://rmoff.net/2026/05/06/ai-slop-is-killing-online-communities/",
      "source": "rmoff.net",
      "image_url": "https://images.unsplash.com/photo-1536240478700?w=600&q=60"
    },
    {
      "title": "Anthropic's Mythos AI model is the best cybersecurity news in a decade",
      "description": "Anthropic's powerful AI model (codenamed Mythos) is being hailed as the biggest positive development in cybersecurity in a decade. The UK's AISI reported that AI models showed 'progress well above previous trends' on cybersecurity vulnerability discovery and testing.",
      "url": "https://sfstandard.com/opinion/2026/05/06/mythos-cybersecurity-ai/",
      "source": "San Francisco Standard",
      "image_url": "https://images.unsplash.com/photo-1558494949?w=600&q=60"
    }
  ],
  "funding": [
    {
      "title": "Sierra Raises $950M at $15B Valuation for AI Customer Service",
      "description": "Sierra, the AI customer service platform co-founded by Bret Taylor, raised $950 million at a valuation of over $15 billion. The company helps enterprises build conversational AI agents for customer support and has seen explosive growth as businesses rush to deploy AI-powered customer experiences.",
      "url": "https://sierra.ai/blog/better-customer-experiences-built-on-sierra",
      "source": "Sierra AI",
      "image_url": "https://images.unsplash.com/photo-1611974789855?w=600&q=60"
    },
    {
      "title": "Anduril Raises $5B at $61B Valuation, Doubling in Under a Year",
      "description": "Defense tech company Anduril raised a $5B Series H round led by Thrive Capital and Andreessen Horowitz at a $61B valuation — more than double its $30.5B valuation from less than a year ago. The company doubled revenue in 2025 to $2.2B and has now raised over $11B from investors.",
      "url": "https://techcrunch.com/2026/05/13/anduril-raises-5b-doubles-valuation-to-61b/",
      "source": "TechCrunch",
      "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=60"
    },
    {
      "title": "Shield AI Raises $1.5B Series G at $12.7B Valuation",
      "description": "Defense AI startup Shield AI raised $1.5B in Series G funding at a $12.7B valuation, underscoring surging VC interest in defense technology. The company builds AI pilots for autonomous aircraft and has been winning major Pentagon contracts.",
      "url": "https://techcrunch.com/",
      "source": "TechCrunch",
      "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=600&q=60"
    },
    {
      "title": "AI Voice Startup Vapi Hits $500M Valuation After Winning Amazon Ring",
      "description": "Vapi, an AI voice infrastructure startup, reached a $500M valuation after beating over 40 rivals to win Amazon Ring's voice AI contract. The company provides voice AI APIs for businesses building conversational agents.",
      "url": "https://techcrunch.com/",
      "source": "TechCrunch",
      "image_url": "https://images.unsplash.com/photo-1551288049?w=600&q=60"
    }
  ],
  "tools": [
    {
      "title": "VS Code Inserting 'Co-Authored-by Copilot' Into Commits Regardless of Usage",
      "description": "A GitHub PR reveals that VS Code is automatically adding 'Co-Authored-by: Copilot' tags to git commits even when Copilot wasn't actually used for that code. The controversial change has sparked vigorous debate about proper AI attribution in version control and whether Microsoft is inflating Copilot's apparent usage.",
      "url": "https://github.com/microsoft/vscode/pull/310226",
      "source": "GitHub (Microsoft/vscode)",
      "image_url": "https://images.unsplash.com/photo-1461749280684?w=600&q=60"
    },
    {
      "title": "Going Back to Writing Code By Hand — What AI Gets Wrong at Scale",
      "description": "A developer who vibe-coded a GPU-aware Kubernetes TUI for 7 months decided to archive it and start over by hand. The post explores what AI coding assistants get wrong when projects grow complex — losing context, making inconsistent architectural decisions, and generating code that doesn't compose well.",
      "url": "https://blog.k10s.dev/im-going-back-to-writing-code-by-hand/",
      "source": "k10s.dev",
      "image_url": "https://images.unsplash.com/photo-1536148935331-408321065b18?w=600&q=60"
    },
    {
      "title": "Linux Gaming Is Faster Because Windows APIs Are Becoming Linux Kernel Features",
      "description": "Linux gaming performance is surging as Windows-specific APIs like NTSYNC (native Windows synchronization primitives) are implemented directly in the Linux kernel. The NTSYNC driver is now loaded by default on every updated Steam Deck, offering massive performance gains over previous Wine/Proton translation layers.",
      "url": "https://www.xda-developers.com/linux-gaming-is-getting-faster-because-windows-apis-are-becoming-linux-kernel-features/",
      "source": "XDA Developers",
      "image_url": "https://images.unsplash.com/photo-1552820728-8b83bb6b6413?w=600&q=60"
    },
    {
      "title": "The Emacsification of Software",
      "description": "A viral essay argues that software is becoming increasingly Emacs-like — infinitely malleable, scriptable, and personalized. The piece explores how modern tools are adopting the Emacs culture of extensibility, with 327+ points on Hacker News sparking wide discussion.",
      "url": "https://sockpuppet.org/blog/2026/05/12/emacsification/",
      "source": "Sockpuppet.org",
      "image_url": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=600&q=60"
    }
  ],
  "industry": [
    {
      "title": "Maryland Citizens Hit with $2B Power Grid Upgrade for Out-of-State AI Data Centers",
      "description": "Maryland residents are facing a $2 billion power grid upgrade bill to support AI data centers located outside the state. State regulators filed complaints with federal energy authorities saying the cost breaks ratepayer protection pledges. The case raises major questions about who should pay for AI infrastructure.",
      "url": "https://www.tomshardware.com/tech-industry/artificial-intelligence/maryland-citizens-slapped-with-usd2-billion-grid-upgrade-bill-for-out-of-state-ai-data-centers",
      "source": "Tom's Hardware",
      "image_url": "https://images.unsplash.com/photo-1519389950473?w=600&q=60"
    },
    {
      "title": "Apple and Intel Reach Preliminary Chip-Making Deal",
      "description": "Apple and Intel have reached a preliminary agreement for Intel to manufacture Apple device chips in the US, according to reports. The deal marks a major win for Intel's foundry business and could reduce Apple's reliance on TSMC for chip production, with significant geopolitical implications for semiconductor supply chains.",
      "url": "https://www.reuters.com/business/apple-intel-have-reached-preliminary-chip-making-deal-wsj-reports-2026-05-08/",
      "source": "Reuters",
      "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=60"
    },
    {
      "title": "Apple Explores Using Intel and Samsung to Build Main Device Chips in the US",
      "description": "Bloomberg reports Apple is exploring using both Intel and Samsung to manufacture main device chips on US soil, a strategic shift to diversify beyond TSMC amid rising geopolitical tensions over Taiwan. The move could reshape the global semiconductor landscape.",
      "url": "https://www.bloomberg.com/news/articles/2026-05-05/apple-explores-using-intel-and-samsung-to-build-main-device-chips-in-the-us",
      "source": "Bloomberg",
      "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&q=60"
    },
    {
      "title": "Trump Taps Tim Cook, Jensen Huang, Elon Musk for Beijing Summit on Chips and Tariffs",
      "description": "Trump invited Tim Cook (Apple), Jensen Huang (Nvidia), and Elon Musk to join him at the Beijing summit with Xi Jinping, as semiconductor tariffs and Taiwan relations hang in the balance. AI was added to the summit agenda. Nvidia's chips remain peerless while US access to China's rare-earth exports is critical.",
      "url": "https://arstechnica.com/tech-policy/2026/05/desperate-trump-taps-tim-apple-jensen-huang-elon-musk-to-attend-xi-summit/",
      "source": "Ars Technica",
      "image_url": "https://images.unsplash.com/photo-1516245834210-c4c142787335?w=600&q=60"
    }
  ],
  "oss": [
    {
      "title": "Bambu Lab Accused of Abusing the Open Source Social Contract",
      "description": "Popular 3D printer manufacturer Bambu Lab is facing backlash for pushing always-connected cloud solutions as the new default, contradicting their open-source promises. Users are blocking printers from the internet and refusing firmware updates. Jeff Geerling's deep dive has 400+ points on HN.",
      "url": "https://www.jeffgeerling.com/blog/2026/bambu-lab-abusing-open-source-social-contract/",
      "source": "Jeff Geerling",
      "image_url": "https://images.unsplash.com/photo-1558494949?w=600&q=60"
    },
    {
      "title": "Dirty Frag: Universal Linux Local Privilege Escalation Vulnerability",
      "description": "A new Linux kernel vulnerability dubbed 'Dirty Frag' has been disclosed, allowing local privilege escalation on affected systems. The flaw affects multiple kernel versions and distributions. System administrators are urged to patch immediately. Published via the oss-security mailing list.",
      "url": "https://www.openwall.com/lists/oss-security/2026/05/07/8",
      "source": "Openwall",
      "image_url": "https://images.unsplash.com/photo-1558494949?w=600&q=60"
    },
    {
      "title": "Python Reverts Incremental Garbage Collector in 3.14 and 3.15",
      "description": "Core Python developers reverted the incremental garbage collector in both Python 3.14 and 3.15 after reports of significant memory pressure in production environments. The revert goes back to the generational GC from 3.13. The new GC may be reintroduced in 3.16 through a proper PEP process.",
      "url": "https://discuss.python.org/t/reverting-the-incremental-gc-in-python-3-14-and-3-15/107014",
      "source": "Python Discourse",
      "image_url": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=600&q=60"
    },
    {
      "title": "Plandex v2 — Open Source AI Coding Agent for Large Projects",
      "description": "Plandex v2 was released as an open-source AI coding agent designed for large projects and complex multi-file tasks. It uses a planning engine to break down big changes into manageable steps, executes them, and learns from the results. 257+ points on HN.",
      "url": "https://github.com/plandex-ai/plandex",
      "source": "GitHub (Plandex AI)",
      "image_url": "https://images.unsplash.com/photo-1536240478700?w=600&q=60"
    }
  ]
}

# Write the curated data
with open('/home/faith/tech-pulse-server/pulse-data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("Written pulse-data.json successfully")
print(f"Categories: {list(data.keys())}")
for cat, items in data.items():
    print(f"  {cat}: {len(items)} stories")
