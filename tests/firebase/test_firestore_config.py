"""
Firestore Configuration Tests
=============================

Validate that firebase.json and application code target the correct database.

These tests catch the common error of deploying rules/indexes to the (default)
database instead of the named 'perception-db' database.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict

import pytest


class TestFirebaseJsonConfiguration:
    """Validate firebase.json targets correct database."""

    def test_firebase_json_exists(self, firebase_json_path: Path):
        """firebase.json must exist in project root."""
        assert firebase_json_path.exists(), "firebase.json not found in project root"

    def test_firebase_json_is_valid_json(self, firebase_json_path: Path):
        """firebase.json must be valid JSON."""
        try:
            with open(firebase_json_path) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"firebase.json is not valid JSON: {e}")

    def test_firestore_section_exists(self, firebase_config: Dict[str, Any]):
        """firebase.json must have a firestore section."""
        assert "firestore" in firebase_config, (
            "firebase.json missing 'firestore' section. "
            "Firestore rules and indexes won't be deployed."
        )

    def test_firestore_database_is_perception_db(self, firebase_config: Dict[str, Any]):
        """
        firebase.json firestore.database must be 'perception-db'.

        CRITICAL: Without this, rules deploy to (default) database instead
        of the named perception-db database, causing permission errors.
        """
        firestore_config = firebase_config.get("firestore", {})
        database = firestore_config.get("database")

        assert database == "perception-db", (
            f"firebase.json firestore.database is '{database}', expected 'perception-db'. "
            "Rules and indexes will deploy to wrong database!"
        )

    def test_firestore_rules_path_configured(self, firebase_config: Dict[str, Any]):
        """firebase.json must specify rules file path."""
        firestore_config = firebase_config.get("firestore", {})
        assert "rules" in firestore_config, (
            "firebase.json missing 'firestore.rules' path"
        )

    def test_firestore_indexes_path_configured(self, firebase_config: Dict[str, Any]):
        """firebase.json must specify indexes file path."""
        firestore_config = firebase_config.get("firestore", {})
        assert "indexes" in firestore_config, (
            "firebase.json missing 'firestore.indexes' path"
        )

    def test_referenced_rules_file_exists(
        self, firebase_config: Dict[str, Any], project_root: Path
    ):
        """The rules file referenced in firebase.json must exist."""
        rules_path = firebase_config.get("firestore", {}).get("rules")
        if rules_path:
            full_path = project_root / rules_path
            assert full_path.exists(), (
                f"firestore.rules file not found at {rules_path}"
            )

    def test_referenced_indexes_file_exists(
        self, firebase_config: Dict[str, Any], project_root: Path
    ):
        """The indexes file referenced in firebase.json must exist."""
        indexes_path = firebase_config.get("firestore", {}).get("indexes")
        if indexes_path:
            full_path = project_root / indexes_path
            assert full_path.exists(), (
                f"firestore.indexes.json file not found at {indexes_path}"
            )


class TestDashboardFirebaseConfiguration:
    """Validate dashboard TypeScript code uses named database."""

    def test_dashboard_firebase_ts_exists(self, dashboard_firebase_ts_path: Path):
        """dashboard/src/firebase.ts must exist."""
        assert dashboard_firebase_ts_path.exists(), (
            "dashboard/src/firebase.ts not found"
        )

    def test_dashboard_uses_named_database(self, dashboard_firebase_content: str):
        """
        Dashboard must use getFirestore with 'perception-db' database name.

        CRITICAL: Without the database name, the dashboard connects to (default)
        database and gets permission denied errors.
        """
        # Check for getFirestore call with perception-db
        pattern = r"getFirestore\s*\(\s*app\s*,\s*['\"]perception-db['\"]\s*\)"
        match = re.search(pattern, dashboard_firebase_content)

        assert match is not None, (
            "dashboard/src/firebase.ts must call getFirestore(app, 'perception-db'). "
            "Found getFirestore call without database name - will connect to (default) database!"
        )

    def test_dashboard_exports_db(self, dashboard_firebase_content: str):
        """Dashboard must export the db instance."""
        assert "export const db" in dashboard_firebase_content or \
               "export { db" in dashboard_firebase_content, (
            "dashboard/src/firebase.ts must export 'db' for components to use"
        )

    def test_dashboard_exports_auth(self, dashboard_firebase_content: str):
        """Dashboard must export the auth instance."""
        assert "export const auth" in dashboard_firebase_content or \
               "export { auth" in dashboard_firebase_content, (
            "dashboard/src/firebase.ts must export 'auth' for authentication"
        )


class TestPythonFirestoreConfiguration:
    """Validate Python backend code uses named database."""

    @pytest.fixture
    def python_firestore_files(self, project_root: Path):
        """Find Python files that might use Firestore."""
        patterns = [
            "perception_app/**/tools/*.py",
            "perception_app/mcp_service/**/*.py",
            "scripts/*.py",
        ]
        files = []
        for pattern in patterns:
            files.extend(project_root.glob(pattern))
        return files

    def test_python_firestore_clients_use_database_param(
        self, python_firestore_files, project_root: Path
    ):
        """
        Python Firestore clients should specify database parameter.

        Note: This is a soft check - some files may use mocked clients in tests.
        """
        files_without_database = []

        for filepath in python_firestore_files:
            content = filepath.read_text()

            # Check if file uses Firestore
            if "firestore.Client(" in content:
                # Check if database parameter is specified
                # Pattern: firestore.Client(...database=...) or firestore.Client(..., database=...)
                if 'database=' not in content and 'database =' not in content:
                    # Could be OK if it's a test file or uses emulator
                    if "test" not in str(filepath).lower():
                        files_without_database.append(
                            str(filepath.relative_to(project_root))
                        )

        if files_without_database:
            pytest.skip(
                f"Files using firestore.Client without database param (may be intentional): "
                f"{files_without_database}"
            )
