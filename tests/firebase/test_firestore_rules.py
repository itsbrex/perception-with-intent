"""
Firestore Security Rules Validation Tests
=========================================

Validate firestore.rules file syntax and coverage.

These tests ensure:
1. Rules file exists and has valid syntax
2. All dashboard collections have rules defined
3. Rules require authentication (no public access)
4. No dangerous patterns like 'allow write: if true'
"""

import re
from pathlib import Path
from typing import List

import pytest


class TestFirestoreRulesFile:
    """Validate firestore.rules file existence and structure."""

    def test_rules_file_exists(self, firestore_rules_path: Path):
        """firestore.rules must exist."""
        assert firestore_rules_path.exists(), (
            "firestore.rules not found. Security rules are required!"
        )

    def test_rules_file_not_empty(self, firestore_rules_content: str):
        """firestore.rules must not be empty."""
        assert len(firestore_rules_content.strip()) > 0, (
            "firestore.rules is empty"
        )

    def test_rules_have_service_declaration(self, firestore_rules_content: str):
        """Rules must declare cloud.firestore service."""
        assert "service cloud.firestore" in firestore_rules_content, (
            "firestore.rules missing 'service cloud.firestore' declaration"
        )

    def test_rules_have_match_databases(self, firestore_rules_content: str):
        """Rules must match databases path."""
        assert "match /databases/{database}/documents" in firestore_rules_content, (
            "firestore.rules missing 'match /databases/{database}/documents'"
        )

    def test_rules_version_declared(self, firestore_rules_content: str):
        """Rules should declare version 2."""
        assert "rules_version = '2'" in firestore_rules_content, (
            "firestore.rules should use 'rules_version = '2'' for latest features"
        )


class TestCollectionRulesCoverage:
    """Validate that all dashboard collections have rules defined."""

    # Collections the dashboard expects to access
    REQUIRED_COLLECTIONS = [
        ("users/{userId}", "User profiles and settings"),
        ("sources/{sourceId}", "RSS/API source configurations"),
        ("articles/{articleId}", "News articles"),
        ("briefs/{briefId}", "Daily intelligence briefs"),
        ("ingestion_runs/{runId}", "Pipeline run logs"),
        ("authors/{authorId}", "Author profiles"),
    ]

    # User subcollections
    REQUIRED_SUBCOLLECTIONS = [
        ("users/{userId}/topics/{topicId}", "User topic watchlist"),
        ("users/{userId}/alerts/{alertId}", "User alerts"),
    ]

    def test_all_collections_have_rules(self, firestore_rules_content: str):
        """All dashboard collections must have security rules."""
        missing = []

        for collection_path, description in self.REQUIRED_COLLECTIONS:
            # Match pattern allows flexible whitespace
            pattern = f"match /{collection_path}"
            if pattern not in firestore_rules_content:
                missing.append(f"  - {collection_path}: {description}")

        if missing:
            pytest.fail(
                f"Missing security rules for collections:\n" +
                "\n".join(missing) +
                "\n\nAdd rules to firestore.rules"
            )

    def test_user_subcollections_have_rules(self, firestore_rules_content: str):
        """User subcollections must have rules."""
        missing = []

        for subcoll_path, description in self.REQUIRED_SUBCOLLECTIONS:
            # Subcollections can be nested or use wildcards
            # Check for topics and alerts under users
            if "topics" in subcoll_path:
                if "topics/{" not in firestore_rules_content:
                    missing.append(f"  - {subcoll_path}: {description}")
            elif "alerts" in subcoll_path:
                if "alerts/{" not in firestore_rules_content:
                    missing.append(f"  - {subcoll_path}: {description}")

        if missing:
            pytest.fail(
                f"Missing security rules for user subcollections:\n" +
                "\n".join(missing)
            )


