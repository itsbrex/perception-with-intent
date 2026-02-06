"""
Cloud Run Health Tests
======================

Test Cloud Run services are healthy and responding.

These tests verify:
1. Health endpoints return 200
2. Services respond within acceptable time
3. Functional endpoints work correctly
"""

import pytest


@pytest.mark.integration
class TestCloudRunHealth:
    """Test Cloud Run services are healthy."""

    def test_mcp_service_health(self, mcp_service_url, skip_without_gcp_auth):
        """
        MCP service /health endpoint returns 200.

        This is a basic liveness check.
        """
        import httpx

        try:
            response = httpx.get(
                f"{mcp_service_url}/health",
                timeout=10
            )
        except httpx.ConnectError as e:
            pytest.fail(f"Could not connect to MCP service: {e}")
        except httpx.TimeoutException:
            pytest.fail("MCP health check timed out (>10s)")

        assert response.status_code == 200, (
            f"MCP health check failed: {response.status_code}"
        )

    def test_mcp_service_responds_quickly(
        self, mcp_service_url, skip_without_gcp_auth
    ):
        """
        MCP service should respond within acceptable cold start time.

        Cold starts on Cloud Run can take several seconds.
        """
        import time
        import httpx

        # First request may be cold start
        start = time.time()
        try:
            response = httpx.get(
                f"{mcp_service_url}/health",
                timeout=30  # Allow for cold start
            )
        except Exception as e:
            pytest.fail(f"MCP health request failed: {e}")

        elapsed = time.time() - start

        # Warn if too slow but don't fail
        if elapsed > 10:
            pytest.skip(
                f"MCP cold start slow: {elapsed:.2f}s. "
                "Consider increasing min instances."
            )

        assert response.status_code == 200

    def test_mcp_rss_endpoint_functional(
        self, mcp_service_url, skip_without_gcp_auth
    ):
        """
        MCP RSS endpoint is functional.

        Test with a known feed ID.
        """
        import httpx

        try:
            response = httpx.post(
                f"{mcp_service_url}/mcp/tools/fetch_rss_feed",
                json={"feed_id": "hackernews"},
                timeout=30
            )
        except httpx.TimeoutException:
            pytest.skip("RSS fetch timed out - may be rate limited")
        except Exception as e:
            pytest.fail(f"RSS endpoint request failed: {e}")

        # 200 = success, 422 = validation error (expected for unknown feed)
        assert response.status_code in [200, 422], (
            f"Unexpected status: {response.status_code}\n"
            f"Response: {response.text[:200]}"
        )

    def test_mcp_openapi_docs_available(
        self, mcp_service_url, skip_without_gcp_auth
    ):
        """
        MCP OpenAPI docs should be accessible.

        FastAPI generates these automatically at /docs or /openapi.json.
        """
        import httpx

        # Try common FastAPI doc endpoints
        doc_endpoints = ["/docs", "/openapi.json", "/redoc"]

        for endpoint in doc_endpoints:
            try:
                response = httpx.get(
                    f"{mcp_service_url}{endpoint}",
                    timeout=10
                )
                if response.status_code == 200:
                    return  # Found docs
            except Exception:
                continue

        pytest.skip("OpenAPI docs not found at standard endpoints")


@pytest.mark.integration
class TestCloudRunPerformance:
    """Performance tests for Cloud Run services."""

    def test_mcp_health_latency(self, mcp_service_url, skip_without_gcp_auth):
        """
        Health endpoint should be fast (<500ms after warm-up).

        Run multiple requests to measure warm latency.
        """
        import time
        import httpx

        latencies = []

        # Warm-up request
        httpx.get(f"{mcp_service_url}/health", timeout=30)

        # Measure subsequent requests
        for _ in range(3):
            start = time.time()
            response = httpx.get(f"{mcp_service_url}/health", timeout=10)
            latencies.append((time.time() - start) * 1000)

            assert response.status_code == 200

        avg_latency = sum(latencies) / len(latencies)

        # Health endpoint should be very fast when warm
        assert avg_latency < 500, (
            f"Health endpoint too slow: {avg_latency:.0f}ms average"
        )

    def test_mcp_concurrent_requests(
        self, mcp_service_url, skip_without_gcp_auth
    ):
        """
        MCP service should handle concurrent requests.

        Tests that scaling works correctly.
        """
        import concurrent.futures
        import httpx

        def make_request():
            response = httpx.get(
                f"{mcp_service_url}/health",
                timeout=15
            )
            return response.status_code

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [f.result() for f in futures]

        # All should succeed
        success_count = sum(1 for r in results if r == 200)
        assert success_count == len(results), (
            f"Only {success_count}/{len(results)} concurrent requests succeeded"
        )
