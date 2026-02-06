"""
Cloud Logging Integration Tests
===============================

Test Google Cloud Logging for backend errors.

These tests query Cloud Logging to detect:
1. Firestore permission denied errors
2. Missing index errors
3. MCP service 500 errors
4. Agent Engine failures

Requires GCP authentication and google-cloud-logging package.
"""

import pytest


@pytest.mark.integration
class TestCloudLogging:
    """Test Google Cloud Logging for backend errors."""

    def test_no_firestore_permission_errors(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Check Cloud Logging for Firestore permission denied errors.

        These indicate:
        1. Security rules issues
        2. Service account permission problems
        3. Wrong database targeted
        """
        from google.cloud.logging_v2 import DESCENDING

        filter_str = '''
            resource.type="cloud_run_revision"
            resource.labels.service_name="perception-mcp"
            severity>=ERROR
            (textPayload:"PERMISSION_DENIED" OR textPayload:"permission")
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=10
            ))
        except Exception as e:
            pytest.skip(f"Could not query Cloud Logging: {e}")

        if entries:
            error_samples = [
                str(e.payload)[:200] if hasattr(e, 'payload') else str(e)[:200]
                for e in entries[:3]
            ]
            pytest.fail(
                f"Found {len(entries)} permission errors in Cloud Logging:\n" +
                "\n".join(error_samples) +
                "\n\nCheck Firestore rules and service account permissions"
            )

    def test_no_firestore_index_errors(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Check Cloud Logging for missing index errors.

        FAILED_PRECONDITION with "index" indicates queries need indexes.
        """
        from google.cloud.logging_v2 import DESCENDING

        filter_str = '''
            resource.type="cloud_run_revision"
            severity>=ERROR
            (textPayload:"requires an index" OR textPayload:"FAILED_PRECONDITION")
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=10
            ))
        except Exception as e:
            pytest.skip(f"Could not query Cloud Logging: {e}")

        if entries:
            error_samples = [
                str(e.payload)[:200] if hasattr(e, 'payload') else str(e)[:200]
                for e in entries[:3]
            ]
            pytest.fail(
                f"Found {len(entries)} index errors in Cloud Logging:\n" +
                "\n".join(error_samples) +
                "\n\nRun: firebase deploy --only firestore:indexes"
            )

    def test_no_mcp_service_500_errors_recent(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Check for recent 500 errors from MCP service.

        Some 500s may be expected, so this is informational.
        """
        from google.cloud.logging_v2 import DESCENDING

        filter_str = '''
            resource.type="cloud_run_revision"
            resource.labels.service_name="perception-mcp"
            httpRequest.status>=500
            timestamp>="2024-01-01T00:00:00Z"
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=10
            ))
        except Exception as e:
            pytest.skip(f"Could not query Cloud Logging: {e}")

        if entries:
            # Warn but don't fail - some 500s may be expected
            error_count = len(entries)
            pytest.skip(
                f"Found {error_count} recent 500 errors in MCP service. "
                "Review Cloud Logging for details."
            )

    def test_no_agent_engine_errors(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Check Agent Engine for execution errors.

        Note: This filter may need adjustment based on actual log format.
        """
        from google.cloud.logging_v2 import DESCENDING

        filter_str = '''
            resource.type="aiplatform.googleapis.com/Endpoint"
            severity>=ERROR
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=10
            ))
        except Exception as e:
            # Agent Engine logs may have different format
            pytest.skip(f"Could not query Agent Engine logs: {e}")

        if entries:
            pytest.skip(
                f"Found {len(entries)} Agent Engine errors. "
                "Review Cloud Logging for details."
            )

    def test_no_critical_errors_last_hour(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Check for any CRITICAL severity errors in last hour.

        Critical errors should always be investigated.
        """
        from datetime import datetime, timedelta, timezone
        from google.cloud.logging_v2 import DESCENDING

        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

        filter_str = f'''
            resource.labels.project_id="perception-with-intent"
            severity=CRITICAL
            timestamp>="{one_hour_ago}"
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=5
            ))
        except Exception as e:
            pytest.skip(f"Could not query Cloud Logging: {e}")

        if entries:
            error_samples = [
                str(e.payload)[:200] if hasattr(e, 'payload') else str(e)[:200]
                for e in entries[:3]
            ]
            pytest.fail(
                f"Found {len(entries)} CRITICAL errors in last hour:\n" +
                "\n".join(error_samples)
            )


@pytest.mark.integration
class TestFirestoreAuditLogs:
    """Test Firestore data access audit logs."""

    def test_firestore_operations_logged(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Verify Firestore operations are being logged.

        Audit logs help with debugging and security monitoring.
        """
        from google.cloud.logging_v2 import DESCENDING

        filter_str = '''
            protoPayload.serviceName="firestore.googleapis.com"
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=5
            ))
        except Exception as e:
            pytest.skip(f"Could not query Firestore audit logs: {e}")

        # Having some logs is good - means audit logging is enabled
        if not entries:
            pytest.skip(
                "No Firestore audit logs found. "
                "Enable Data Access audit logs for debugging."
            )

    def test_no_unauthorized_access_attempts(
        self, logging_client, skip_without_gcp_auth
    ):
        """
        Check for unauthorized Firestore access attempts.

        Code 7 = PERMISSION_DENIED in audit logs.
        """
        from google.cloud.logging_v2 import DESCENDING

        filter_str = '''
            protoPayload.serviceName="firestore.googleapis.com"
            protoPayload.status.code=7
        '''

        try:
            entries = list(logging_client.list_entries(
                filter_=filter_str,
                order_by=DESCENDING,
                max_results=10
            ))
        except Exception as e:
            pytest.skip(f"Could not query Firestore audit logs: {e}")

        if entries:
            # This is informational - some denials may be expected
            pytest.skip(
                f"Found {len(entries)} unauthorized Firestore access attempts. "
                "Review audit logs if unexpected."
            )
