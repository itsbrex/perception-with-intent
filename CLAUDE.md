# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Task Tracking (Beads / bd)

Use `bd` for ALL tasks/issues (no markdown TODO lists).
- Start of session: `bd ready`
- Create work: `bd create "Title" -p 1 --description "Context + acceptance criteria"`
- Update status: `bd update <id> --status in_progress`
- Finish: `bd close <id> --reason "Done"`
- End of session: `bd sync` (flush/import/export + git sync)
- After upgrading `bd`, run: `bd info --whats-new`
- If `bd info` warns about hooks, run: `bd hooks install`

## Project Overview

**Perception** is an AI news intelligence platform using Google's Agent Development Kit (ADK). 8 specialized agents on Vertex AI Agent Engine coordinate to collect, analyze, and synthesize news into executive briefs.

**GCP Project:** `perception-with-intent`
**Dashboard:** https://perception-with-intent.web.app
**MCP Service:** https://perception-mcp-w53xszfqnq-uc.a.run.app
**Agent Engine ID:** `4241324322704064512`

## Architecture

```
Firebase Dashboard (React)
    ↓
Vertex AI Agent Engine (8 Agents via A2A Protocol)
    ↓
Cloud Run MCP Service (7 tool endpoints)
    ↓
Firestore (articles, daily_summaries, topics_to_monitor)
```

**Key principle:** Firebase = humans, Agents = thinking, MCPs = doing, Firestore = storage.

### Agent System (perception_app/perception_agent/agents/)

| Agent | YAML Config | Role |
|-------|-------------|------|
| 0 | `agent_0_orchestrator.yaml` | Editor-in-Chief, coordinates workflow |
| 1 | `agent_1_source_harvester.yaml` | Fetches news from RSS/APIs |
| 2 | `agent_2_topic_manager.yaml` | Manages tracked keywords |
| 3 | `agent_3_relevance_ranking.yaml` | Scores articles 1-10 |
| 4 | `agent_4_brief_writer.yaml` | Generates summaries |
| 5 | `agent_5_alert_anomaly.yaml` | Detects alerts |
| 6 | `agent_6_validator.yaml` | Data quality checks |
| 7 | `agent_7_storage_manager.yaml` | Firestore persistence |
| 8 | `agent_8_tech_editor.yaml` | Technology section editor |

### MCP Service (perception_app/mcp_service/)

FastAPI endpoints at `/mcp/tools/*`:
- `fetch_rss_feed` - RSS fetching (real implementation)
- `fetch_api_feed`, `fetch_webpage` - Content fetching (stubbed)
- `store_articles`, `generate_brief` - Storage/synthesis (stubbed)
- `log_ingestion_run`, `send_notification` - Ops (stubbed)

## Commands

### Setup
```bash
make install                    # Create venv and install deps
gcloud auth application-default login
gcloud config set project perception-with-intent
```

### Development
```bash
make dev                        # Run local ADK server (localhost:8080)
# Or directly:
python -m perception_app.main --host 127.0.0.1 --port 8080

# Verify agent configs
python perception_app/agent_engine_app.py
```

### Testing
```bash
# Run all tests
make test
# Or: pytest tests/ -v --cov=perception_app

# Run specific test suites (as CI does)
pytest tests/unit/ -v --no-cov
pytest tests/api/ -v --no-cov
pytest tests/mcp/ -v --no-cov
pytest tests/agent/ -v --no-cov
pytest tests/security/ -v --no-cov

# Run single test file
pytest tests/unit/test_rss_parsing.py -v

# Full production suite (~5,196 tests)
./scripts/run_all_tests.sh
```

### Linting
```bash
make lint                       # Run all linters
make format                     # Auto-format with black

# Individual tools
black --check perception_app/
ruff check perception_app/
mypy perception_app/
```

### Deployment
```bash
# MCP to Cloud Run
gcloud run deploy perception-mcp \
  --source perception_app/mcp_service \
  --region us-central1

# Agent Engine
./scripts/deploy_agent_engine.sh

# Dashboard
cd dashboard && npm run build && firebase deploy --only hosting

# Terraform
cd infra/terraform/envs/dev
tofu init && tofu plan && tofu apply
```

