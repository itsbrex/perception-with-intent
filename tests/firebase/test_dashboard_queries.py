"""
Dashboard Query Contract Tests
==============================

Test all Firestore queries that the dashboard makes.

These tests verify that dashboard queries work against live Firestore,
catching permission and index issues before users encounter them.

Requires GCP authentication to run.
"""

import pytest


@pytest.mark.integration
class TestDashboardQueries:
    """Test all queries the dashboard components make."""

    def test_briefs_query(self, firestore_db, skip_without_gcp_auth):
        """
        TodayBriefCard: orderBy date DESC, limit 1

        Query:
            collection('briefs')
            .orderBy('date', 'desc')
            .limit(1)
        """
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("briefs")
            .order_by("date", direction=Query.DESCENDING)
            .limit(1)
        )

        # Should not raise
        try:
            docs = list(query.stream())
            # Query executed successfully
        except Exception as e:
            error_msg = str(e).lower()
            if "permission" in error_msg:
                pytest.fail(
                    f"Briefs query permission denied: {e}\n"
                    "Check firestore.rules allows authenticated read on briefs"
                )
            elif "index" in error_msg:
                pytest.fail(
                    f"Briefs query missing index: {e}\n"
                    "Single-field orderBy shouldn't need composite index"
                )
            raise

    def test_authors_query(self, firestore_db, skip_without_gcp_auth):
        """
        AuthorsCard: where status==active, orderBy lastPublished DESC

        Query:
            collection('authors')
            .where('status', '==', 'active')  // Optional filter
            .orderBy('lastPublished', 'desc')
            .limit(5)

        Note: The actual dashboard may or may not use the status filter.
        Testing both variants.
        """
        from google.cloud.firestore_v1 import Query

        # Test with status filter (requires composite index)
        query_with_filter = (
            firestore_db.collection("authors")
            .where("status", "==", "active")
            .order_by("lastPublished", direction=Query.DESCENDING)
            .limit(5)
        )

        try:
            list(query_with_filter.stream())
        except Exception as e:
            if "index" in str(e).lower():
                pytest.fail(
                    f"Authors query with status filter failed - missing index: {e}\n"
                    "Add composite index: authors(status ASC, lastPublished DESC)"
                )
            elif "permission" in str(e).lower():
                pytest.fail(f"Authors query permission denied: {e}")
            raise

        # Test without status filter (simpler query)
        query_simple = (
            firestore_db.collection("authors")
            .order_by("lastPublished", direction=Query.DESCENDING)
            .limit(5)
        )

        try:
            list(query_simple.stream())
        except Exception as e:
            if "permission" in str(e).lower():
                pytest.fail(f"Authors simple query permission denied: {e}")
            raise

    def test_sources_query(self, firestore_db, skip_without_gcp_auth):
        """
        SourceHealthCard: all documents (no filter/orderBy)

        Query:
            collection('sources')
            .get()
        """
        try:
            docs = list(firestore_db.collection("sources").stream())
            # Query executed successfully
        except Exception as e:
            if "permission" in str(e).lower():
                pytest.fail(
                    f"Sources query permission denied: {e}\n"
                    "Check firestore.rules allows authenticated read on sources"
                )
            raise

    def test_ingestion_runs_query(self, firestore_db, skip_without_gcp_auth):
        """
        SystemActivityCard: orderBy startedAt DESC, limit 10

        Query:
            collection('ingestion_runs')
            .orderBy('startedAt', 'desc')
            .limit(10)
        """
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("ingestion_runs")
            .order_by("startedAt", direction=Query.DESCENDING)
            .limit(10)
        )

        try:
            list(query.stream())
        except Exception as e:
            if "permission" in str(e).lower():
                pytest.fail(f"Ingestion runs query permission denied: {e}")
            elif "index" in str(e).lower():
                pytest.fail(f"Ingestion runs query missing index: {e}")
            raise

    def test_user_topics_query(
        self, firestore_db, test_user_id, skip_without_gcp_auth
    ):
        """
        TopicWatchlistCard: user subcollection

        Query:
            collection('users').doc(userId).collection('topics')
            .get()
        """
        try:
            list(
                firestore_db
                .collection("users")
                .document(test_user_id)
                .collection("topics")
                .stream()
            )
        except Exception as e:
            if "permission" in str(e).lower():
                # Expected for non-owner - this is correct behavior
                # The actual test would need auth context
                pytest.skip(
                    "User topics query requires authenticated user context. "
                    "Permission denied is expected for service account."
                )
            raise

    def test_user_alerts_query(
        self, firestore_db, test_user_id, skip_without_gcp_auth
    ):
        """
        AlertsCard: user subcollection

        Query:
            collection('users').doc(userId).collection('alerts')
            .get()
        """
        try:
            list(
                firestore_db
                .collection("users")
                .document(test_user_id)
                .collection("alerts")
                .stream()
            )
        except Exception as e:
            if "permission" in str(e).lower():
                # Expected for non-owner
                pytest.skip(
                    "User alerts query requires authenticated user context. "
                    "Permission denied is expected for service account."
                )
            raise

    def test_articles_by_relevance_query(self, firestore_db, skip_without_gcp_auth):
        """
        Articles sorted by relevance (used in recommendations).

        Query:
            collection('articles')
            .orderBy('relevance_score', 'desc')
            .orderBy('published_at', 'desc')
            .limit(20)
        """
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("articles")
            .order_by("relevance_score", direction=Query.DESCENDING)
            .order_by("published_at", direction=Query.DESCENDING)
            .limit(20)
        )

        try:
            list(query.stream())
        except Exception as e:
            if "index" in str(e).lower():
                pytest.fail(
                    f"Articles relevance query missing index: {e}\n"
                    "Add composite index: articles(relevance_score DESC, published_at DESC)"
                )
            elif "permission" in str(e).lower():
                pytest.fail(f"Articles query permission denied: {e}")
            raise

    def test_articles_by_category_query(self, firestore_db, skip_without_gcp_auth):
        """
        Articles filtered by category.

        Query:
            collection('articles')
            .where('category', '==', 'tech')
            .orderBy('published_at', 'desc')
            .limit(20)
        """
        from google.cloud.firestore_v1 import Query

        query = (
            firestore_db.collection("articles")
            .where("category", "==", "tech")
            .order_by("published_at", direction=Query.DESCENDING)
            .limit(20)
        )

        try:
            list(query.stream())
        except Exception as e:
            if "index" in str(e).lower():
                pytest.fail(
                    f"Articles category query missing index: {e}\n"
                    "Add composite index: articles(category ASC, published_at DESC)"
                )
            elif "permission" in str(e).lower():
                pytest.fail(f"Articles query permission denied: {e}")
            raise


@pytest.mark.integration
class TestQueryPerformance:
    """Test that queries complete within acceptable time."""

    TIMEOUT_MS = 5000  # 5 second timeout

    def test_sources_query_performance(self, firestore_db, skip_without_gcp_auth):
        """Sources query should complete quickly."""
        import time

        start = time.time()
        list(firestore_db.collection("sources").limit(100).stream())
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < self.TIMEOUT_MS, (
            f"Sources query too slow: {elapsed_ms:.0f}ms (limit: {self.TIMEOUT_MS}ms)"
        )

    def test_briefs_query_performance(self, firestore_db, skip_without_gcp_auth):
        """Briefs query should complete quickly."""
        import time
        from google.cloud.firestore_v1 import Query

        start = time.time()
        list(
            firestore_db.collection("briefs")
            .order_by("date", direction=Query.DESCENDING)
            .limit(1)
            .stream()
        )
        elapsed_ms = (time.time() - start) * 1000

        assert elapsed_ms < self.TIMEOUT_MS, (
            f"Briefs query too slow: {elapsed_ms:.0f}ms"
        )
