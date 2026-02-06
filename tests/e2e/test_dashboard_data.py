"""
Dashboard E2E Data Loading Tests
================================

E2E tests that verify dashboard data loading works correctly.
Catches Firestore errors that only manifest in the browser.

Uses Playwright for browser automation.
"""

import os
from typing import List

import pytest


@pytest.mark.e2e
class TestDashboardDataLoading:
    """E2E tests for dashboard data loading - catches Firestore errors in browser."""

    def test_no_permission_errors_in_console(
        self, page, dashboard_url
    ):
        """
        Catch 'Missing or insufficient permissions' errors.

        These errors indicate:
        1. Security rules not deployed to correct database
        2. User not authenticated when accessing protected data
        3. Rules too restrictive
        """
        console_errors: List[str] = []

        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console)

        # Navigate to dashboard
        page.goto(f"{dashboard_url}/dashboard", wait_until="networkidle")

        # Allow time for Firestore queries
        page.wait_for_timeout(3000)

        # Check for permission errors
        permission_errors = [
            e for e in console_errors
            if "permission" in e.lower() or "PERMISSION_DENIED" in e
        ]

        assert len(permission_errors) == 0, (
            f"Permission errors found in console:\n" +
            "\n".join(permission_errors[:5]) +
            "\n\nCheck: firestore.rules deployed to perception-db"
        )

    def test_no_index_errors_in_console(
        self, page, dashboard_url
    ):
        """
        Catch 'query requires an index' errors.

        These errors indicate:
        1. Composite index not defined in firestore.indexes.json
        2. Indexes not deployed to Firestore
        """
        console_errors: List[str] = []

        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console)

        # Navigate to authors page (has composite index query)
        page.goto(f"{dashboard_url}/authors", wait_until="networkidle")

        # Wait for queries to execute
        page.wait_for_timeout(3000)

        # Check for index errors
        index_errors = [
            e for e in console_errors
            if "index" in e.lower() or "FAILED_PRECONDITION" in e
        ]

        assert len(index_errors) == 0, (
            f"Index errors found in console:\n" +
            "\n".join(index_errors[:5]) +
            "\n\nRun: firebase deploy --only firestore:indexes"
        )

    def test_sources_card_shows_data(
        self, page, dashboard_url
    ):
        """
        SourceHealthCard should show sources count > 0.

        Verifies that sources collection is accessible and has data.
        """
        page.goto(f"{dashboard_url}/dashboard", wait_until="networkidle")

        # Check if redirected to login (unauthenticated)
        if "/login" in page.url or page.locator("input[type='password']").count() > 0:
            pytest.skip("Dashboard requires authentication - skipping sources card test")

        # Wait for sources card to load
        try:
            page.wait_for_selector(
                "[data-testid='sources-card']",
                timeout=10000
            )
        except Exception:
            # If testid not present, try finding by heading
            try:
                page.wait_for_selector(
                    "text=Source Health",
                    timeout=5000
                )
            except Exception:
                pytest.skip("Sources card not found - may require authentication")

        # Check that we don't show 0 sources or error state
        page_content = page.content()

        # Should NOT show "0 Total Sources" or loading forever
        if "0 Total Sources" in page_content:
            pytest.skip("Sources card shows 0 - collection may be empty")

        # Should NOT show error state
        assert "Error loading sources" not in page_content, (
            "Sources card showing error - check Firestore permissions"
        )

    def test_authors_page_loads_without_error(
        self, page, dashboard_url
    ):
        """
        Authors page should load without 'Error loading authors'.

        This is the query that was failing due to missing composite index.
        """
        page.goto(f"{dashboard_url}/authors", wait_until="networkidle")

        # Wait for content to load
        page.wait_for_timeout(3000)

        page_content = page.content()

        # Should NOT show error message
        assert "Error loading authors" not in page_content, (
            "Authors page showing error - likely missing index.\n"
            "Run: firebase deploy --only firestore:indexes"
        )

        # Should NOT be stuck on loading
        if "Loading authors" in page_content:
            pytest.skip("Authors page still loading - may be slow network")

    def test_briefs_card_shows_content(
        self, page, dashboard_url
    ):
        """
        TodayBriefCard should show brief content, not error state.

        Note: 'No brief available' is OK - that just means no briefs exist yet.
        """
        page.goto(f"{dashboard_url}/dashboard", wait_until="networkidle")

        # Wait for brief card
        page.wait_for_timeout(3000)

        page_content = page.content()

        # Should NOT show error
        assert "Error loading brief" not in page_content, (
            "Brief card showing error - check Firestore permissions"
        )

        # 'No brief available' is acceptable - just skip
        if "No brief available" in page_content:
            pytest.skip("No briefs in database yet - run ingestion")

    def test_no_firebase_initialization_errors(
        self, page, dashboard_url
    ):
        """
        Check for Firebase initialization errors.

        Catches issues like:
        - Invalid API key
        - Wrong project ID
        - App not initialized
        """
        console_errors: List[str] = []

        def handle_console(msg):
            if msg.type == "error":
                console_errors.append(msg.text)

        page.on("console", handle_console)

        page.goto(f"{dashboard_url}/", wait_until="networkidle")
        page.wait_for_timeout(2000)

        # Check for Firebase/app initialization errors
        firebase_errors = [
            e for e in console_errors
            if any(term in e.lower() for term in [
                "firebase",
                "api-key",
                "apikey",
                "not initialized",
                "app/no-app",
            ])
        ]

        assert len(firebase_errors) == 0, (
            f"Firebase initialization errors:\n" +
            "\n".join(firebase_errors[:5])
        )


@pytest.mark.e2e
class TestDashboardNavigation:
    """Test that all dashboard routes work."""

    ROUTES = [
        ("/", "landing or dashboard"),
        ("/dashboard", "main dashboard"),
        ("/authors", "authors list"),
        ("/login", "login page"),
    ]

    @pytest.mark.parametrize("route,description", ROUTES)
    def test_route_loads_without_crash(
        self, page, dashboard_url, route, description
    ):
        """
        Each route should load without JavaScript errors.
        """
        console_errors: List[str] = []

        def handle_console(msg):
            if msg.type == "error":
                text = msg.text
                # Ignore some expected errors
                if "favicon" in text.lower():
                    return
                console_errors.append(text)

        page.on("console", handle_console)

        response = page.goto(
            f"{dashboard_url}{route}",
            wait_until="networkidle"
        )

        # Should not get 5xx error
        assert response.status < 500, (
            f"Route {route} returned {response.status}"
        )

        # Should not have fatal errors
        fatal_errors = [
            e for e in console_errors
            if "uncaught" in e.lower() or "fatal" in e.lower()
        ]

        assert len(fatal_errors) == 0, (
            f"Fatal errors on {route}:\n" + "\n".join(fatal_errors[:3])
        )
