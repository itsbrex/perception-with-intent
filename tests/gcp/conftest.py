"""
GCP Test Fixtures
=================

Shared fixtures for Google Cloud Platform integration tests.
"""

import os

import pytest


@pytest.fixture(scope="session")
def gcp_project():
    """GCP project ID."""
    return os.getenv("GCP_PROJECT", "perception-with-intent")


@pytest.fixture(scope="session")
def gcp_region():
    """Default GCP region."""
    return os.getenv("GCP_REGION", "us-central1")


@pytest.fixture(scope="session")
def mcp_service_url():
    """MCP Cloud Run service URL."""
    return os.getenv(
        "MCP_SERVICE_URL",
        "https://perception-mcp-348724539390.us-central1.run.app"
    )


@pytest.fixture(scope="session")
def gcp_credentials():
    """
    Ensure GCP credentials are available.

    Returns credentials object or skips test.
    """
    try:
        from google.auth import default
        credentials, project = default()
        return credentials
    except Exception as e:
        pytest.skip(f"GCP authentication not available: {e}")


@pytest.fixture
def skip_without_gcp_auth(gcp_credentials):
    """Skip test if not authenticated to GCP."""
    # gcp_credentials fixture will skip if auth not available
    pass


@pytest.fixture(scope="session")
def logging_client(gcp_project, gcp_credentials):
    """Google Cloud Logging client."""
    try:
        from google.cloud import logging_v2
        return logging_v2.Client(project=gcp_project)
    except ImportError:
        pytest.skip("google-cloud-logging not installed")
    except Exception as e:
        pytest.skip(f"Could not create logging client: {e}")


@pytest.fixture(scope="session")
def firestore_client(gcp_project, gcp_credentials):
    """Firestore client for perception-db."""
    try:
        from google.cloud import firestore
        return firestore.Client(
            project=gcp_project,
            database="perception-db"
        )
    except ImportError:
        pytest.skip("google-cloud-firestore not installed")
    except Exception as e:
        pytest.skip(f"Could not create Firestore client: {e}")
