"""
Storage Tool Router

Handles Firestore writes for articles and data persistence.
Real Firestore batch writes for both store_articles and upsert_author.
"""

import hashlib
import logging
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from fastapi import APIRouter
from pydantic import BaseModel, Field
from google.cloud import firestore

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic Models
class Article(BaseModel):
    """Article to store in Firestore."""

    title: str
    url: str
    source_id: str
    published_at: str
    summary: Optional[str] = None
    content: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_tags: List[str] = Field(default_factory=list)
    relevance_score: Optional[float] = None
    categories: List[str] = Field(default_factory=list)
    source_name: Optional[str] = None
    category: Optional[str] = None


class StoreArticlesRequest(BaseModel):
    """Request schema for store_articles tool."""

    run_id: str = Field(..., description="Ingestion run ID")
    articles: List[Article] = Field(..., description="Articles to store")


class StoreArticlesResponse(BaseModel):
    """Response schema for store_articles tool."""

    run_id: str
    stored_count: int
    failed_count: int
    failed_urls: List[str] = Field(default_factory=list)
    storage_stats: Dict[str, Any]


class FeedMetadata(BaseModel):
    """Feed-level metadata for author tracking."""

    title: Optional[str] = None
    link: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


class UpsertAuthorRequest(BaseModel):
    """Request schema for upsert_author tool."""

    feed_url: str = Field(..., description="RSS feed URL")
    articles: List[Article] = Field(..., description="Articles from this feed")
    feed_metadata: Optional[FeedMetadata] = Field(None, description="Feed-level metadata")


class UpsertAuthorResponse(BaseModel):
    """Response schema for upsert_author tool."""

    author_id: Optional[str]
    author_name: Optional[str] = None
    status: str  # "created", "updated", "skipped", "failed"
    error: Optional[str] = None


# Tool Endpoint
@router.post("/store_articles", response_model=StoreArticlesResponse)
async def store_articles(request: StoreArticlesRequest):
    """
    Batch write articles to Firestore /articles collection.

    Deduplicates by URL, uses batch writes (max 500 per batch),
    and handles partial failures gracefully.
    """
    logger.info(
        json.dumps(
            {
                "severity": "INFO",
                "message": "Storing articles",
                "mcp_tool": "store_articles",
                "run_id": request.run_id,
                "article_count": len(request.articles),
            }
        )
    )

    try:
        db = firestore.Client(project="perception-with-intent", database="perception-db")

        # Deduplicate articles by URL
        seen_urls = set()
        unique_articles = []
        for article in request.articles:
            if article.url and article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        duplicates_skipped = len(request.articles) - len(unique_articles)
        stored_count = 0
        failed_count = 0
        failed_urls = []

        # Batch write (Firestore limit: 500 per batch)
        batch_size = 500
        for i in range(0, len(unique_articles), batch_size):
            batch = db.batch()
            chunk = unique_articles[i : i + batch_size]

            for article in chunk:
                try:
                    url_hash = hashlib.sha256(article.url.encode()).hexdigest()[:16]
                    doc_id = f"art-{url_hash}"
                    doc_ref = db.collection("articles").document(doc_id)

                    now = datetime.now(timezone.utc)
                    doc_data = {
                        "title": article.title,
                        "url": article.url,
                        "source_id": article.source_id,
                        "published_at": article.published_at,
                        "summary": article.summary,
                        "content": article.content,
                        "ai_summary": article.ai_summary,
                        "ai_tags": article.ai_tags,
                        "relevance_score": article.relevance_score,
                        "categories": article.categories,
                        "source_name": article.source_name,
                        "category": article.category,
                        "stored_at": now,
                        "run_id": request.run_id,
                    }
                    # Remove None values to avoid overwriting existing data
                    doc_data = {k: v for k, v in doc_data.items() if v is not None}

                    batch.set(doc_ref, doc_data, merge=True)
                    stored_count += 1
                except Exception as e:
                    logger.warning(
                        json.dumps(
                            {"severity": "WARNING", "message": f"Failed to prepare article: {e}", "url": article.url}
                        )
                    )
                    failed_count += 1
                    failed_urls.append(article.url)

            batch.commit()

        response = StoreArticlesResponse(
            run_id=request.run_id,
            stored_count=stored_count,
            failed_count=failed_count,
            failed_urls=failed_urls,
            storage_stats={
                "firestore_writes": stored_count,
                "duplicates_skipped": duplicates_skipped,
                "batch_count": (len(unique_articles) + batch_size - 1) // batch_size,
            },
        )

        logger.info(
            json.dumps(
                {
                    "severity": "INFO",
                    "message": "Articles stored successfully",
                    "mcp_tool": "store_articles",
                    "run_id": request.run_id,
                    "stored_count": response.stored_count,
                    "duplicates_skipped": duplicates_skipped,
                }
            )
        )

        return response

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "severity": "ERROR",
                    "message": "Failed to store articles",
                    "mcp_tool": "store_articles",
                    "run_id": request.run_id,
                    "error": str(e),
                }
            )
        )

        return StoreArticlesResponse(
            run_id=request.run_id,
            stored_count=0,
            failed_count=len(request.articles),
            failed_urls=[a.url for a in request.articles],
            storage_stats={"error": str(e)},
        )


