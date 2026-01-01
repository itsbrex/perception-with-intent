"""
Agent 0 Orchestrator Tests
==========================

Tests for the perception orchestrator agent tools.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestStartIngestionRun:
    """Tests for start_ingestion_run function."""

    def test_returns_run_id(self):
        """Test start_ingestion_run returns run_id."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run("scheduled")
        assert "run_id" in result
        assert result["run_id"].startswith("run_")

    def test_returns_started_at_timestamp(self):
        """Test start_ingestion_run returns started_at timestamp."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run("scheduled")
        assert "started_at" in result
        # Should be valid ISO timestamp
        datetime.fromisoformat(result["started_at"].replace("Z", "+00:00"))

    def test_returns_trigger(self):
        """Test start_ingestion_run returns trigger."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run("manual_dashboard")
        assert result["trigger"] == "manual_dashboard"

    def test_returns_running_status(self):
        """Test start_ingestion_run returns running status."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run("scheduled")
        assert result["status"] == "running"

    @pytest.mark.parametrize("trigger", [
        "scheduled",
        "manual_dashboard",
        "webhook",
        "api_call",
        "test",
    ])
    def test_various_triggers(self, trigger):
        """Test various trigger types."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run(trigger)
        assert result["trigger"] == trigger

    def test_unique_run_ids(self):
        """Test that run_ids are unique when called at different times."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        import time

        run1 = start_ingestion_run("test")
        time.sleep(1.1)  # Delay > 1 second since run_id uses integer seconds
        run2 = start_ingestion_run("test")

        assert run1["run_id"] != run2["run_id"]


class TestFinalizeIngestionRun:
    """Tests for finalize_ingestion_run function."""

    def test_returns_run_id(self):
        """Test finalize returns run_id."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        result = finalize_ingestion_run("run_123", True)
        assert result["run_id"] == "run_123"

    def test_returns_finished_at_timestamp(self):
        """Test finalize returns finished_at timestamp."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        result = finalize_ingestion_run("run_123", True)
        assert "finished_at" in result
        datetime.fromisoformat(result["finished_at"].replace("Z", "+00:00"))

    def test_success_status(self):
        """Test success status."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        result = finalize_ingestion_run("run_123", True)
        assert result["status"] == "success"

    def test_failed_status(self):
        """Test failed status."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        result = finalize_ingestion_run("run_123", False)
        assert result["status"] == "failed"

    def test_with_stats(self):
        """Test with stats dictionary."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        stats = {"articles_ingested": 100, "articles_selected": 25}
        result = finalize_ingestion_run("run_123", True, stats)
        assert result["stats"] == stats

    def test_without_stats(self):
        """Test without stats dictionary."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        result = finalize_ingestion_run("run_123", True)
        assert result["stats"] == {}

    def test_empty_stats(self):
        """Test with empty stats dictionary."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
        result = finalize_ingestion_run("run_123", True, {})
        assert result["stats"] == {}


class TestBuildDailyIngestionPlan:
    """Tests for build_daily_ingestion_plan function."""

    def test_returns_plan_dict(self):
        """Test returns plan dictionary."""
        from perception_app.perception_agent.tools.agent_0_tools import build_daily_ingestion_plan
        result = build_daily_ingestion_plan()
        assert isinstance(result, dict)

    def test_includes_steps(self):
        """Test includes steps list."""
        from perception_app.perception_agent.tools.agent_0_tools import build_daily_ingestion_plan
        result = build_daily_ingestion_plan()
        assert "steps" in result
        assert isinstance(result["steps"], list)

    def test_steps_contain_required_operations(self):
        """Test steps contain required operations."""
        from perception_app.perception_agent.tools.agent_0_tools import build_daily_ingestion_plan
        result = build_daily_ingestion_plan()
        required_steps = ["fetch_sources", "harvest_articles", "validate", "store"]
        for step in required_steps:
            assert step in result["steps"]

    def test_with_user_id(self):
        """Test with specific user_id."""
        from perception_app.perception_agent.tools.agent_0_tools import build_daily_ingestion_plan
        result = build_daily_ingestion_plan("user_123")
        assert result["user_id"] == "user_123"

    def test_without_user_id(self):
        """Test without user_id."""
        from perception_app.perception_agent.tools.agent_0_tools import build_daily_ingestion_plan
        result = build_daily_ingestion_plan()
        assert result["user_id"] is None


