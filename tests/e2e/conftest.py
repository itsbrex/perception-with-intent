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