@router.post("/upsert_author", response_model=UpsertAuthorResponse)
async def upsert_author(request: UpsertAuthorRequest):
    """
    Create or update author record based on fetched articles.

    This endpoint tracks authors/feeds and their freshness for the
    author-focused dashboard. It updates:
    - lastPublished: Most recent article date
    - lastFetched: Current timestamp
    - articleCount: Incremented by articles count
    - categories: Merged from article categories

    Phase implementation: Real Firestore writes.
    """
    logger.info(
        json.dumps(
            {
                "severity": "INFO",
                "message": "Upserting author",
                "mcp_tool": "upsert_author",
                "feed_url": request.feed_url,
                "article_count": len(request.articles),
            }
        )
    )

    if not request.articles:
        return UpsertAuthorResponse(author_id=None, status="skipped", error="No articles to process")

    try:
        # Initialize Firestore
        db = firestore.Client(project="perception-with-intent", database="perception-db")

        # Generate author ID from feed URL
        url_hash = hashlib.sha256(request.feed_url.encode()).hexdigest()[:16]
        author_id = f"author-{url_hash}"

        # Find newest article
        newest_published = None
        for article in request.articles:
            pub_at = article.published_at
            if pub_at:
                try:
                    dt = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
                    if newest_published is None or dt > newest_published:
                        newest_published = dt
                except (ValueError, TypeError):
                    pass

        if newest_published is None:
            newest_published = datetime.now(timezone.utc)

        # Extract author name
        author_name = None
        if request.feed_metadata:
            author_name = request.feed_metadata.title or request.feed_metadata.author

        if not author_name:
            # Try to get from first article
            for article in request.articles:
                if hasattr(article, "author") and article.author:
                    author_name = article.author
                    break

        if not author_name:
            # Fallback to domain
            parsed = urlparse(request.feed_url)
            author_name = parsed.netloc.replace("www.", "")

        # Extract website URL
        website_url = None
        if request.feed_metadata and request.feed_metadata.link:
            website_url = request.feed_metadata.link
        else:
            parsed = urlparse(request.feed_url)
            website_url = f"{parsed.scheme}://{parsed.netloc}"

        # Collect categories
        categories = set()
        for article in request.articles:
            for cat in article.categories:
                if cat:
                    categories.add(cat)

        # Build update document
        now = datetime.now(timezone.utc)
        update_data = {
            "name": author_name,
            "feedUrl": request.feed_url,
            "websiteUrl": website_url,
            "lastPublished": newest_published,
            "lastFetched": now,
            "updatedAt": now,
            "status": "active",
            "consecutiveErrors": 0,
        }

        if categories:
            update_data["categories"] = list(categories)

        if request.feed_metadata and request.feed_metadata.description:
            update_data["feedDescription"] = request.feed_metadata.description

        # Check if document exists
        doc_ref = db.collection("authors").document(author_id)
        doc = doc_ref.get()

        if doc.exists:
            existing_data = doc.to_dict()
            existing_count = existing_data.get("articleCount", 0)
            update_data["articleCount"] = existing_count + len(request.articles)
            status = "updated"
        else:
            update_data["createdAt"] = now
            update_data["articleCount"] = len(request.articles)
            status = "created"

        # Write to Firestore
        doc_ref.set(update_data, merge=True)

        logger.info(
            json.dumps(
                {
                    "severity": "INFO",
                    "message": f"Author {status}",
                    "mcp_tool": "upsert_author",
                    "author_id": author_id,
                    "author_name": author_name,
                    "status": status,
                }
            )
        )

        return UpsertAuthorResponse(author_id=author_id, author_name=author_name, status=status)

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "severity": "ERROR",
                    "message": "Failed to upsert author",
                    "mcp_tool": "upsert_author",
                    "feed_url": request.feed_url,
                    "error": str(e),
                }
            )
        )

        return UpsertAuthorResponse(author_id=None, status="failed", error=str(e))
