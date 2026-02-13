"""
Trigger Router

Orchestration endpoints for running full ingestion pipelines.
Not an MCP tool - this is a higher-level coordinator that calls MCP tools internally.
"""

import asyncio
import hashlib
import logging
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()


class TriggerIngestionRequest(BaseModel):
    """Request schema for trigger ingestion endpoint."""

    trigger: str = Field("manual", description="Trigger source: manual, scheduled, test")
    time_window_hours: int = Field(24, description="Only fetch articles from last N hours", ge=1, le=720)
    max_items_per_source: int = Field(50, description="Max articles per source", ge=1, le=500)


class TriggerIngestionResponse(BaseModel):
    """Response schema for trigger ingestion endpoint."""

    run_id: str
    status: str
    sources_processed: int
    articles_fetched: int
    articles_stored: int
    authors_upserted: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    duration_seconds: float


def load_sources() -> List[Dict[str, Any]]:
    """Load RSS sources from config/rss_sources.yaml."""
    yaml_path = Path(__file__).parent.parent / "config" / "rss_sources.yaml"

    try:
        with open(yaml_path, "r") as f:
            config = yaml.safe_load(f)

        sources = []
        for source in config.get("sources", []):
            if source.get("active", True):
                source_id = source["name"].lower().replace(" ", "-").replace("/", "-")
                sources.append(
                    {
                        "source_id": source_id,
                        "name": source["name"],
                        "url": source["url"],
                        "category": source.get("category", "general"),
                    }
                )

        logger.info(
            json.dumps({"severity": "INFO", "message": f"Loaded {len(sources)} sources from YAML", "router": "trigger"})
        )
        return sources

    except FileNotFoundError:
        logger.error(
            json.dumps({"severity": "ERROR", "message": f"YAML config not found: {yaml_path}", "router": "trigger"})
        )
        return []
    except Exception as e:
        logger.error(json.dumps({"severity": "ERROR", "message": f"Failed to load sources: {e}", "router": "trigger"}))
        return []


async def fetch_single_feed(
    client: httpx.AsyncClient,
    source: Dict[str, Any],
    time_window_hours: int,
    max_items: int,
    run_id: str,
) -> Dict[str, Any]:
    """Fetch a single RSS feed via the local MCP endpoint."""
    try:
        response = await client.post(
            "http://localhost:8080/mcp/tools/fetch_rss_feed",
            json={
                "feed_url": source["url"],
                "time_window_hours": time_window_hours,
                "max_items": max_items,
                "request_id": f"{run_id}_{source['source_id']}",
            },
        )
        response.raise_for_status()
        data = response.json()
        return {
            "source": source,
            "articles": data.get("articles", []),
            "feed_metadata": data.get("feed_metadata"),
            "article_count": data.get("article_count", 0),
        }
    except Exception as e:
        return {
            "source": source,
            "articles": [],
            "feed_metadata": None,
            "article_count": 0,
            "error": str(e),
        }