### Verify MCP is Alive
```bash
curl https://perception-mcp-w53xszfqnq-uc.a.run.app/health

curl -X POST https://perception-mcp-w53xszfqnq-uc.a.run.app/mcp/tools/fetch_rss_feed \
  -H "Content-Type: application/json" \
  -d '{"feed_url": "https://news.ycombinator.com/rss", "max_items": 10}'
```

## Project Structure

```
perception/
├── perception_app/
│   ├── main.py                    # Dev entrypoint (uvicorn)
│   ├── agent_engine_app.py        # Production entrypoint (Vertex AI)
│   ├── perception_agent/
│   │   ├── agents/                # Agent YAML configs (agent_0-8)
│   │   ├── tools/                 # Python tools per agent (agent_*_tools.py)
│   │   └── config/
│   │       └── rss_sources.yaml   # RSS feed sources
│   ├── jvp_agent/                 # A2A protocol wrapper
│   │   ├── agent.yaml             # JVP agent config
│   │   ├── a2a.py                 # A2A protocol implementation
│   │   └── memory.py              # Context caching
│   └── mcp_service/
│       ├── main.py                # FastAPI app
│       └── routers/               # Tool endpoints (rss.py, storage.py, etc.)
├── dashboard/                     # React + Vite + TypeScript
├── infra/terraform/               # OpenTofu IaC
├── scripts/
│   ├── dev_run_adk.sh            # Local dev server
│   ├── deploy_agent_engine.sh    # Deploy to Vertex AI
│   ├── run_all_tests.sh          # Full test suite
│   └── run_ingestion_once.py     # Manual ingestion trigger
├── tests/
│   ├── unit/                      # Unit tests
│   ├── api/                       # API tests
│   ├── mcp/                       # MCP router tests
│   ├── agent/                     # Agent tests
│   ├── security/                  # Security tests
│   └── factories/                 # Test data factories
└── 000-docs/                      # Technical documentation
```

## Key Files

- `perception_app/agent_engine_app.py:36` - Agent loading function
- `perception_app/perception_agent/agents/agent_0_orchestrator.yaml:1` - Root orchestrator config
- `perception_app/mcp_service/main.py:39` - MCP FastAPI app
- `.github/workflows/ci.yml` - CI pipeline (lint, test, security, tofu)

## CI/CD

Push to `main` triggers GitHub Actions:
1. **lint** - black, ruff, mypy
2. **test** - pytest (unit, api, mcp, agent, security)
3. **security** - safety check dependencies
4. **tofu** - Terraform/OpenTofu validate

Deployment workflows:
- `.github/workflows/deploy-mcp.yml` - MCP to Cloud Run
- `.github/workflows/deploy-agent-engine.yml` - Agents to Vertex AI
- `.github/workflows/deploy-dashboard.yml` - Dashboard to Firebase

Uses Workload Identity Federation (WIF) for keyless GCP auth.

## Tech Stack

- **Agents:** Google ADK, Vertex AI Agent Engine, A2A Protocol
- **AI Model:** Gemini 2.0 Flash
- **MCP Service:** FastAPI on Cloud Run
- **Database:** Firestore (us-central1, `perception-db`)
- **Dashboard:** React 18 + Vite + TypeScript + TailwindCSS
- **IaC:** OpenTofu (Terraform-compatible)
- **Observability:** Cloud Logging, OpenTelemetry (partial)

## Cloud-Only MCP Policy

MCPs run ONLY on Cloud Run. No localhost MCP servers:
- ✅ Agents: Local development OK (`make dev`)
- ❌ MCP: Cloud Run only (no local testing)
- ✅ Tests: Use staging Cloud Run URLs

## Environment Variables

Local development needs no env vars. Production requires:
```bash
VERTEX_PROJECT_ID=perception-with-intent
VERTEX_LOCATION=us-central1
VERTEX_AGENT_ENGINE_ID=4241324322704064512
```

## Documentation

All docs in `000-docs/` with naming convention: `PREFIX-TYPE-CATEGORY-description.md`
- `6767-*` = Evergreen (architecture, guides, plans)
- `0XX-*` = Sequential (AARs, phase reports)

Key docs:
- `6767-AT-ARCH-observability-and-monitoring.md` - Monitoring guide
- `6767-OD-GUID-agent-engine-deploy.md` - Deployment guide
- `6767-PP-PLAN-release-log.md` - Version history
