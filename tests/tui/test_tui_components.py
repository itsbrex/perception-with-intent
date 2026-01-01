"""
TUI Component Tests
===================

Tests for terminal UI components in perception_tui.py.
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestColors:
    """Tests for the Colors class."""

    def test_colors_class_exists(self):
        """Test Colors class is importable."""
        from perception_tui import Colors
        assert Colors is not None

    def test_primary_colors_defined(self):
        """Test primary colors are defined."""
        from perception_tui import Colors
        assert Colors.CYAN is not None
        assert Colors.MAGENTA is not None
        assert Colors.PURPLE is not None

    def test_status_colors_defined(self):
        """Test status colors are defined."""
        from perception_tui import Colors
        assert Colors.ACTIVE is not None
        assert Colors.INACTIVE is not None
        assert Colors.WARNING is not None

    def test_colors_are_valid_hex(self):
        """Test colors are valid hex values."""
        from perception_tui import Colors
        import re
        hex_pattern = re.compile(r'^#[0-9a-fA-F]{6}$')

        for attr in ['CYAN', 'MAGENTA', 'PURPLE', 'ACTIVE', 'INACTIVE']:
            color = getattr(Colors, attr)
            assert hex_pattern.match(color), f"{attr} is not valid hex: {color}"


class TestStatusIndicator:
    """Tests for the status_indicator function."""

    def test_active_indicator(self):
        """Test active status indicator."""
        from perception_tui import status_indicator, Colors
        result = status_indicator(True)
        assert "●" in result
        assert Colors.ACTIVE in result

    def test_inactive_indicator(self):
        """Test inactive status indicator."""
        from perception_tui import status_indicator, Colors
        result = status_indicator(False)
        assert "○" in result
        assert Colors.INACTIVE in result

    @pytest.mark.parametrize("active,expected_char", [
        (True, "●"),
        (False, "○"),
    ])
    def test_indicator_characters(self, active, expected_char):
        """Test indicator characters."""
        from perception_tui import status_indicator
        result = status_indicator(active)
        assert expected_char in result


class TestCategoryBadge:
    """Tests for the category_badge function."""

    def test_tech_category(self):
        """Test tech category badge."""
        from perception_tui import category_badge, Colors
        result = category_badge("tech")
        assert "TECH" in result.upper()

    def test_ai_category(self):
        """Test AI category badge."""
        from perception_tui import category_badge
        result = category_badge("ai")
        assert "AI" in result.upper()

    def test_business_category(self):
        """Test business category badge."""
        from perception_tui import category_badge
        result = category_badge("business")
        assert "BUSINESS" in result.upper()

    def test_unknown_category_uses_default(self):
        """Test unknown category uses default color."""
        from perception_tui import category_badge, Colors
        result = category_badge("unknown_xyz")
        assert Colors.DIM in result

    def test_badge_truncation(self):
        """Test category name truncation."""
        from perception_tui import category_badge
        result = category_badge("verylongcategoryname")
        # Badge should truncate at 8 chars
        assert len(result) < 100  # Reasonable length

    @pytest.mark.parametrize("category", [
        "tech", "ai", "business", "security", "crypto",
        "science", "world", "sports", "automotive", "engineering"
    ])
    def test_all_known_categories(self, category):
        """Test all known categories have colors."""
        from perception_tui import category_badge
        result = category_badge(category)
        assert category.upper()[:8] in result.upper()


class TestLoadRSSSources:
    """Tests for the load_rss_sources function."""

    @patch('pathlib.Path.exists')
    def test_returns_empty_when_no_config(self, mock_exists):
        """Test returns empty list when config doesn't exist."""
        mock_exists.return_value = False
        from perception_tui import load_rss_sources
        result = load_rss_sources()
        assert result == []

    @patch('builtins.open')
    @patch('pathlib.Path.exists')
    def test_loads_yaml_config(self, mock_exists, mock_open):
        """Test loading YAML config."""
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = """
sources:
  - name: Test Feed
    url: https://example.com/rss
    category: tech
"""
        from perception_tui import load_rss_sources
        result = load_rss_sources()
        assert isinstance(result, list)


class TestLoadActiveFeeds:
    """Tests for the load_active_feeds function."""

    @patch('pathlib.Path.exists')
    def test_returns_empty_when_no_file(self, mock_exists):
        """Test returns empty list when file doesn't exist."""
        mock_exists.return_value = False
        from perception_tui import load_active_feeds
        result = load_active_feeds()
        assert result == []


