"""
Factory Tests
=============

Tests for test data factories.
"""

import pytest
from datetime import datetime, date
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestArticleFactory:
    """Tests for ArticleFactory."""

    def test_creates_valid_article(self):
        """Test ArticleFactory creates valid article."""
        from tests.factories import ArticleFactory
        article = ArticleFactory()
        assert "id" in article
        assert "title" in article
        assert "url" in article
        assert "published_at" in article

    def test_article_has_uuid(self):
        """Test article has valid UUID."""
        from tests.factories import ArticleFactory
        article = ArticleFactory()
        # Should be valid UUID format
        uuid.UUID(article["id"])

    def test_article_has_relevance_score(self):
        """Test article has relevance score."""
        from tests.factories import ArticleFactory
        article = ArticleFactory()
        assert 0.0 <= article["relevance_score"] <= 1.0

    def test_high_relevance_trait(self):
        """Test high_relevance trait."""
        from tests.factories import ArticleFactory
        article = ArticleFactory(high_relevance=True)
        assert article["relevance_score"] >= 0.8

    def test_low_relevance_trait(self):
        """Test low_relevance trait."""
        from tests.factories import ArticleFactory
        article = ArticleFactory(low_relevance=True)
        assert article["relevance_score"] <= 0.3

    def test_tech_category_trait(self):
        """Test tech category trait."""
        from tests.factories import ArticleFactory
        article = ArticleFactory(tech=True)
        assert article["category"] == "tech"

    def test_unanalyzed_trait(self):
        """Test unanalyzed trait."""
        from tests.factories import ArticleFactory
        article = ArticleFactory(unanalyzed=True)
        assert article["is_analyzed"] is False
        assert article["ai_tags"] == []

    def test_unique_ids(self):
        """Test factories create unique IDs."""
        from tests.factories import ArticleFactory
        articles = [ArticleFactory() for _ in range(10)]
        ids = [a["id"] for a in articles]
        assert len(ids) == len(set(ids))


class TestArticleBatchFactory:
    """Tests for ArticleBatchFactory."""

    def test_creates_batch(self):
        """Test creating article batch."""
        from tests.factories.article_factory import ArticleBatchFactory
        batch = ArticleBatchFactory.create_batch(10)
        assert len(batch) == 10

    def test_creates_mixed_batch(self):
        """Test creating mixed batch."""
        from tests.factories.article_factory import ArticleBatchFactory
        batch = ArticleBatchFactory.create_mixed_batch(20)
        assert len(batch) == 20

    def test_creates_category_batch(self):
        """Test creating category batch."""
        from tests.factories.article_factory import ArticleBatchFactory
        batch = ArticleBatchFactory.create_category_batch("tech", 5)
        assert len(batch) == 5
        for article in batch:
            assert article["category"] == "tech"


class TestTopicFactory:
    """Tests for TopicFactory."""

    def test_creates_valid_topic(self):
        """Test TopicFactory creates valid topic."""
        from tests.factories import TopicFactory
        topic = TopicFactory()
        assert "id" in topic
        assert "name" in topic
        assert "keywords" in topic
        assert "category" in topic
        assert "active" in topic

    def test_topic_has_keywords(self):
        """Test topic has keywords list."""
        from tests.factories import TopicFactory
        topic = TopicFactory()
        assert isinstance(topic["keywords"], list)
        assert len(topic["keywords"]) > 0

    def test_inactive_trait(self):
        """Test inactive trait."""
        from tests.factories import TopicFactory
        topic = TopicFactory(inactive=True)
        assert topic["active"] is False

    def test_high_priority_trait(self):
        """Test high priority trait."""
        from tests.factories import TopicFactory
        topic = TopicFactory(high_priority=True)
        assert topic["priority"] == 10

    def test_tech_topic_trait(self):
        """Test tech topic trait."""
        from tests.factories import TopicFactory
        topic = TopicFactory(tech=True)
        assert topic["category"] == "tech"
        assert "AI" in topic["keywords"] or "machine learning" in topic["keywords"]


class TestRSSFeedFactory:
    """Tests for RSSFeedFactory."""

    def test_creates_valid_feed(self):
        """Test RSSFeedFactory creates valid feed."""
        from tests.factories import RSSFeedFactory
        feed = RSSFeedFactory()
        assert "id" in feed
        assert "name" in feed
        assert "url" in feed
        assert "category" in feed

    def test_feed_url_format(self):
        """Test feed has valid URL format."""
        from tests.factories import RSSFeedFactory
        feed = RSSFeedFactory()
        assert feed["url"].startswith("https://")
        assert "/rss" in feed["url"]

    def test_failing_trait(self):
        """Test failing trait."""
        from tests.factories import RSSFeedFactory
        feed = RSSFeedFactory(failing=True)
        assert feed["error_count"] >= 3


class TestRSSItemFactory:
    """Tests for RSSItemFactory."""

    def test_creates_valid_item(self):
        """Test RSSItemFactory creates valid item."""
        from tests.factories import RSSItemFactory
        item = RSSItemFactory()
        assert "title" in item
        assert "link" in item
        assert "description" in item
        assert "pub_date" in item

    def test_recent_trait(self):
        """Test recent trait."""
        from tests.factories import RSSItemFactory
        item = RSSItemFactory(recent=True)
        assert "GMT" in item["pub_date"]