class TestRunDailyIngestion:
    """Tests for run_daily_ingestion async function."""

    @pytest.mark.asyncio
    @patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources')
    @patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics')
    @patch('perception_app.perception_agent.tools.agent_0_tools.score_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.filter_top_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.build_brief_payload')
    @patch('perception_app.perception_agent.tools.agent_0_tools.validate_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.validate_brief')
    @patch('perception_app.perception_agent.tools.agent_0_tools.store_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.store_brief')
    @patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run')
    async def test_successful_pipeline(
        self,
        mock_update,
        mock_store_brief,
        mock_store_articles,
        mock_validate_brief,
        mock_validate_articles,
        mock_build_brief,
        mock_filter,
        mock_score,
        mock_topics,
        mock_harvest
    ):
        """Test successful pipeline execution."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        # Setup mocks
        mock_topics.return_value = [{"topic_id": "tech", "name": "Tech"}]
        mock_harvest.return_value = {"articles": [{"title": "Test"}], "stats": {}}
        mock_score.return_value = [{"title": "Test", "score": 8}]
        mock_filter.return_value = [{"title": "Test", "score": 8}]
        mock_build_brief.return_value = {"brief_id": "brief_123"}
        mock_validate_articles.return_value = {"valid": True, "errors": []}
        mock_validate_brief.return_value = {"valid": True, "errors": []}
        mock_store_articles.return_value = {"stored_count": 1, "errors": []}
        mock_store_brief.return_value = {"status": "stored"}

        result = await run_daily_ingestion()

        assert result["status"] == "success"
        assert "run_id" in result
        assert "stats" in result

    @pytest.mark.asyncio
    @patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources')
    @patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics')
    @patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run')
    async def test_no_articles_harvested(
        self,
        mock_update,
        mock_topics,
        mock_harvest
    ):
        """Test handling when no articles are harvested."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        mock_topics.return_value = [{"topic_id": "tech"}]
        mock_harvest.return_value = {"articles": [], "stats": {}}

        result = await run_daily_ingestion()

        assert result["status"] == "success"
        assert result["stats"]["articles_harvested"] == 0

    @pytest.mark.asyncio
    @patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources')
    @patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics')
    @patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run')
    async def test_default_topics_when_none_found(
        self,
        mock_update,
        mock_topics,
        mock_harvest
    ):
        """Test default topics are used when none found."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        mock_topics.return_value = []  # No topics
        mock_harvest.return_value = {"articles": [], "stats": {}}

        result = await run_daily_ingestion()

        # Should not fail, uses default topics
        assert result is not None

    @pytest.mark.asyncio
    @patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics')
    @patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run')
    async def test_handles_harvest_exception(
        self,
        mock_update,
        mock_topics
    ):
        """Test handling of harvest exception."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        mock_topics.return_value = [{"topic_id": "tech"}]

        with patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources') as mock_harvest:
            mock_harvest.side_effect = Exception("Network error")

            result = await run_daily_ingestion()

            assert result["status"] == "failed"
            assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    @patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources')
    @patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics')
    @patch('perception_app.perception_agent.tools.agent_0_tools.score_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.filter_top_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.build_brief_payload')
    @patch('perception_app.perception_agent.tools.agent_0_tools.validate_articles')
    @patch('perception_app.perception_agent.tools.agent_0_tools.validate_brief')
    @patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run')
    async def test_validation_failure_stops_pipeline(
        self,
        mock_update,
        mock_validate_brief,
        mock_validate_articles,
        mock_build_brief,
        mock_filter,
        mock_score,
        mock_topics,
        mock_harvest
    ):
        """Test that validation failure stops pipeline."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        mock_topics.return_value = [{"topic_id": "tech"}]
        mock_harvest.return_value = {"articles": [{"title": "Test"}]}
        mock_score.return_value = [{"title": "Test", "score": 8}]
        mock_filter.return_value = [{"title": "Test", "score": 8}]
        mock_build_brief.return_value = {"brief_id": "brief_123"}
        mock_validate_articles.return_value = {"valid": False, "errors": ["Invalid article"]}
        mock_validate_brief.return_value = {"valid": True, "errors": []}

        result = await run_daily_ingestion()

        assert result["status"] == "failed"
        assert "Invalid article" in result["errors"]


class TestIngestionRunIdFormat:
    """Tests for ingestion run ID format."""

    def test_run_id_starts_with_run(self):
        """Test run_id starts with 'run_'."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run("test")
        assert result["run_id"].startswith("run_")

    def test_run_id_contains_timestamp(self):
        """Test run_id contains timestamp."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
        result = start_ingestion_run("test")
        # Extract timestamp part
        parts = result["run_id"].split("_")
        assert len(parts) == 2
        # Should be parseable as int (Unix timestamp)
        timestamp = int(parts[1])
        assert timestamp > 0


class TestLogging:
    """Tests for logging in agent 0 tools."""

    @pytest.mark.asyncio
    @patch('perception_app.perception_agent.tools.agent_0_tools.logger')
    @patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources')
    @patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics')
    @patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run')
    async def test_logs_info_on_start(
        self,
        mock_update,
        mock_topics,
        mock_harvest,
        mock_logger
    ):
        """Test info logging on pipeline start."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        mock_topics.return_value = []
        mock_harvest.return_value = {"articles": []}

        await run_daily_ingestion()

        assert mock_logger.info.called


# Parametrized tests for triggers
@pytest.mark.parametrize("trigger,expected_status", [
    ("scheduled", "running"),
    ("manual", "running"),
    ("api_call", "running"),
])
def test_start_ingestion_run_triggers(trigger, expected_status):
    """Test various trigger types produce correct status."""
    from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run
    result = start_ingestion_run(trigger)
    assert result["status"] == expected_status


# Parametrized tests for finalize status
@pytest.mark.parametrize("success,expected_status", [
    (True, "success"),
    (False, "failed"),
])
def test_finalize_run_status(success, expected_status):
    """Test finalize produces correct status."""
    from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run
    result = finalize_ingestion_run("run_123", success)
    assert result["status"] == expected_status
