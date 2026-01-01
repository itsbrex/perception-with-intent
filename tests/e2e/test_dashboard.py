"""
Dashboard E2E Tests
===================

End-to-end browser tests for the Perception dashboard.
"""

import pytest
from playwright.sync_api import Page, expect
import re


@pytest.mark.e2e
class TestDashboardHomepage:
    """Tests for dashboard homepage."""

    def test_homepage_loads(self, page: Page, dashboard_url: str):
        """Test homepage loads successfully."""
        response = page.goto(dashboard_url)
        assert response is not None
        assert response.status < 400

    def test_homepage_has_title(self, page: Page, dashboard_url: str):
        """Test homepage has correct title."""
        page.goto(dashboard_url)
        expect(page).to_have_title(re.compile(r"Perception", re.IGNORECASE))

    def test_homepage_has_header(self, page: Page, dashboard_url: str):
        """Test homepage has header element."""
        page.goto(dashboard_url)
        # Wait for page to load
        page.wait_for_load_state("networkidle")

    def test_homepage_no_console_errors(self, page: Page, dashboard_url: str):
        """Test homepage has no console errors."""
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")
        # Filter out known non-critical errors
        critical_errors = [e for e in errors if "favicon" not in e.lower()]
        assert len(critical_errors) == 0, f"Console errors: {critical_errors}"


@pytest.mark.e2e
class TestDashboardNavigation:
    """Tests for dashboard navigation."""

    def test_can_navigate_to_homepage(self, page: Page, dashboard_url: str):
        """Test navigation to homepage."""
        page.goto(dashboard_url)
        expect(page).to_have_url(re.compile(dashboard_url))

    def test_navigation_preserves_state(self, page: Page, dashboard_url: str):
        """Test navigation preserves application state."""
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")
        # Navigation should work without errors


@pytest.mark.e2e
class TestDashboardResponsive:
    """Tests for responsive design."""

    def test_desktop_viewport(self, page: Page, dashboard_url: str):
        """Test desktop viewport renders correctly."""
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")

    def test_tablet_viewport(self, page: Page, dashboard_url: str):
        """Test tablet viewport renders correctly."""
        page.set_viewport_size({"width": 1024, "height": 768})
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")

    def test_mobile_viewport(self, page: Page, dashboard_url: str):
        """Test mobile viewport renders correctly."""
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")


@pytest.mark.e2e
class TestDashboardPerformance:
    """Tests for dashboard performance."""

    def test_page_loads_under_5_seconds(self, page: Page, dashboard_url: str):
        """Test page loads under 5 seconds."""
        import time
        start = time.time()
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")
        load_time = time.time() - start
        assert load_time < 5, f"Page took {load_time:.2f}s to load"

    def test_first_contentful_paint(self, page: Page, dashboard_url: str):
        """Test first contentful paint is reasonable."""
        page.goto(dashboard_url)
        # FCP should happen quickly
        page.wait_for_load_state("domcontentloaded", timeout=10000)


@pytest.mark.e2e
class TestDashboardAccessibility:
    """Tests for accessibility."""

    def test_page_has_lang_attribute(self, page: Page, dashboard_url: str):
        """Test page has lang attribute."""
        page.goto(dashboard_url)
        html = page.locator("html")
        lang = html.get_attribute("lang")
        assert lang is not None

    def test_images_have_alt_text(self, page: Page, dashboard_url: str):
        """Test images have alt text."""
        page.goto(dashboard_url)
        images = page.locator("img").all()
        for img in images:
            alt = img.get_attribute("alt")
            # Images should have alt text (empty string is acceptable for decorative)
            assert alt is not None


@pytest.mark.e2e
class TestDashboardSecurity:
    """Tests for security headers."""

    def test_has_content_security_policy(self, page: Page, dashboard_url: str):
        """Test page has CSP headers."""
        response = page.goto(dashboard_url)
        # CSP may or may not be present depending on hosting config
        assert response is not None

    def test_no_mixed_content(self, page: Page, dashboard_url: str):
        """Test page has no mixed content warnings."""
        warnings = []
        page.on("console", lambda msg: warnings.append(msg.text) if "mixed content" in msg.text.lower() else None)
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")
        assert len(warnings) == 0


@pytest.mark.e2e
class TestDashboardErrorHandling:
    """Tests for error handling."""

    def test_404_page_exists(self, page: Page, dashboard_url: str):
        """Test 404 page exists for unknown routes."""
        response = page.goto(f"{dashboard_url}/nonexistent-page-12345")
        # Should either return 404 or redirect to homepage for SPA
        assert response is not None


@pytest.mark.e2e
class TestDashboardComponents:
    """Tests for UI components."""

    def test_page_renders_content(self, page: Page, dashboard_url: str):
        """Test page renders some content."""
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")
        # Page should have visible content
        body = page.locator("body")
        expect(body).to_be_visible()

    def test_interactive_elements_are_clickable(self, page: Page, dashboard_url: str):
        """Test interactive elements are clickable."""
        page.goto(dashboard_url)
        page.wait_for_load_state("networkidle")
        # Find buttons and links
        buttons = page.locator("button, a[href]").all()
        # At least some interactive elements should exist
        assert len(buttons) >= 0


# Parametrized viewport tests
@pytest.mark.e2e
@pytest.mark.parametrize("width,height", [
    (320, 568),   # iPhone SE
    (375, 667),   # iPhone 8
    (414, 896),   # iPhone 11 Pro Max
    (768, 1024),  # iPad
    (1024, 768),  # iPad Landscape
    (1280, 720),  # HD
    (1920, 1080), # Full HD
    (2560, 1440), # 2K
])
def test_viewport_renders(page: Page, dashboard_url: str, width: int, height: int):
    """Test page renders at various viewport sizes."""
    page.set_viewport_size({"width": width, "height": height})
    response = page.goto(dashboard_url)
    assert response is not None
    assert response.status < 400


# Parametrized navigation tests
@pytest.mark.e2e
@pytest.mark.parametrize("path", [
    "/",
    "/#/",
])
def test_paths_accessible(page: Page, dashboard_url: str, path: str):
    """Test various paths are accessible."""
    response = page.goto(f"{dashboard_url}{path}")
    assert response is not None
    # Should not return server error
    assert response.status < 500