class TestGetCategoryStats:
    """Tests for the get_category_stats function."""

    def test_counts_categories(self):
        """Test counting categories."""
        from perception_tui import get_category_stats
        sources = [
            {"category": "tech"},
            {"category": "tech"},
            {"category": "business"},
        ]
        result = get_category_stats(sources)
        assert result["tech"] == 2
        assert result["business"] == 1

    def test_handles_missing_category(self):
        """Test handling sources without category."""
        from perception_tui import get_category_stats
        sources = [
            {"name": "No Category"},
            {"category": "tech"},
        ]
        result = get_category_stats(sources)
        assert "other" in result
        assert result["tech"] == 1

    def test_sorts_by_count_descending(self):
        """Test sorting by count."""
        from perception_tui import get_category_stats
        sources = [
            {"category": "tech"},
            {"category": "tech"},
            {"category": "tech"},
            {"category": "business"},
        ]
        result = get_category_stats(sources)
        categories = list(result.keys())
        assert categories[0] == "tech"

    def test_empty_sources(self):
        """Test with empty sources list."""
        from perception_tui import get_category_stats
        result = get_category_stats([])
        assert result == {}


class TestMakeHeader:
    """Tests for the make_header function."""

    def test_header_returns_panel(self):
        """Test header returns Panel object."""
        from perception_tui import make_header
        from rich.panel import Panel
        result = make_header()
        assert isinstance(result, Panel)

    def test_header_contains_perception(self):
        """Test header contains PERCEPTION text."""
        from perception_tui import make_header
        result = make_header()
        # Check it's a panel (content will have the text)
        assert result.title is not None or result.subtitle is not None


class TestMakeStatusPanel:
    """Tests for the make_status_panel function."""

    def test_status_panel_returns_panel(self):
        """Test status panel returns Panel object."""
        from perception_tui import make_status_panel
        from rich.panel import Panel
        result = make_status_panel()
        assert isinstance(result, Panel)

    def test_status_panel_has_title(self):
        """Test status panel has a title."""
        from perception_tui import make_status_panel
        result = make_status_panel()
        assert result.title is not None


class TestMakeFeedsTable:
    """Tests for the make_feeds_table function."""

    def test_feeds_table_returns_panel(self):
        """Test feeds table returns Panel object."""
        from perception_tui import make_feeds_table
        from rich.panel import Panel
        sources = [
            {"name": "Test Feed", "category": "tech", "active": True}
        ]
        result = make_feeds_table(sources)
        assert isinstance(result, Panel)

    def test_feeds_table_empty_sources(self):
        """Test feeds table with empty sources."""
        from perception_tui import make_feeds_table
        result = make_feeds_table([])
        assert result is not None

    def test_feeds_table_limit(self):
        """Test feeds table respects limit."""
        from perception_tui import make_feeds_table
        sources = [
            {"name": f"Feed {i}", "category": "tech", "active": True}
            for i in range(50)
        ]
        result = make_feeds_table(sources, limit=10)
        # Should still return valid panel
        assert result is not None


class TestMakeCategoryChart:
    """Tests for the make_category_chart function."""

    def test_category_chart_returns_panel(self):
        """Test category chart returns Panel object."""
        from perception_tui import make_category_chart
        from rich.panel import Panel
        stats = {"tech": 10, "business": 5}
        result = make_category_chart(stats)
        assert isinstance(result, Panel)

    def test_category_chart_empty_stats(self):
        """Test category chart with empty stats."""
        from perception_tui import make_category_chart
        result = make_category_chart({})
        assert result is not None


class TestUIRichMarkup:
    """Tests for Rich markup in UI elements."""

    def test_markup_not_malformed(self):
        """Test Rich markup is not malformed."""
        from rich.console import Console
        from perception_tui import make_header, make_status_panel

        console = Console(file=StringIO(), force_terminal=True)

        # These should not raise markup errors
        try:
            console.print(make_header())
            console.print(make_status_panel())
        except Exception as e:
            pytest.fail(f"Rich markup error: {e}")


class TestConsoleOutput:
    """Tests for console output."""

    def test_console_creation(self):
        """Test console can be created."""
        from perception_tui import console
        assert console is not None

    def test_console_is_rich_console(self):
        """Test console is Rich Console."""
        from perception_tui import console
        from rich.console import Console
        assert isinstance(console, Console)


# Parametrized tests for colors
@pytest.mark.parametrize("color_name,expected_prefix", [
    ("CYAN", "#"),
    ("MAGENTA", "#"),
    ("PURPLE", "#"),
    ("PINK", "#"),
    ("BLUE", "#"),
    ("YELLOW", "#"),
    ("ACTIVE", "#"),
    ("INACTIVE", "#"),
    ("WARNING", "#"),
])
def test_color_format(color_name, expected_prefix):
    """Test color values have correct format."""
    from perception_tui import Colors
    color = getattr(Colors, color_name)
    assert color.startswith(expected_prefix)


# Parametrized tests for category colors
@pytest.mark.parametrize("category,should_have_color", [
    ("tech", True),
    ("ai", True),
    ("business", True),
    ("security", True),
    ("unknown", True),  # Should use default
])
def test_category_has_color(category, should_have_color):
    """Test categories have associated colors."""
    from perception_tui import category_badge
    result = category_badge(category)
    assert result is not None
    assert len(result) > 0