class TestRSSResponseFactory:
    """Tests for RSSResponseFactory."""

    def test_creates_valid_rss_xml(self):
        """Test creates valid RSS XML."""
        from tests.factories.rss_factory import RSSResponseFactory
        xml = RSSResponseFactory.create_rss_xml(5)
        assert "<?xml" in xml
        assert "<rss" in xml
        assert "<channel>" in xml
        assert "<item>" in xml

    def test_creates_valid_atom_xml(self):
        """Test creates valid Atom XML."""
        from tests.factories.rss_factory import RSSResponseFactory
        xml = RSSResponseFactory.create_atom_xml(5)
        assert "<?xml" in xml
        assert "<feed" in xml
        assert "<entry>" in xml

    def test_creates_invalid_xml(self):
        """Test creates invalid XML for error testing."""
        from tests.factories.rss_factory import RSSResponseFactory
        xml = RSSResponseFactory.create_invalid_xml()
        assert "unclosed" in xml

    def test_creates_empty_feed(self):
        """Test creates empty feed."""
        from tests.factories.rss_factory import RSSResponseFactory
        xml = RSSResponseFactory.create_empty_feed()
        assert "<item>" not in xml


class TestDailySummaryFactory:
    """Tests for DailySummaryFactory."""

    def test_creates_valid_summary(self):
        """Test DailySummaryFactory creates valid summary."""
        from tests.factories import DailySummaryFactory
        summary = DailySummaryFactory()
        assert "id" in summary
        assert "date" in summary
        assert "article_count" in summary
        assert "executive_summary" in summary
        assert "highlights" in summary

    def test_summary_has_sections(self):
        """Test summary has sections."""
        from tests.factories import DailySummaryFactory
        summary = DailySummaryFactory()
        assert "sections" in summary
        assert isinstance(summary["sections"], dict)

    def test_yesterday_trait(self):
        """Test yesterday trait."""
        from tests.factories import DailySummaryFactory
        summary = DailySummaryFactory(yesterday=True)
        yesterday = (date.today() - __import__('datetime').timedelta(days=1)).isoformat()
        assert summary["date"] == yesterday

    def test_high_volume_trait(self):
        """Test high_volume trait."""
        from tests.factories import DailySummaryFactory
        summary = DailySummaryFactory(high_volume=True)
        assert summary["article_count"] >= 500


class TestAgentConfigFactory:
    """Tests for AgentConfigFactory."""

    def test_creates_valid_config(self):
        """Test AgentConfigFactory creates valid config."""
        from tests.factories import AgentConfigFactory
        config = AgentConfigFactory()
        assert "agent_id" in config
        assert "name" in config
        assert "model" in config
        assert "tools" in config

    def test_orchestrator_trait(self):
        """Test orchestrator trait."""
        from tests.factories import AgentConfigFactory
        config = AgentConfigFactory(orchestrator=True)
        assert config["agent_id"] == "agent_0"
        assert config["name"] == "Root Orchestrator"

    def test_disabled_trait(self):
        """Test disabled trait."""
        from tests.factories import AgentConfigFactory
        config = AgentConfigFactory(disabled=True)
        assert config["enabled"] is False


class TestAgentResponseFactory:
    """Tests for AgentResponseFactory."""

    def test_creates_valid_response(self):
        """Test AgentResponseFactory creates valid response."""
        from tests.factories import AgentResponseFactory
        response = AgentResponseFactory()
        assert "response_id" in response
        assert "agent_id" in response
        assert "status" in response
        assert "content" in response

    def test_success_trait(self):
        """Test success trait."""
        from tests.factories import AgentResponseFactory
        response = AgentResponseFactory(success=True)
        assert response["status"] == "success"

    def test_error_trait(self):
        """Test error trait."""
        from tests.factories import AgentResponseFactory
        response = AgentResponseFactory(error=True)
        assert response["status"] == "error"

    def test_with_tool_calls_trait(self):
        """Test with_tool_calls trait."""
        from tests.factories import AgentResponseFactory
        response = AgentResponseFactory(with_tool_calls=True)
        assert len(response["tool_calls"]) > 0


class TestAgentBatchFactory:
    """Tests for AgentBatchFactory."""

    def test_creates_all_agents(self):
        """Test creates all 8 agents."""
        from tests.factories.agent_factory import AgentBatchFactory
        agents = AgentBatchFactory.create_all_agents()
        assert len(agents) == 8

    def test_agents_have_unique_ids(self):
        """Test agents have unique IDs."""
        from tests.factories.agent_factory import AgentBatchFactory
        agents = AgentBatchFactory.create_all_agents()
        ids = [a["agent_id"] for a in agents]
        assert len(ids) == len(set(ids))

    def test_includes_orchestrator(self):
        """Test includes orchestrator agent."""
        from tests.factories.agent_factory import AgentBatchFactory
        agents = AgentBatchFactory.create_all_agents()
        orchestrator = next((a for a in agents if a["agent_id"] == "agent_0"), None)
        assert orchestrator is not None
        assert orchestrator["name"] == "Root Orchestrator"


# Parametrized tests for batch creation
@pytest.mark.parametrize("count", [1, 5, 10, 50, 100])
def test_article_batch_sizes(count):
    """Test article batch creation with various sizes."""
    from tests.factories.article_factory import ArticleBatchFactory
    batch = ArticleBatchFactory.create_batch(count)
    assert len(batch) == count


@pytest.mark.parametrize("category", ["tech", "business", "sports", "science", "health"])
def test_article_categories(category):
    """Test article factory with various categories."""
    from tests.factories import ArticleFactory
    article = ArticleFactory(category=category)
    assert article["category"] == category


@pytest.mark.parametrize("item_count", [0, 1, 5, 10, 20])
def test_rss_xml_item_counts(item_count):
    """Test RSS XML generation with various item counts."""
    from tests.factories.rss_factory import RSSResponseFactory
    xml = RSSResponseFactory.create_rss_xml(item_count)
    assert xml.count("<item>") == item_count
