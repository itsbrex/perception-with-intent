# Epic Plan: rssatoms Integration + Discord Demo

**Epic ID:** perception-aku
**Status:** Planning
**Created:** 2025-12-29
**Owner:** Jeremy

## Executive Summary

Integrate the curated TIER 1 RSS feeds from rssatoms (97 high-quality feeds, score 75-100) into perception's ingestion pipeline, and create a Discord bot/webhook integration to demo real-time article alerts to potential users/stakeholders.

## Goals

1. **Feed Integration**: Wire rssatoms TIER 1 feeds into perception's MCP service
2. **Live Demo**: Create Discord channel where stakeholders can see real-time intelligence alerts
3. **Showcase Value**: Demonstrate perception's AI-powered news analysis capabilities

## Current State

### Perception (perception-with-intent)
- **Agent Engine:** `4241324322704064512` - WORKING
- **MCP Service:** `https://perception-mcp-w53xszfqnq-uc.a.run.app` - WORKING
- **Firestore:** `perception-db` (us-central1) - WORKING
- **Current RSS Config:** 15 generic feeds in `rss_sources.yaml`

### rssatoms
- **TIER1_BEST_FEEDS.csv:** 97 high-quality feeds (score 75-100)
- **Categories:** 11 (AI, Data Science, Hardware, Automotive, Marine, etc.)
- **AI/Tech Feeds:** 12 premium sources (MIT, OpenAI, DeepMind, Hugging Face, etc.)

## Phase 1: Feed Integration (2 subtasks)

### 1.1 Import TIER 1 AI/Tech Feeds to Perception

**Task:** Add the 12 AI/Tech TIER 1 feeds to perception's rss_sources.yaml

| Feed | URL | Score |
|------|-----|-------|
| AI News | artificialintelligence-news.com/feed/ | 95 |
| MIT News AI | news.mit.edu/rss/topic/artificial-intelligence2 | 100 |
| OpenAI Blog | openai.com/blog/rss.xml | 75 |
| DeepMind Blog | deepmind.com/blog/feed/basic/ | 75 |
| Hugging Face | huggingface.co/blog/feed.xml | 75 |
| ML Mastery | machinelearningmastery.com/feed/ | 80 |
| Towards Data Science | towardsdatascience.com/feed | 85 |
| Analytics Vidhya | analyticsvidhya.com/feed/ | 95 |
| KDnuggets | kdnuggets.com/feed | 80 |
| Tom's Hardware | tomshardware.com/feeds/all | 85 |
| The Gradient | thegradient.pub/rss/ | 85 |
| OpenAI News | openai.com/news/rss.xml | 95 |

**Acceptance:** Feeds added, MCP service updated, successful ingestion run

### 1.2 Create Feed Category Mapping

**Task:** Map rssatoms categories to perception sections

```yaml
rssatoms_to_perception_mapping:
  "AI Developer Tools": "tech"
  "AI Industry News": "tech"
  "AI Research & Academic": "tech"
  "AI Research & Machine Learning": "tech"
  "Data Science": "tech"
  "Hardware & Tech News": "tech"
  "Automotive Repair": "industry"
  "Heavy Equipment": "industry"
  "Electronics Repair": "industry"
  "Boats and Marine": "industry"
```

**Acceptance:** Category mapping implemented in agent scoring logic

## Phase 2: Discord Integration (3 subtasks)

### 2.1 Create Discord Webhook for Perception

**Task:** Set up Discord server + webhook for alert delivery

```
Discord Server: "Perception Intelligence Demo"
├── #welcome (server intro, how it works)
├── #daily-brief (daily executive summaries)
├── #breaking-alerts (high-relevance articles)
├── #tech-news (AI/ML/Tech category)
├── #industry-news (Repair/Equipment category)
└── #system-status (ingestion run status)
```

**Implementation:**
1. Create Discord server or use existing
2. Create webhooks for each channel
3. Store webhook URLs in Secret Manager

**Acceptance:** Webhooks created, URLs stored securely

### 2.2 Add Discord Delivery to MCP Service

**Task:** Implement send_discord_alert MCP tool

```python
@app.post("/mcp/tools/send_discord_alert")
async def send_discord_alert(
    webhook_url: str,
    title: str,
    content: str,
    color: int = 0x3498db,  # Blue
    article_url: str = None
):
    """Send formatted alert to Discord channel."""
    embed = {
        "title": title,
        "description": content[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "Perception Intelligence"}
    }
    if article_url:
        embed["url"] = article_url

    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json={"embeds": [embed]})
```

**Acceptance:** MCP endpoint deployed, test alerts working

### 2.3 Wire Agent Pipeline to Discord Delivery

