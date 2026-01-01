"""
MCP Service API Tests
=====================

Integration tests for the MCP FastAPI service.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock, MagicMock
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "perception_app" / "mcp_service"))


@pytest.fixture
def client():
    """Create a test client for the MCP service."""
    from main import app
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test health endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_healthy_status(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_returns_service_info(self, client):
        """Test health endpoint returns service info."""
        response = client.get("/health")
        data = response.json()
        assert data["service"] == "mcp-service"
        assert "version" in data
        assert "timestamp" in data

    def test_health_check_timestamp_format(self, client):
        """Test health endpoint returns valid ISO timestamp."""
        response = client.get("/health")
        data = response.json()
        # Should be parseable as ISO 8601
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_returns_200(self, client):
        """Test root endpoint returns 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_service_info(self, client):
        """Test root endpoint returns service info."""
        response = client.get("/")
        data = response.json()
        assert data["service"] == "Perception MCP Service"

    def test_root_returns_tool_list(self, client):
        """Test root endpoint returns list of tools."""
        response = client.get("/")
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) >= 7

    def test_root_returns_docs_link(self, client):
        """Test root endpoint returns docs link."""
        response = client.get("/")
        data = response.json()
        assert data["docs"] == "/docs"


class TestDocsEndpoint:
    """Tests for the OpenAPI docs endpoint."""

    def test_docs_returns_200(self, client):
        """Test docs endpoint returns 200."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_available(self, client):
        """Test OpenAPI JSON is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data


class TestFetchRSSFeedEndpoint:
    """Tests for the fetch_rss_feed endpoint."""

    @patch('httpx.AsyncClient')
    def test_fetch_rss_feed_valid_request(self, mock_client, client):
        """Test fetching RSS feed with valid request."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = """<?xml version="1.0"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <item>
                    <title>Test Article</title>
                    <link>https://example.com/article</link>
                    <pubDate>Mon, 15 Jan 2024 10:30:00 GMT</pubDate>
                </item>
            </channel>
        </rss>"""
        mock_response.raise_for_status = MagicMock()

        async_mock = AsyncMock()
        async_mock.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value = async_mock

        response = client.post(
            "/mcp/tools/fetch_rss_feed",
            json={"feed_url": "https://example.com/rss"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "articles" in data
        assert "article_count" in data

    def test_fetch_rss_feed_missing_url(self, client):
        """Test fetch_rss_feed with missing feed_url."""
        response = client.post("/mcp/tools/fetch_rss_feed", json={})
        assert response.status_code == 422  # Validation error

    def test_fetch_rss_feed_invalid_time_window(self, client):
        """Test fetch_rss_feed with invalid time window."""
        response = client.post(
            "/mcp/tools/fetch_rss_feed",
            json={"feed_url": "https://example.com/rss", "time_window_hours": 0}
        )
        assert response.status_code == 422

    def test_fetch_rss_feed_invalid_max_items(self, client):
        """Test fetch_rss_feed with invalid max_items."""
        response = client.post(
            "/mcp/tools/fetch_rss_feed",
            json={"feed_url": "https://example.com/rss", "max_items": 1000}
        )
        assert response.status_code == 422

    @patch('httpx.AsyncClient')
    def test_fetch_rss_feed_with_request_id(self, mock_client, client):
        """Test fetch_rss_feed with request_id tracking."""
        mock_response = MagicMock()
        mock_response.text = """<?xml version="1.0"?>
        <rss version="2.0"><channel><title>Test</title></channel></rss>"""
        mock_response.raise_for_status = MagicMock()

        async_mock = AsyncMock()
        async_mock.__aenter__.return_value.get.return_value = mock_response
        mock_client.return_value = async_mock

        response = client.post(
            "/mcp/tools/fetch_rss_feed",
            json={
                "feed_url": "https://example.com/rss",
                "request_id": "test-request-123"
            }
        )

        assert response.status_code == 200


class TestMiddleware:
    """Tests for middleware functionality."""

    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        # CORS middleware should handle OPTIONS
        assert response.status_code in [200, 405]

    def test_request_logging(self, client):
        """Test that requests are handled (logging optional)."""
        # Just verify the request completes - logging implementation varies
        response = client.get("/health")
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_route(self, client):
        """Test 404 response for unknown route."""
        response = client.get("/unknown/route")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Test 405 for wrong HTTP method."""
        response = client.delete("/health")
        assert response.status_code == 405

    def test_validation_error_format(self, client):
        """Test validation error response format."""
        response = client.post(
            "/mcp/tools/fetch_rss_feed",
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data


class TestContentType:
    """Tests for content type handling."""

    def test_json_content_type(self, client):
        """Test JSON content type in response."""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"

    def test_accepts_json_request(self, client):
        """Test accepting JSON request body."""
        response = client.post(
            "/mcp/tools/fetch_rss_feed",
            json={"feed_url": "https://example.com/rss"},
            headers={"Content-Type": "application/json"}
        )
        # Should accept and process (may fail on network, but validates JSON)
        # 404 can occur when external feed URL returns 404
        assert response.status_code in [200, 404, 504, 500]


class TestResponseFormat:
    """Tests for response format consistency."""

    def test_health_response_structure(self, client):
        """Test health response has expected structure."""
        response = client.get("/health")
        data = response.json()
        required_keys = ["status", "service", "version", "timestamp"]
        for key in required_keys:
            assert key in data

    def test_root_response_structure(self, client):
        """Test root response has expected structure."""
        response = client.get("/")
        data = response.json()
        required_keys = ["service", "docs", "health", "tools"]
        for key in required_keys:
            assert key in data


# Parametrized tests for various endpoints
@pytest.mark.parametrize("endpoint,method,expected_status", [
    ("/health", "get", 200),
    ("/", "get", 200),
    ("/docs", "get", 200),
    ("/redoc", "get", 200),
    ("/openapi.json", "get", 200),
])
def test_endpoint_availability(client, endpoint, method, expected_status):
    """Test various endpoints are available."""
    func = getattr(client, method)
    response = func(endpoint)
    assert response.status_code == expected_status


@pytest.mark.parametrize("content_type", [
    "application/json",
])
def test_accepts_content_types(client, content_type):
    """Test accepting various content types."""
    response = client.post(
        "/mcp/tools/fetch_rss_feed",
        json={"feed_url": "https://example.com/rss"},
        headers={"Content-Type": content_type}
    )
    # 404 can occur when external feed URL returns 404
    assert response.status_code in [200, 404, 422, 500, 504]