@router.post("/ingestion", response_model=TriggerIngestionResponse)
async def trigger_ingestion(request: TriggerIngestionRequest):
    """
    Run a full ingestion pipeline across all configured sources.

    Loads sources from rss_sources.yaml, fetches each feed,
    stores articles to Firestore, and upserts author records.
    """
    run_id = f"run-{uuid.uuid4().hex[:12]}"
    start_time = time.time()

    logger.info(
        json.dumps(
            {
                "severity": "INFO",
                "message": "Starting ingestion run",
                "router": "trigger",
                "run_id": run_id,
                "trigger": request.trigger,
                "time_window_hours": request.time_window_hours,
                "max_items_per_source": request.max_items_per_source,
            }
        )
    )

    sources = load_sources()
    if not sources:
        return TriggerIngestionResponse(
            run_id=run_id,
            status="failed",
            sources_processed=0,
            articles_fetched=0,
            articles_stored=0,
            authors_upserted=0,
            errors=[{"message": "No sources loaded from config"}],
            duration_seconds=time.time() - start_time,
        )

    # Fetch all feeds with concurrency control
    semaphore = asyncio.Semaphore(10)
    errors: List[Dict[str, Any]] = []
    all_articles: List[Dict[str, Any]] = []
    sources_processed = 0

    async def fetch_with_semaphore(client, source):
        async with semaphore:
            return await fetch_single_feed(
                client, source, request.time_window_hours, request.max_items_per_source, run_id
            )

    async with httpx.AsyncClient(timeout=60.0) as client:
        tasks = [fetch_with_semaphore(client, s) for s in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            errors.append({"message": str(result)})
            continue

        sources_processed += 1
        source = result["source"]

        if "error" in result:
            errors.append(
                {
                    "source": source["name"],
                    "url": source["url"],
                    "message": result["error"],
                }
            )
            continue

        for raw_article in result["articles"]:
            all_articles.append(
                {
                    "title": raw_article.get("title", "Untitled"),
                    "url": raw_article.get("url", ""),
                    "source_id": source["source_id"],
                    "source_name": source["name"],
                    "category": source["category"],
                    "published_at": raw_article.get("published_at", ""),
                    "summary": raw_article.get("summary"),
                    "content": raw_article.get("raw_content") or raw_article.get("content_snippet"),
                    "categories": raw_article.get("categories", []),
                }
            )

    total_fetched = len(all_articles)

    # Store articles via MCP store_articles endpoint
    articles_stored = 0
    if all_articles:
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Send in batches of 200 to avoid oversized payloads
                batch_size = 200
                for i in range(0, len(all_articles), batch_size):
                    chunk = all_articles[i : i + batch_size]
                    store_response = await client.post(
                        "http://localhost:8080/mcp/tools/store_articles",
                        json={
                            "run_id": run_id,
                            "articles": chunk,
                        },
                    )
                    if store_response.status_code == 200:
                        store_data = store_response.json()
                        articles_stored += store_data.get("stored_count", 0)
                    else:
                        errors.append(
                            {
                                "message": f"store_articles returned {store_response.status_code}",
                                "batch_start": i,
                            }
                        )
        except Exception as e:
            errors.append({"message": f"store_articles failed: {e}"})

    # Upsert authors (group articles by feed URL)
    authors_upserted = 0
    feed_groups: Dict[str, Dict[str, Any]] = {}
    for result in results:
        if isinstance(result, Exception) or "error" in result:
            continue
        source = result["source"]
        feed_url = source["url"]
        if feed_url not in feed_groups:
            feed_groups[feed_url] = {
                "articles": [],
                "feed_metadata": result.get("feed_metadata"),
            }
        for raw_article in result["articles"]:
            feed_groups[feed_url]["articles"].append(
                {
                    "title": raw_article.get("title", "Untitled"),
                    "url": raw_article.get("url", ""),
                    "source_id": source["source_id"],
                    "published_at": raw_article.get("published_at", ""),
                    "summary": raw_article.get("summary"),
                    "categories": raw_article.get("categories", []),
                }
            )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            for feed_url, group in feed_groups.items():
                if not group["articles"]:
                    continue
                try:
                    resp = await client.post(
                        "http://localhost:8080/mcp/tools/upsert_author",
                        json={
                            "feed_url": feed_url,
                            "articles": group["articles"],
                            "feed_metadata": group["feed_metadata"],
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data.get("status") in ("created", "updated"):
                            authors_upserted += 1
                except Exception as e:
                    errors.append({"message": f"upsert_author failed for {feed_url}: {e}"})
    except Exception as e:
        errors.append({"message": f"Author upsert phase failed: {e}"})

    duration = time.time() - start_time
    status = "completed" if not errors else "completed_with_errors"

    logger.info(
        json.dumps(
            {
                "severity": "INFO",
                "message": "Ingestion run completed",
                "router": "trigger",
                "run_id": run_id,
                "status": status,
                "sources_processed": sources_processed,
                "articles_fetched": total_fetched,
                "articles_stored": articles_stored,
                "authors_upserted": authors_upserted,
                "error_count": len(errors),
                "duration_seconds": round(duration, 2),
            }
        )
    )

    return TriggerIngestionResponse(
        run_id=run_id,
        status=status,
        sources_processed=sources_processed,
        articles_fetched=total_fetched,
        articles_stored=articles_stored,
        authors_upserted=authors_upserted,
        errors=errors[:50],  # Cap errors to avoid huge responses
        duration_seconds=round(duration, 2),
    )
