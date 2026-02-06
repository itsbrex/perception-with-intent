"""
Perception Test Suite - Main Configuration
==========================================

Central pytest configuration and shared fixtures.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from faker import Faker

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize Faker for test data generation
fake = Faker()
Faker.seed(42)  # Reproducible test data


# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end browser tests")
    config.addinivalue_line("markers", "tui: Terminal UI tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "mcp: MCP service tests")
    config.addinivalue_line("markers", "agent: Agent system tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "security: Security tests")
    config.addinivalue_line("markers", "firebase: Firebase/Firestore tests")
    config.addinivalue_line("markers", "gcp: Google Cloud Platform tests")


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add markers based on test path
        test_path = str(item.fspath)
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
        elif "/e2e/" in test_path:
            item.add_marker(pytest.mark.e2e)
        elif "/tui/" in test_path:
            item.add_marker(pytest.mark.tui)
        elif "/api/" in test_path:
            item.add_marker(pytest.mark.api)
        elif "/mcp/" in test_path:
            item.add_marker(pytest.mark.mcp)
        elif "/agent/" in test_path:
            item.add_marker(pytest.mark.agent)
        elif "/firebase/" in test_path:
            item.add_marker(pytest.mark.firebase)
        elif "/gcp/" in test_path:
            item.add_marker(pytest.mark.gcp)


# =============================================================================
# EVENT LOOP FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# ENVIRONMENT FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root path."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_data_dir(project_root: Path) -> Path:
    """Return the test data directory."""
    data_dir = project_root / "tests" / "fixtures" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test data."""
    return tmp_path


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    """Set up environment variables for testing."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")


# =============================================================================
# MOCK FIXTURES
# =============================================================================


@pytest.fixture
def mock_firestore():
    """Mock Firestore client."""
    with patch("google.cloud.firestore.Client") as mock:
        client = MagicMock()
        mock.return_value = client

        # Mock collection and document operations
        collection = MagicMock()
        client.collection.return_value = collection

        document = MagicMock()
        collection.document.return_value = document
        document.get.return_value = MagicMock(exists=True, to_dict=lambda: {})

        yield client


@pytest.fixture
def mock_vertex_ai():
    """Mock Vertex AI client."""
    with patch("google.cloud.aiplatform") as mock:
        yield mock


@pytest.fixture
def mock_httpx_client():
    """Mock httpx async client."""
    with patch("httpx.AsyncClient") as mock:
        client = AsyncMock()
        mock.return_value.__aenter__.return_value = client
        mock.return_value.__aexit__.return_value = None
        yield client


# =============================================================================
# DATA FIXTURES
# =============================================================================


@pytest.fixture
def sample_article() -> Dict[str, Any]:
    """Generate a sample article."""
    return {
        "id": fake.uuid4(),
        "title": fake.sentence(nb_words=10),
        "summary": fake.paragraph(nb_sentences=3),
        "content": fake.text(max_nb_chars=2000),
        "source": fake.company(),
        "url": fake.url(),
        "published_at": fake.date_time_this_year().isoformat(),
        "relevance_score": fake.pyfloat(min_value=0.0, max_value=1.0),
        "ai_tags": [fake.word() for _ in range(5)],
        "category": fake.random_element(["tech", "business", "sports", "science"]),
    }


@pytest.fixture
def sample_articles(sample_article) -> list:
    """Generate multiple sample articles."""
    return [
        {
            **sample_article,
            "id": fake.uuid4(),
            "title": fake.sentence(nb_words=10),
        }
        for _ in range(10)
    ]


@pytest.fixture
def sample_topic() -> Dict[str, Any]:
    """Generate a sample topic."""
    return {
        "id": fake.uuid4(),
        "keywords": [fake.word() for _ in range(5)],
        "category": fake.random_element(["tech", "business", "sports"]),
        "active": True,
        "created_at": fake.date_time_this_year().isoformat(),
    }


@pytest.fixture
def sample_daily_summary() -> Dict[str, Any]:
    """Generate a sample daily summary."""
    return {
        "id": fake.uuid4(),
        "date": fake.date_this_year().isoformat(),
        "article_count": fake.random_int(min=10, max=100),
        "highlights": [fake.sentence() for _ in range(5)],
        "sections": {
            "tech": {"count": 10, "top_articles": []},
            "business": {"count": 8, "top_articles": []},
        },
    }


@pytest.fixture
def sample_rss_feed() -> Dict[str, Any]:
    """Generate a sample RSS feed configuration."""
    return {
        "id": fake.slug(),
        "name": fake.company(),
        "url": f"https://{fake.domain_name()}/rss",
        "category": fake.random_element(["tech", "news", "business"]),
        "active": True,
        "fetch_interval": 3600,
    }


@pytest.fixture
def sample_rss_response() -> str:
    """Generate a sample RSS XML response."""
    items = "\n".join([
        f"""
        <item>
            <title>{fake.sentence()}</title>
            <link>{fake.url()}</link>
            <description>{fake.paragraph()}</description>
            <pubDate>{fake.date_time_this_month().strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
        </item>
        """
        for _ in range(5)
    ])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>{fake.company()} RSS</title>
        <link>{fake.url()}</link>
        <description>{fake.paragraph()}</description>
        {items}
    </channel>
</rss>"""


# =============================================================================
# API TESTING FIXTURES
# =============================================================================


@pytest.fixture
def api_headers() -> Dict[str, str]:
    """Return common API headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


# =============================================================================
# FAKER FIXTURE
# =============================================================================


@pytest.fixture
def faker_instance() -> Faker:
    """Return a Faker instance for generating test data."""
    return fake


# =============================================================================
# PERFORMANCE FIXTURES
# =============================================================================


@pytest.fixture
def performance_threshold() -> Dict[str, float]:
    """Return performance thresholds for tests."""
    return {
        "api_response_time": 0.5,  # 500ms max
        "db_query_time": 0.1,  # 100ms max
        "rss_fetch_time": 5.0,  # 5s max
        "agent_response_time": 30.0,  # 30s max
    }