**Task:** Add Discord alerts to Agent 7 (or create Agent 9)

**Alert Triggers:**
- **Daily Brief Complete:** Post to #daily-brief
- **High-Relevance Article (score > 8.5):** Post to #breaking-alerts
- **Ingestion Run Status:** Post to #system-status

**Acceptance:** Automated alerts flowing to Discord

## Phase 3: Demo Experience (2 subtasks)

### 3.1 Create Invite Flow

**Task:** Streamline demo onboarding

1. Generate Discord invite link (non-expiring)
2. Create welcome message with:
   - What Perception does
   - What each channel shows
   - How often updates arrive
   - How to request features

**Acceptance:** Single-click invite, clear onboarding

### 3.2 Create Demo Script

**Task:** Document demo flow for stakeholder presentations

```markdown
## Perception Intelligence Demo Script

1. **Invite to Discord** (30 sec)
   - Send invite link
   - They join and see welcome channel

2. **Show Daily Brief** (2 min)
   - Navigate to #daily-brief
   - Show latest executive summary
   - Highlight: AI-generated, 5am delivery

3. **Show Breaking Alerts** (2 min)
   - Navigate to #breaking-alerts
   - Show real-time high-relevance articles
   - Highlight: Automatic relevance scoring

4. **Show Source Quality** (1 min)
   - Explain TIER 1 sources (MIT, OpenAI, etc.)
   - Show tech vs industry categorization

5. **Q&A / Feedback** (5 min)
   - Collect feedback
   - Discuss customization options
```

**Acceptance:** Demo script documented, tested with 1 stakeholder

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    rssatoms TIER 1 Feeds                     │
│         (97 curated feeds, score 75-100)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Perception Agent Engine                         │
│         (4241324322704064512)                                │
│                                                              │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐    │
│  │Agent 1  │→→→│Agent 3  │→→→│Agent 4  │→→→│Agent 7  │    │
│  │Harvest  │   │Score    │   │Analyze  │   │Store    │    │
│  └────┬────┘   └─────────┘   └─────────┘   └────┬────┘    │
│       │                                          │          │
└───────┼──────────────────────────────────────────┼──────────┘
        │                                          │
        ▼                                          ▼
┌───────────────────┐                   ┌──────────────────────┐
│   MCP Service     │                   │     Firestore        │
│   (Cloud Run)     │                   │   (perception-db)    │
│                   │                   │                      │
│ fetch_rss_feed    │                   │ /articles            │
│ send_discord_alert│──────────────────▶│ /briefs              │
└────────┬──────────┘                   │ /ingestion_runs      │
         │                              └──────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Discord Server                            │
│                                                              │
│  #daily-brief      ← Executive summaries (6am)              │
│  #breaking-alerts  ← High-relevance articles (real-time)    │
│  #tech-news        ← AI/ML/Tech category                    │
│  #industry-news    ← Repair/Equipment category              │
│  #system-status    ← Ingestion run logs                     │
└─────────────────────────────────────────────────────────────┘
```

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Agent Engine | WORKING | 4241324322704064512 |
| MCP Service | WORKING | Cloud Run deployed |
| Firestore | WORKING | perception-db |
| rssatoms feeds | AVAILABLE | TIER1_BEST_FEEDS.csv |
| Discord | NOT STARTED | Need server + webhooks |
| aiohttp | NOT ADDED | For async Discord calls |

## Estimated Effort

| Phase | Subtasks | Complexity |
|-------|----------|------------|
| Phase 1: Feed Integration | 2 | Low |
| Phase 2: Discord Integration | 3 | Medium |
| Phase 3: Demo Experience | 2 | Low |
| **Total** | **7 subtasks** | **Medium** |

## Success Metrics

1. **Feed Quality:** All 12 AI/Tech TIER 1 feeds ingesting successfully
2. **Discord Delivery:** < 5 min latency from article harvest to Discord alert
3. **Demo Completion:** Successfully demo to 3 stakeholders
4. **Feedback:** Collect actionable feedback for v0.5.0

## Risks

| Risk | Mitigation |
|------|------------|
| Discord rate limits | Batch alerts, use queuing |
| Feed changes/breaks | Monitoring, fallback feeds |
| Stakeholder availability | Pre-record demo video |

## Next Steps

1. Create beads subtasks for each phase
2. Start Phase 1.1 (feed import)
3. Create Discord server (can be done in parallel)

---

**Reference:**
- rssatoms: `/home/jeremy/000-projects/rssatoms/`
- perception: `/home/jeremy/000-projects/perception/`
- bob's-brain ADK patterns: `/home/jeremy/000-projects/bobs-brain-ref/agents/`
