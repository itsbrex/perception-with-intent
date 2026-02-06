"""
Firebase Test Fixtures
======================

Shared fixtures for Firebase/Firestore tests.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest


# =============================================================================
# PATH FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Return the project root path."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="session")
def firebase_json_path(project_root: Path) -> Path:
    """Path to firebase.json."""
    return project_root / "firebase.json"


@pytest.fixture(scope="session")
def firestore_rules_path(project_root: Path) -> Path:
    """Path to firestore.rules."""
    return project_root / "firestore.rules"


@pytest.fixture(scope="session")
def firestore_indexes_path(project_root: Path) -> Path:
    """Path to firestore.indexes.json."""
    return project_root / "firestore.indexes.json"


@pytest.fixture(scope="session")
def dashboard_firebase_ts_path(project_root: Path) -> Path:
    """Path to dashboard/src/firebase.ts."""
    return project_root / "dashboard" / "src" / "firebase.ts"


# =============================================================================
# CONFIG FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def firebase_config(firebase_json_path: Path) -> Dict[str, Any]:
    """Load firebase.json configuration."""
    with open(firebase_json_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def firestore_indexes(firestore_indexes_path: Path) -> Dict[str, Any]:
    """Load firestore.indexes.json configuration."""
    with open(firestore_indexes_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def firestore_rules_content(firestore_rules_path: Path) -> str:
    """Load firestore.rules content."""
    return firestore_rules_path.read_text()


@pytest.fixture(scope="session")
def dashboard_firebase_content(dashboard_firebase_ts_path: Path) -> str:
    """Load dashboard/src/firebase.ts content."""
    return dashboard_firebase_ts_path.read_text()


# =============================================================================
# FIRESTORE CLIENT FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def gcp_project() -> str:
    """GCP project ID."""
    return os.getenv("GCP_PROJECT", "perception-with-intent")


@pytest.fixture(scope="session")
def firestore_database() -> str:
    """Firestore database name."""
    return "perception-db"


@pytest.fixture(scope="session")
def firestore_db(gcp_project: str, firestore_database: str):
    """
    Real Firestore client for perception-db.

    Only used for integration tests that require GCP auth.
    """
    try:
        from google.cloud import firestore
        return firestore.Client(
            project=gcp_project,
            database=firestore_database
        )
    except Exception as e:
        pytest.skip(f"Firestore client not available: {e}")


@pytest.fixture
def test_user_id() -> str:
    """A test user ID for subcollection queries."""
    return "test-user-firebase-tests"


# =============================================================================
# SKIP CONDITIONS
# =============================================================================


@pytest.fixture
def skip_without_gcp_auth():
    """Skip test if not authenticated to GCP."""
    try:
        from google.auth import default
        default()
    except Exception:
        pytest.skip("GCP authentication not available")
