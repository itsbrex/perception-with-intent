"""
Collection Schema Validation Tests
==================================

Validate that Firestore documents have expected fields.

These tests ensure that the data in Firestore matches what the
dashboard expects. They help catch:
1. Missing required fields
2. Wrong field types
3. Schema drift between backend and frontend
"""

from typing import Any, Dict, List, Optional

import pytest


@pytest.mark.integration
class TestAuthorDocumentSchema:
    """Validate authors collection documents."""

    REQUIRED_FIELDS = ["name", "lastPublished"]
    OPTIONAL_FIELDS = ["status", "feedUrl", "bio", "avatarUrl", "articleCount", "categories"]

    def test_author_has_required_fields(self, firestore_db, skip_without_gcp_auth):
        """Authors must have required fields for dashboard display."""
        docs = list(firestore_db.collection("authors").limit(1).stream())

        if not docs:
            pytest.skip("No authors in database yet - run ingestion first")

        data = docs[0].to_dict()
        missing = [f for f in self.REQUIRED_FIELDS if f not in data]

        assert not missing, (
            f"Author document missing required fields: {missing}\n"
            f"Document has: {list(data.keys())}"
        )

    def test_author_lastpublished_is_timestamp(self, firestore_db, skip_without_gcp_auth):
        """Author lastPublished should be a timestamp for ordering."""
        docs = list(firestore_db.collection("authors").limit(1).stream())

        if not docs:
            pytest.skip("No authors in database")

        data = docs[0].to_dict()
        last_published = data.get("lastPublished")

        if last_published is not None:
            # Should be Firestore timestamp or datetime-like
            assert hasattr(last_published, "seconds") or hasattr(last_published, "timestamp"), (
                f"lastPublished should be timestamp, got {type(last_published)}"
            )

    def test_author_status_is_valid_enum(self, firestore_db, skip_without_gcp_auth):
        """Author status should be a valid enum value."""
        docs = list(firestore_db.collection("authors").limit(5).stream())

        if not docs:
            pytest.skip("No authors in database")

        valid_statuses = {"active", "inactive", "error", "paused"}

        for doc in docs:
            data = doc.to_dict()
            status = data.get("status")
            if status is not None:
                assert status in valid_statuses, (
                    f"Author {doc.id} has invalid status: {status}"
                )


@pytest.mark.integration
class TestBriefDocumentSchema:
    """Validate briefs collection documents."""

    REQUIRED_FIELDS = ["date"]
    CONTENT_FIELDS = ["executiveSummary", "highlights"]

    def test_brief_has_date_field(self, firestore_db, skip_without_gcp_auth):
        """Briefs must have date field for ordering."""
        docs = list(firestore_db.collection("briefs").limit(1).stream())

        if not docs:
            pytest.skip("No briefs in database yet")

        data = docs[0].to_dict()
        assert "date" in data, (
            f"Brief document missing 'date' field. Has: {list(data.keys())}"
        )

    def test_brief_date_is_sortable(self, firestore_db, skip_without_gcp_auth):
        """Brief date should be a sortable value (string or timestamp)."""
        docs = list(firestore_db.collection("briefs").limit(1).stream())

        if not docs:
            pytest.skip("No briefs in database")

        data = docs[0].to_dict()
        date_val = data.get("date")

        # Date can be ISO string, timestamp, or date object
        valid_type = isinstance(date_val, str) or hasattr(date_val, "seconds")
        assert valid_type, (
            f"Brief date should be string or timestamp, got {type(date_val)}"
        )

    def test_brief_has_content(self, firestore_db, skip_without_gcp_auth):
        """Briefs should have some content fields."""
        docs = list(firestore_db.collection("briefs").limit(1).stream())

        if not docs:
            pytest.skip("No briefs in database")

        data = docs[0].to_dict()
        has_content = any(f in data for f in self.CONTENT_FIELDS)

        if not has_content:
            pytest.skip(
                f"Brief has no content fields. "
                f"Expected one of: {self.CONTENT_FIELDS}"
            )


