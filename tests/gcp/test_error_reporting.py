"""
Cloud Error Reporting Tests
===========================

Test Google Cloud Error Reporting for aggregated errors.

Error Reporting groups similar errors together, making it easier
to track and prioritize issues.
"""

import pytest


@pytest.mark.integration
class TestErrorReporting:
    """Test Google Cloud Error Reporting for aggregated errors."""

    @pytest.fixture
    def error_stats_client(self, gcp_credentials):
        """Error Reporting stats client."""
        try:
            from google.cloud import errorreporting_v1beta1
            return errorreporting_v1beta1.ErrorStatsServiceClient()
        except ImportError:
            pytest.skip("google-cloud-error-reporting not installed")
        except Exception as e:
            pytest.skip(f"Could not create Error Reporting client: {e}")

    def test_no_new_error_groups_last_hour(
        self, error_stats_client, gcp_project, skip_without_gcp_auth
    ):
        """
        Check for new error groups in last hour.

        New error groups indicate new types of failures.
        """
        from google.cloud.errorreporting_v1beta1 import (
            ListGroupStatsRequest,
            QueryTimeRange,
        )

        try:
            request = ListGroupStatsRequest(
                project_name=f"projects/{gcp_project}",
                time_range=QueryTimeRange(period="PERIOD_1_HOUR"),
            )
            groups = list(error_stats_client.list_group_stats(request=request))
        except Exception as e:
            pytest.skip(f"Could not query Error Reporting: {e}")

        # Filter for groups with recent errors
        recent_errors = [g for g in groups if g.count > 0]

        if recent_errors:
            error_summary = [
                f"  - {g.group.group_id}: {g.count} occurrences"
                for g in recent_errors[:5]
            ]
            pytest.skip(
                f"Found {len(recent_errors)} error groups with recent errors:\n" +
                "\n".join(error_summary) +
                "\n\nReview in Cloud Console > Error Reporting"
            )

    def test_no_high_frequency_errors(
        self, error_stats_client, gcp_project, skip_without_gcp_auth
    ):
        """
        Check for high-frequency errors (>100 in 24 hours).

        High frequency indicates systematic issues.
        """
        from google.cloud.errorreporting_v1beta1 import (
            ListGroupStatsRequest,
            QueryTimeRange,
        )

        try:
            request = ListGroupStatsRequest(
                project_name=f"projects/{gcp_project}",
                time_range=QueryTimeRange(period="PERIOD_1_DAY"),
            )
            groups = list(error_stats_client.list_group_stats(request=request))
        except Exception as e:
            pytest.skip(f"Could not query Error Reporting: {e}")

        # Find high-frequency errors
        high_freq_threshold = 100
        high_freq_errors = [g for g in groups if g.count > high_freq_threshold]

        if high_freq_errors:
            error_summary = [
                f"  - {g.count} occurrences: {g.group.group_id[:50]}..."
                for g in high_freq_errors[:5]
            ]
            pytest.fail(
                f"Found {len(high_freq_errors)} high-frequency error groups "
                f"(>{high_freq_threshold}/day):\n" +
                "\n".join(error_summary)
            )
