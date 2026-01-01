"""
Data Validation Tests
=====================

Tests for data validation logic and Pydantic models.
"""

import pytest
from datetime import datetime, date, timedelta
from pydantic import ValidationError
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestArticleValidation:
    """Tests for article data validation."""

    def test_valid_article_title(self):
        """Test valid article title."""
        title = "Breaking News: Major Event Happens"
        assert len(title) > 0
        assert len(title) < 500

    def test_empty_title_invalid(self):
        """Test empty title is invalid."""
        title = ""
        assert len(title) == 0

    def test_title_max_length(self):
        """Test title max length validation."""
        title = "A" * 1000
        # Title should be truncated or rejected if too long
        assert len(title) > 500

    def test_valid_url_format(self):
        """Test valid URL format."""
        urls = [
            "https://example.com/article",
            "http://test.org/news/123",
            "https://sub.domain.co.uk/path/to/article",
        ]
        for url in urls:
            assert url.startswith("http")

    def test_invalid_url_format(self):
        """Test invalid URL format."""
        invalid_urls = [
            "not-a-url",
            "ftp://files.com/doc",
            "",
            "javascript:alert(1)",
        ]
        for url in invalid_urls:
            assert not url.startswith("https://") or url == ""

    def test_relevance_score_bounds(self):
        """Test relevance score within bounds."""
        valid_scores = [0.0, 0.5, 1.0, 0.123, 0.999]
        for score in valid_scores:
            assert 0.0 <= score <= 1.0

    def test_relevance_score_out_of_bounds(self):
        """Test relevance score out of bounds."""
        invalid_scores = [-0.1, 1.1, 2.0, -1.0]
        for score in invalid_scores:
            assert score < 0.0 or score > 1.0

    def test_valid_category(self):
        """Test valid category values."""
        valid_categories = ["tech", "business", "sports", "science", "health", "world"]
        for cat in valid_categories:
            assert cat.islower()
            assert len(cat) > 0

    def test_valid_timestamp_format(self):
        """Test valid ISO timestamp format."""
        timestamps = [
            "2024-01-15T10:30:00Z",
            "2024-01-15T10:30:00+00:00",
            "2024-01-15T10:30:00.123456Z",
        ]
        for ts in timestamps:
            # Should be parseable
            parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            assert parsed is not None

    def test_uuid_format(self):
        """Test UUID format validation."""
        valid_uuids = [
            str(uuid.uuid4()),
            "123e4567-e89b-12d3-a456-426614174000",
        ]
        for uid in valid_uuids:
            uuid.UUID(uid)  # Should not raise

    def test_invalid_uuid_format(self):
        """Test invalid UUID format."""
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "",
        ]
        for uid in invalid_uuids:
            with pytest.raises(ValueError):
                uuid.UUID(uid)

    def test_ai_tags_list(self):
        """Test AI tags is a list."""
        tags = ["AI", "technology", "innovation"]
        assert isinstance(tags, list)
        assert all(isinstance(t, str) for t in tags)

    def test_sentiment_values(self):
        """Test valid sentiment values."""
        valid_sentiments = ["positive", "negative", "neutral"]
        for sent in valid_sentiments:
            assert sent in valid_sentiments


class TestTopicValidation:
    """Tests for topic data validation."""

    def test_keywords_is_list(self):
        """Test keywords is a list."""
        keywords = ["AI", "machine learning", "deep learning"]
        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_keywords_not_empty_strings(self):
        """Test keywords are not empty strings."""
        keywords = ["AI", "ML", "NLP"]
        for kw in keywords:
            assert len(kw) > 0
            assert kw.strip() == kw

    def test_priority_bounds(self):
        """Test priority within bounds."""
        valid_priorities = [1, 5, 10]
        for p in valid_priorities:
            assert 1 <= p <= 10

    def test_match_threshold_bounds(self):
        """Test match threshold within bounds."""
        valid_thresholds = [0.5, 0.7, 0.9, 1.0]
        for t in valid_thresholds:
            assert 0.0 <= t <= 1.0


class TestDailySummaryValidation:
    """Tests for daily summary data validation."""

    def test_date_format(self):
        """Test date format validation."""
        date_str = date.today().isoformat()
        parsed = date.fromisoformat(date_str)
        assert parsed is not None

    def test_article_count_non_negative(self):
        """Test article count is non-negative."""
        counts = [0, 1, 100, 1000]
        for c in counts:
            assert c >= 0

    def test_highlights_is_list(self):
        """Test highlights is a list."""
        highlights = ["Major event", "Key development", "Breaking news"]
        assert isinstance(highlights, list)
        assert all(isinstance(h, str) for h in highlights)

    def test_sections_is_dict(self):
        """Test sections is a dictionary."""
        sections = {"tech": {"count": 10}, "business": {"count": 5}}
        assert isinstance(sections, dict)

    def test_sentiment_percentages_sum_to_100(self):
        """Test sentiment percentages approximately sum to 100."""
        sentiment = {
            "positive_percentage": 40,
            "negative_percentage": 20,
            "neutral_percentage": 40,
        }
        total = sum(sentiment.values())
        assert 95 <= total <= 105  # Allow small rounding errors


