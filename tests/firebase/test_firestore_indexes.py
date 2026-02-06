"""
Firestore Index Validation Tests
================================

Validate that all required composite indexes are defined in firestore.indexes.json.

Missing indexes cause queries to fail with 'query requires an index' errors.
These tests catch index issues BEFORE deployment.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


class TestFirestoreIndexesFile:
    """Validate firestore.indexes.json structure."""

    def test_indexes_file_exists(self, firestore_indexes_path: Path):
        """firestore.indexes.json must exist."""
        assert firestore_indexes_path.exists(), (
            "firestore.indexes.json not found. Create it to define composite indexes."
        )

    def test_indexes_file_is_valid_json(self, firestore_indexes_path: Path):
        """firestore.indexes.json must be valid JSON."""
        try:
            with open(firestore_indexes_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"firestore.indexes.json is not valid JSON: {e}")

    def test_indexes_array_exists(self, firestore_indexes: Dict[str, Any]):
        """firestore.indexes.json must have an 'indexes' array."""
        assert "indexes" in firestore_indexes, (
            "firestore.indexes.json missing 'indexes' array"
        )
        assert isinstance(firestore_indexes["indexes"], list), (
            "firestore.indexes.json 'indexes' must be an array"
        )


class TestRequiredIndexes:
    """Validate that all dashboard-required indexes are defined."""

    def _find_index(
        self,
        indexes: List[Dict[str, Any]],
        collection: str,
        fields: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """
        Find an index matching collection and field requirements.

        Args:
            indexes: List of index definitions
            collection: Collection group name
            fields: Dict of {fieldPath: order} requirements

        Returns:
            Matching index definition or None
        """
        for index in indexes:
            if index.get("collectionGroup") != collection:
                continue

            index_fields = {
                f["fieldPath"]: f.get("order", f.get("arrayConfig"))
                for f in index.get("fields", [])
            }

            # Check if all required fields match
            if all(
                index_fields.get(path) == order
                for path, order in fields.items()
            ):
                return index

        return None

    def test_authors_status_lastpublished_index(self, firestore_indexes: Dict[str, Any]):
        """
        Authors collection requires (status ASC, lastPublished DESC) index.

        Dashboard AuthorsCard queries:
            .where("status", "==", "active")
            .orderBy("lastPublished", direction="DESCENDING")
        """
        indexes = firestore_indexes.get("indexes", [])
        required_fields = {
            "status": "ASCENDING",
            "lastPublished": "DESCENDING"
        }

        index = self._find_index(indexes, "authors", required_fields)
        assert index is not None, (
            "Missing index: authors(status ASC, lastPublished DESC). "
            "AuthorsCard will fail with 'query requires an index' error. "
            "Add to firestore.indexes.json:\n"
            '{\n'
            '  "collectionGroup": "authors",\n'
            '  "queryScope": "COLLECTION",\n'
            '  "fields": [\n'
            '    {"fieldPath": "status", "order": "ASCENDING"},\n'
            '    {"fieldPath": "lastPublished", "order": "DESCENDING"}\n'
            '  ]\n'
            '}'
        )

    def test_articles_relevance_published_index(self, firestore_indexes: Dict[str, Any]):
        """
        Articles collection requires (relevance_score DESC, published_at DESC) index.

        Dashboard and API queries for top articles by relevance.
        """
        indexes = firestore_indexes.get("indexes", [])
        required_fields = {
            "relevance_score": "DESCENDING",
            "published_at": "DESCENDING"
        }

        index = self._find_index(indexes, "articles", required_fields)
        assert index is not None, (
            "Missing index: articles(relevance_score DESC, published_at DESC). "
            "Add to firestore.indexes.json:\n"
            '{\n'
            '  "collectionGroup": "articles",\n'
            '  "queryScope": "COLLECTION",\n'
            '  "fields": [\n'
            '    {"fieldPath": "relevance_score", "order": "DESCENDING"},\n'
            '    {"fieldPath": "published_at", "order": "DESCENDING"}\n'
            '  ]\n'
            '}'
        )

    def test_articles_category_published_index(self, firestore_indexes: Dict[str, Any]):
        """
        Articles collection requires (category ASC, published_at DESC) index.

        Dashboard queries for articles by category.
        """
        indexes = firestore_indexes.get("indexes", [])
        required_fields = {
            "category": "ASCENDING",
            "published_at": "DESCENDING"
        }

        index = self._find_index(indexes, "articles", required_fields)
        assert index is not None, (
            "Missing index: articles(category ASC, published_at DESC). "
            "Add to firestore.indexes.json:\n"
            '{\n'
            '  "collectionGroup": "articles",\n'
            '  "queryScope": "COLLECTION",\n'
            '  "fields": [\n'
            '    {"fieldPath": "category", "order": "ASCENDING"},\n'
            '    {"fieldPath": "published_at", "order": "DESCENDING"}\n'
            '  ]\n'
            '}'
        )

    def test_all_indexes_have_required_fields(self, firestore_indexes: Dict[str, Any]):
        """All indexes must have collectionGroup and fields defined."""
        indexes = firestore_indexes.get("indexes", [])

        for i, index in enumerate(indexes):
            assert "collectionGroup" in index, (
                f"Index {i} missing 'collectionGroup'"
            )
            assert "fields" in index, (
                f"Index {i} ({index.get('collectionGroup', 'unknown')}) missing 'fields'"
            )
            assert len(index["fields"]) >= 2, (
                f"Index {i} ({index.get('collectionGroup', 'unknown')}) "
                "should have at least 2 fields (single-field indexes are automatic)"
            )

    def test_index_fields_have_order(self, firestore_indexes: Dict[str, Any]):
        """All index fields must specify order or arrayConfig."""
        indexes = firestore_indexes.get("indexes", [])

        for index in indexes:
            collection = index.get("collectionGroup", "unknown")
            for field in index.get("fields", []):
                has_order = "order" in field or "arrayConfig" in field
                assert has_order, (
                    f"Index on '{collection}' field '{field.get('fieldPath')}' "
                    "missing 'order' or 'arrayConfig'"
                )


@pytest.mark.integration
class TestIndexesWorkInFirestore:
    """
    Integration tests that verify indexes work against live Firestore.

    These tests actually run the queries that would fail if indexes are missing.
    Requires GCP authentication.
    """

    def test_authors_query_works(self, firestore_db, skip_without_gcp_auth):
        """
        Actually run the authors query that failed.

        This query requires the (status, lastPublished) composite index.
        """
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("authors")
            .where("status", "==", "active")
            .order_by("lastPublished", direction=Query.DESCENDING)
            .limit(5)
        )

        # This will raise if index doesn't exist
        try:
            list(query.stream())
        except Exception as e:
            if "index" in str(e).lower():
                pytest.fail(
                    f"Authors query failed - missing index: {e}\n"
                    "Run: firebase deploy --only firestore:indexes"
                )
            raise

    def test_briefs_query_works(self, firestore_db, skip_without_gcp_auth):
        """Test briefs orderBy date DESC query."""
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("briefs")
            .order_by("date", direction=Query.DESCENDING)
            .limit(1)
        )

        try:
            list(query.stream())
        except Exception as e:
            if "index" in str(e).lower():
                pytest.fail(f"Briefs query failed - missing index: {e}")
            raise

    def test_ingestion_runs_query_works(self, firestore_db, skip_without_gcp_auth):
        """Test ingestion_runs orderBy startedAt DESC query."""
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("ingestion_runs")
            .order_by("startedAt", direction=Query.DESCENDING)
            .limit(10)
        )

        try:
            list(query.stream())
        except Exception as e:
            if "index" in str(e).lower():
                pytest.fail(f"Ingestion runs query failed - missing index: {e}")
            raise

    def test_sources_simple_query_works(self, firestore_db, skip_without_gcp_auth):
        """Test simple sources collection read (no composite index needed)."""
        try:
            docs = list(firestore_db.collection("sources").limit(1).stream())
            # Just verify it doesn't raise
        except Exception as e:
            if "permission" in str(e).lower():
                pytest.fail(f"Sources query failed - permission denied: {e}")
            raise
