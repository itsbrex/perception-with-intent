"""
E2E Test Configuration
======================

Playwright fixtures for browser testing.
"""

import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from typing import Generator
import os


# Dashboard URLs for different environments
DASHBOARD_URLS = {
    "local": "http://localhost:5173",
    "staging": "https://perception-with-intent.web.app",
    "production": "https://perception-with-intent.web.app",
}


def get_dashboard_url() -> str:
    """Get the dashboard URL based on environment."""
    env = os.getenv("TEST_ENV", "staging")
    return DASHBOARD_URLS.get(env, DASHBOARD_URLS["staging"])


@pytest.fixture(scope="session")
def browser() -> Generator[Browser, None, None]:
    """Create a browser instance for the test session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ]
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a browser context for each test."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="PerceptionTestBot/1.0",
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture
def dashboard_url() -> str:
    """Return the dashboard URL."""
    return get_dashboard_url()


@pytest.fixture
def mobile_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a mobile browser context."""
    context = browser.new_context(
        viewport={"width": 375, "height": 812},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        is_mobile=True,
        has_touch=True,
    )
    yield context
    context.close()


@pytest.fixture
def tablet_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a tablet browser context."""
    context = browser.new_context(
        viewport={"width": 1024, "height": 768},
        user_agent="Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15",
        is_mobile=True,
        has_touch=True,
    )
    yield context
    context.close()


@pytest.fixture
def slow_network_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a context simulating slow network."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
    )
    # Note: Playwright doesn't have direct network throttling
    # This is a placeholder for future implementation
    yield context
    context.close()


@pytest.fixture
def console_error_collector(page: Page) -> Generator[list, None, None]:
    """
    Collect all console errors during test.

    Usage:
        def test_something(page, console_error_collector):
            page.goto(...)
            assert len(console_error_collector) == 0
    """
    errors: list = []

    def handle_console(msg):
        if msg.type == "error":
            errors.append(msg.text)

    page.on("console", handle_console)
    yield errors


@pytest.fixture
def authenticated_page(page: Page, dashboard_url: str) -> Generator[Page, None, None]:
    """
    Page with test user authenticated.

    Requires TEST_USER_EMAIL and TEST_USER_PASSWORD environment variables.
    Skips test if credentials not available.

    Usage:
        def test_dashboard(authenticated_page, dashboard_url):
            # authenticated_page is already logged in
            authenticated_page.goto(f"{dashboard_url}/dashboard")
    """
    email = os.getenv("TEST_USER_EMAIL")
    password = os.getenv("TEST_USER_PASSWORD")

    if not email or not password:
        pytest.skip(
            "TEST_USER_EMAIL and TEST_USER_PASSWORD required for authenticated tests"
        )

    # Navigate to login
    page.goto(f"{dashboard_url}/login", wait_until="networkidle")

    # Fill login form
    email_input = page.locator("input[type='email']")
    if email_input.count() == 0:
        email_input = page.locator("input[name='email']")

    if email_input.count() == 0:
        pytest.skip("Could not find email input on login page")

    email_input.fill(email)

    password_input = page.locator("input[type='password']")
    password_input.fill(password)

    # Submit form
    submit_button = page.locator("button[type='submit']")
    if submit_button.count() == 0:
        submit_button = page.locator("button:has-text('Sign')")
    if submit_button.count() == 0:
        submit_button = page.locator("button:has-text('Log')")

    submit_button.click()

    # Wait for navigation to dashboard
    try:
        page.wait_for_url("**/dashboard**", timeout=10000)
    except Exception:
        # May have different redirect behavior
        page.wait_for_timeout(3000)

    yield page