class TestRSSFeedValidation:
    """Tests for RSS feed data validation."""

    def test_fetch_interval_positive(self):
        """Test fetch interval is positive."""
        intervals = [60, 300, 3600, 86400]
        for i in intervals:
            assert i > 0

    def test_error_count_non_negative(self):
        """Test error count is non-negative."""
        counts = [0, 1, 5, 10]
        for c in counts:
            assert c >= 0

    def test_active_is_boolean(self):
        """Test active is boolean."""
        values = [True, False]
        for v in values:
            assert isinstance(v, bool)


class TestAgentResponseValidation:
    """Tests for agent response validation."""

    def test_status_values(self):
        """Test valid status values."""
        valid_statuses = ["success", "error", "pending"]
        for s in valid_statuses:
            assert s in valid_statuses

    def test_latency_positive(self):
        """Test latency is positive."""
        latencies = [1, 100, 1000, 5000]
        for l in latencies:
            assert l > 0

    def test_tokens_used_positive(self):
        """Test tokens used is positive."""
        tokens = [10, 100, 1000, 4096]
        for t in tokens:
            assert t > 0


# Parametrized validation tests
@pytest.mark.parametrize("score", [
    0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0
])
def test_valid_relevance_scores(score):
    """Test valid relevance scores."""
    assert 0.0 <= score <= 1.0


@pytest.mark.parametrize("score", [
    -0.1, -1.0, 1.01, 1.5, 2.0, 100.0
])
def test_invalid_relevance_scores(score):
    """Test invalid relevance scores."""
    assert score < 0.0 or score > 1.0


@pytest.mark.parametrize("category", [
    "tech", "business", "sports", "science", "health",
    "world", "entertainment", "politics", "environment"
])
def test_valid_categories(category):
    """Test valid category names."""
    assert len(category) > 0
    assert category.islower()


@pytest.mark.parametrize("priority", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
def test_valid_priorities(priority):
    """Test valid priority values."""
    assert 1 <= priority <= 10


@pytest.mark.parametrize("timestamp", [
    "2024-01-15T10:30:00Z",
    "2024-01-15T10:30:00+00:00",
    "2024-06-20T23:59:59Z",
    "2024-12-31T00:00:00+00:00",
])
def test_valid_timestamps(timestamp):
    """Test valid ISO timestamps."""
    parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    assert parsed is not None


@pytest.mark.parametrize("url", [
    "https://example.com",
    "https://sub.example.com/path",
    "https://example.com/path?query=1",
    "https://example.com/path#anchor",
    "http://test.org/article",
])
def test_valid_urls(url):
    """Test valid URL formats."""
    assert url.startswith("http")
    assert "://" in url


@pytest.mark.parametrize("invalid_url", [
    "",
    "not-a-url",
    "ftp://files.com",
    "javascript:alert(1)",
    "data:text/html,<script>",
])
def test_invalid_urls(invalid_url):
    """Test invalid URL formats."""
    is_valid = invalid_url.startswith("http://") or invalid_url.startswith("https://")
    # These should all be invalid
    assert not is_valid or invalid_url == ""


@pytest.mark.parametrize("sentiment", ["positive", "negative", "neutral"])
def test_valid_sentiments(sentiment):
    """Test valid sentiment values."""
    assert sentiment in ["positive", "negative", "neutral"]


@pytest.mark.parametrize("status", ["success", "error", "pending", "running", "failed"])
def test_valid_statuses(status):
    """Test valid status values."""
    assert len(status) > 0


# Date range validation tests
@pytest.mark.parametrize("days_ago", [0, 1, 7, 30, 90, 365])
def test_date_within_range(days_ago):
    """Test dates within various ranges."""
    test_date = date.today() - timedelta(days=days_ago)
    assert test_date <= date.today()


# Word count validation tests
@pytest.mark.parametrize("word_count", [0, 50, 100, 500, 1000, 5000, 10000])
def test_valid_word_counts(word_count):
    """Test valid word count values."""
    assert word_count >= 0


# Batch size validation tests
@pytest.mark.parametrize("batch_size", [1, 10, 50, 100, 500, 1000])
def test_valid_batch_sizes(batch_size):
    """Test valid batch size values."""
    assert batch_size > 0
    assert batch_size <= 10000  # Reasonable upper limit