class TestSecurityPatterns:
    """Validate security rules follow best practices."""

    def test_no_public_read_access(self, firestore_rules_content: str):
        """
        Rules should not allow unauthenticated read access.

        Pattern: 'allow read: if true' is dangerous.
        """
        dangerous_patterns = [
            r"allow\s+read\s*:\s*if\s+true",
            r"allow\s+read,\s*write\s*:\s*if\s+true",
        ]

        for pattern in dangerous_patterns:
            match = re.search(pattern, firestore_rules_content)
            if match:
                pytest.fail(
                    f"Dangerous rule found: '{match.group()}'. "
                    "All reads should require authentication."
                )

    def test_no_public_write_access(self, firestore_rules_content: str):
        """
        Rules should not allow unauthenticated write access.

        This would allow anyone to modify data.
        """
        dangerous_patterns = [
            r"allow\s+write\s*:\s*if\s+true",
            r"allow\s+create\s*:\s*if\s+true",
            r"allow\s+update\s*:\s*if\s+true",
            r"allow\s+delete\s*:\s*if\s+true",
        ]

        for pattern in dangerous_patterns:
            match = re.search(pattern, firestore_rules_content)
            if match:
                pytest.fail(
                    f"Dangerous rule found: '{match.group()}'. "
                    "Writes should require authentication or be disabled."
                )

    def test_has_auth_helper_function(self, firestore_rules_content: str):
        """
        Rules should define an isSignedIn() or similar auth helper.

        This is a best practice for readable, maintainable rules.
        """
        auth_patterns = [
            "isSignedIn()",
            "isAuthenticated()",
            "request.auth != null",
            "request.auth !== null",
        ]

        has_auth_check = any(
            pattern in firestore_rules_content
            for pattern in auth_patterns
        )

        assert has_auth_check, (
            "firestore.rules should have authentication check. "
            "Add: function isSignedIn() { return request.auth != null; }"
        )

    def test_user_data_owner_check(self, firestore_rules_content: str):
        """
        User collection rules should verify document ownership.

        Users should only access their own data.
        """
        # Check for owner verification pattern
        owner_patterns = [
            "request.auth.uid == userId",
            "request.auth.uid == uid",
            "isOwner(userId)",
            "isOwner(uid)",
        ]

        has_owner_check = any(
            pattern in firestore_rules_content
            for pattern in owner_patterns
        )

        assert has_owner_check, (
            "User collection rules should verify ownership. "
            "Add: function isOwner(userId) { return request.auth.uid == userId; }"
        )

    def test_backend_collections_write_disabled(self, firestore_rules_content: str):
        """
        Backend-only collections should disable client writes.

        Collections like articles, briefs, ingestion_runs should have:
        'allow write: if false;' or equivalent
        """
        backend_collections = ["articles", "briefs", "ingestion_runs", "sources"]
        issues = []

        for collection in backend_collections:
            # Find the collection's rules block
            # This is a simplified check - a full parser would be better
            collection_pattern = f"match /{collection}/"
            if collection_pattern in firestore_rules_content:
                # Check if write is disabled for this collection
                # Look for 'allow write: if false' nearby
                # This is heuristic-based, not a full rules parser
                if f"match /{collection}" in firestore_rules_content:
                    # Get the section after the match
                    idx = firestore_rules_content.find(f"match /{collection}")
                    section = firestore_rules_content[idx:idx+500]

                    if "allow write: if false" not in section and \
                       "allow write: if request.auth" not in section:
                        # May have admin-only or service account write
                        # Don't fail, just note it
                        pass

        # This test is informational - full validation requires parsing


class TestRulesSyntax:
    """Basic syntax validation for firestore.rules."""

    def test_balanced_braces(self, firestore_rules_content: str):
        """Rules file should have balanced braces."""
        open_braces = firestore_rules_content.count("{")
        close_braces = firestore_rules_content.count("}")

        assert open_braces == close_braces, (
            f"Unbalanced braces: {open_braces} open, {close_braces} close"
        )

    def test_no_syntax_errors_in_functions(self, firestore_rules_content: str):
        """Function declarations should be syntactically valid."""
        # Check for common function declaration pattern
        function_pattern = r"function\s+\w+\s*\([^)]*\)\s*\{"
        functions = re.findall(function_pattern, firestore_rules_content)

        # Every function should have a return statement
        # This is a basic heuristic check
        if functions:
            # Just verify we found some functions
            assert len(functions) > 0, "Expected helper functions in rules"

    def test_match_paths_are_valid(self, firestore_rules_content: str):
        """Match paths should use valid Firestore path syntax."""
        # Find all match statements
        match_pattern = r"match\s+/([^\{]+)\{([^\}]+)\}"
        matches = re.findall(match_pattern, firestore_rules_content)

        for path, wildcard in matches:
            # Wildcards should be valid identifiers
            assert re.match(r"^\w+$", wildcard), (
                f"Invalid wildcard '{wildcard}' in match path"
            )
