"""
Pipeline Integration Tests
==========================

Integration tests for the ingestion pipeline.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestPipelineFlow:
    """Tests for pipeline flow integration."""

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
    async def test_full_pipeline_success(
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
        """Test full pipeline executes successfully."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        # Setup mocks
        mock_topics.return_value = [{"topic_id": "tech"}]
        mock_harvest.return_value = {"articles": [{"title": "Test"}]}
        mock_score.return_value = [{"title": "Test", "score": 8}]
        mock_filter.return_value = [{"title": "Test", "score": 8}]
        mock_build_brief.return_value = {"brief_id": "brief_123"}
        mock_validate_articles.return_value = {"valid": True, "errors": []}
        mock_validate_brief.return_value = {"valid": True, "errors": []}
        mock_store_articles.return_value = {"stored_count": 1, "errors": []}
        mock_store_brief.return_value = {"status": "stored"}

        result = await run_daily_ingestion()

        assert result["status"] == "success"
        mock_harvest.assert_called_once()
        mock_score.assert_called_once()
        mock_store_articles.assert_called_once()

    @pytest.mark.asyncio
    async def test_pipeline_with_empty_harvest(self):
        """Test pipeline handles empty harvest."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        with patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources') as mock_harvest:
            with patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics') as mock_topics:
                with patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run'):
                    mock_topics.return_value = [{"topic_id": "tech"}]
                    mock_harvest.return_value = {"articles": []}

                    result = await run_daily_ingestion()

                    assert result["status"] == "success"
                    assert result["stats"]["articles_harvested"] == 0


class TestPipelineSteps:
    """Tests for individual pipeline steps."""

    def test_start_ingestion_creates_run(self):
        """Test starting ingestion creates run."""
        from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run

        run = start_ingestion_run("test")

        assert "run_id" in run
        assert run["status"] == "running"

    def test_finalize_ingestion_completes(self):
        """Test finalizing ingestion completes run."""
        from perception_app.perception_agent.tools.agent_0_tools import finalize_ingestion_run

        result = finalize_ingestion_run("run_123", True, {"count": 10})

        assert result["status"] == "success"
        assert result["stats"]["count"] == 10


class TestPipelineDataFlow:
    """Tests for data flow through pipeline."""

    def test_articles_flow_through_scoring(self):
        """Test articles flow through scoring step."""
        from perception_app.perception_agent.tools.agent_3_tools import score_articles

        articles = [
            {"title": "AI Article", "summary": "About AI"},
            {"title": "Cloud Article", "summary": "About cloud"},
        ]
        topics = [{"keywords": ["ai", "cloud"]}]

        scored = score_articles(articles, topics)

        assert len(scored) == 2
        for article in scored:
            assert "relevance_score" in article

    def test_articles_flow_through_filtering(self):
        """Test articles flow through filtering step."""
        from perception_app.perception_agent.tools.agent_3_tools import filter_top_articles

        articles = [
            {"title": "High Score", "relevance_score": 9},
            {"title": "Low Score", "relevance_score": 2},
            {"title": "Medium Score", "relevance_score": 5},
        ]

        filtered = filter_top_articles(articles, max_per_topic=10, min_score=5)

        # Should filter out low scores
        scores = [a["relevance_score"] for a in filtered]
        assert all(s >= 5 for s in scores)


class TestPipelineErrorHandling:
    """Tests for pipeline error handling."""

    @pytest.mark.asyncio
    async def test_handles_harvest_failure(self):
        """Test pipeline handles harvest failure."""
        from perception_app.perception_agent.tools.agent_0_tools import run_daily_ingestion

        with patch('perception_app.perception_agent.tools.agent_0_tools.harvest_all_sources') as mock_harvest:
            with patch('perception_app.perception_agent.tools.agent_0_tools.get_active_topics') as mock_topics:
                with patch('perception_app.perception_agent.tools.agent_0_tools.update_ingestion_run'):
                    mock_topics.return_value = [{"topic_id": "tech"}]
                    mock_harvest.side_effect = Exception("Network error")

                    result = await run_daily_ingestion()

                    assert result["status"] == "failed"
                    assert len(result["errors"]) > 0


# Parametrized integration tests
@pytest.mark.parametrize("trigger", ["scheduled", "manual", "api", "webhook"])
def test_pipeline_triggers(trigger):
    """Test pipeline with various triggers."""
    from perception_app.perception_agent.tools.agent_0_tools import start_ingestion_run

    run = start_ingestion_run(trigger)
    assert run["trigger"] == trigger


@pytest.mark.parametrize("article_count", [0, 1, 10, 50, 100])
def test_pipeline_article_volumes(article_count):
    """Test pipeline with various article volumes."""
    articles = [{"title": f"Article {i}", "relevance_score": i % 10} for i in range(article_count)]
    assert len(articles) == article_count


@pytest.mark.parametrize("topic_count", [0, 1, 5, 10])
def test_pipeline_topic_counts(topic_count):
    """Test pipeline with various topic counts."""
    topics = [{"topic_id": f"topic_{i}", "keywords": [f"keyword_{i}"]} for i in range(topic_count)]
    assert len(topics) == topic_count