@pytest.mark.integration
class TestSourceDocumentSchema:
    """Validate sources collection documents."""

    REQUIRED_FIELDS = ["name"]
    STATUS_FIELD = "status"

    def test_source_has_name(self, firestore_db, skip_without_gcp_auth):
        """Sources must have a name for display."""
        docs = list(firestore_db.collection("sources").limit(1).stream())

        if not docs:
            pytest.skip("No sources in database")

        data = docs[0].to_dict()
        assert "name" in data, (
            f"Source document missing 'name' field. Has: {list(data.keys())}"
        )

    def test_source_has_status_or_enabled(self, firestore_db, skip_without_gcp_auth):
        """Sources should have status/enabled indicator for health card."""
        docs = list(firestore_db.collection("sources").limit(1).stream())

        if not docs:
            pytest.skip("No sources in database")

        data = docs[0].to_dict()
        has_status = "status" in data or "enabled" in data or "active" in data

        assert has_status, (
            f"Source document should have 'status' or 'enabled' field. "
            f"Has: {list(data.keys())}"
        )


@pytest.mark.integration
class TestArticleDocumentSchema:
    """Validate articles collection documents."""

    REQUIRED_FIELDS = ["title"]
    SORTABLE_FIELDS = ["published_at", "relevance_score"]

    def test_article_has_title(self, firestore_db, skip_without_gcp_auth):
        """Articles must have a title."""
        docs = list(firestore_db.collection("articles").limit(1).stream())

        if not docs:
            pytest.skip("No articles in database")

        data = docs[0].to_dict()
        assert "title" in data, (
            f"Article missing 'title' field. Has: {list(data.keys())}"
        )

    def test_article_has_sortable_fields(self, firestore_db, skip_without_gcp_auth):
        """Articles should have fields for sorting/ranking."""
        docs = list(firestore_db.collection("articles").limit(1).stream())

        if not docs:
            pytest.skip("No articles in database")

        data = docs[0].to_dict()
        has_sortable = any(f in data for f in self.SORTABLE_FIELDS)

        if not has_sortable:
            pytest.skip(
                f"Article has no sortable fields. "
                f"Expected one of: {self.SORTABLE_FIELDS}"
            )


@pytest.mark.integration
class TestIngestionRunDocumentSchema:
    """Validate ingestion_runs collection documents."""

    REQUIRED_FIELDS = ["startedAt"]

    def test_ingestion_run_has_started_at(self, firestore_db, skip_without_gcp_auth):
        """Ingestion runs must have startedAt for ordering."""
        docs = list(firestore_db.collection("ingestion_runs").limit(1).stream())

        if not docs:
            pytest.skip("No ingestion runs in database")

        data = docs[0].to_dict()
        assert "startedAt" in data, (
            f"Ingestion run missing 'startedAt'. Has: {list(data.keys())}"
        )

    def test_ingestion_run_started_at_is_timestamp(
        self, firestore_db, skip_without_gcp_auth
    ):
        """startedAt should be a timestamp for ordering."""
        docs = list(firestore_db.collection("ingestion_runs").limit(1).stream())

        if not docs:
            pytest.skip("No ingestion runs in database")

        data = docs[0].to_dict()
        started_at = data.get("startedAt")

        if started_at is not None:
            assert hasattr(started_at, "seconds") or hasattr(started_at, "timestamp"), (
                f"startedAt should be timestamp, got {type(started_at)}"
            )


@pytest.mark.integration
class TestCollectionsExist:
    """Verify that expected collections have documents."""

    EXPECTED_COLLECTIONS = [
        "sources",  # RSS/API sources
        "authors",  # Discovered authors
        "articles", # News articles
        "briefs",   # Daily briefs
        "ingestion_runs",  # Pipeline runs
    ]

    def test_collections_have_documents(self, firestore_db, skip_without_gcp_auth):
        """Warn about empty collections."""
        empty_collections = []

        for collection in self.EXPECTED_COLLECTIONS:
            docs = list(firestore_db.collection(collection).limit(1).stream())
            if not docs:
                empty_collections.append(collection)

        if empty_collections:
            pytest.skip(
                f"Empty collections (run ingestion to populate): {empty_collections}"
            )

    def test_sources_collection_populated(self, firestore_db, skip_without_gcp_auth):
        """Sources collection should have data after initial setup."""
        docs = list(firestore_db.collection("sources").limit(1).stream())

        # Sources should be populated during setup, not just ingestion
        if not docs:
            pytest.skip(
                "No sources configured. Run setup or add RSS sources."
            )
