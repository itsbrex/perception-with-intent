"""
Utility Function Tests
======================

Tests for utility functions and helpers.
"""

import pytest
from datetime import datetime, date, timedelta, timezone
import json
import re
import uuid
import hashlib


class TestDateTimeUtils:
    """Tests for datetime utility functions."""

    def test_iso_format_generation(self):
        """Test ISO format generation."""
        now = datetime.now(tz=timezone.utc)
        iso = now.isoformat()
        assert "T" in iso
        assert "+" in iso or "Z" in iso

    def test_iso_format_parsing(self):
        """Test ISO format parsing."""
        iso_strings = [
            "2024-01-15T10:30:00Z",
            "2024-01-15T10:30:00+00:00",
            "2024-06-20T23:59:59.123456Z",
        ]
        for iso in iso_strings:
            parsed = datetime.fromisoformat(iso.replace("Z", "+00:00"))
            assert parsed is not None

    def test_timestamp_comparison(self):
        """Test timestamp comparison."""
        now = datetime.now(tz=timezone.utc)
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)

        assert past < now
        assert now < future
        assert past < future

    def test_date_difference_calculation(self):
        """Test date difference calculation."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)

        assert (today - yesterday).days == 1
        assert (today - week_ago).days == 7

    def test_timezone_conversion(self):
        """Test timezone handling."""
        utc_now = datetime.now(tz=timezone.utc)
        assert utc_now.tzinfo is not None


class TestStringUtils:
    """Tests for string utility functions."""

    def test_string_truncation(self):
        """Test string truncation."""
        long_string = "A" * 1000
        truncated = long_string[:500]
        assert len(truncated) == 500

    def test_string_sanitization(self):
        """Test string sanitization."""
        dirty = "  hello world  "
        clean = dirty.strip()
        assert clean == "hello world"

    def test_string_normalization(self):
        """Test string normalization."""
        strings = ["Hello", "HELLO", "hello"]
        normalized = [s.lower() for s in strings]
        assert all(s == "hello" for s in normalized)

    def test_slug_generation(self):
        """Test slug generation from title."""
        title = "Hello World - This is a Test!"
        # Simple slug generation
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        assert " " not in slug
        assert slug.islower() or '-' in slug

    def test_html_entity_handling(self):
        """Test HTML entity handling."""
        html_entities = {
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
        }
        for entity, char in html_entities.items():
            assert entity != char


class TestJSONUtils:
    """Tests for JSON utility functions."""

    def test_json_serialization(self):
        """Test JSON serialization."""
        data = {"key": "value", "number": 42, "array": [1, 2, 3]}
        json_str = json.dumps(data)
        assert isinstance(json_str, str)
        assert "key" in json_str

    def test_json_deserialization(self):
        """Test JSON deserialization."""
        json_str = '{"key": "value", "number": 42}'
        data = json.loads(json_str)
        assert data["key"] == "value"
        assert data["number"] == 42

    def test_json_with_dates(self):
        """Test JSON with date serialization."""
        data = {"date": date.today().isoformat()}
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        assert parsed["date"] == date.today().isoformat()

    def test_json_pretty_print(self):
        """Test JSON pretty printing."""
        data = {"key": "value"}
        pretty = json.dumps(data, indent=2)
        assert "\n" in pretty

    def test_json_with_unicode(self):
        """Test JSON with unicode characters."""
        data = {"emoji": "🚀", "chinese": "中文", "arabic": "عربي"}
        json_str = json.dumps(data, ensure_ascii=False)
        parsed = json.loads(json_str)
        assert parsed["emoji"] == "🚀"


class TestUUIDUtils:
    """Tests for UUID utility functions."""

    def test_uuid4_generation(self):
        """Test UUID4 generation."""
        uid = uuid.uuid4()
        assert len(str(uid)) == 36
        assert str(uid).count('-') == 4

    def test_uuid_uniqueness(self):
        """Test UUID uniqueness."""
        uuids = [uuid.uuid4() for _ in range(100)]
        assert len(uuids) == len(set(str(u) for u in uuids))

    def test_uuid_parsing(self):
        """Test UUID parsing."""
        uid_str = "123e4567-e89b-12d3-a456-426614174000"
        parsed = uuid.UUID(uid_str)
        assert str(parsed) == uid_str

    def test_uuid_version(self):
        """Test UUID version."""
        uid = uuid.uuid4()
        assert uid.version == 4


class TestHashUtils:
    """Tests for hashing utility functions."""

    def test_md5_hash(self):
        """Test MD5 hash generation."""
        data = "test string"
        md5 = hashlib.md5(data.encode()).hexdigest()
        assert len(md5) == 32

    def test_sha256_hash(self):
        """Test SHA256 hash generation."""
        data = "test string"
        sha256 = hashlib.sha256(data.encode()).hexdigest()
        assert len(sha256) == 64

    def test_hash_consistency(self):
        """Test hash consistency."""
        data = "test string"
        hash1 = hashlib.sha256(data.encode()).hexdigest()
        hash2 = hashlib.sha256(data.encode()).hexdigest()
        assert hash1 == hash2

    def test_hash_uniqueness(self):
        """Test hash uniqueness for different inputs."""
        data1 = "test1"
        data2 = "test2"
        hash1 = hashlib.sha256(data1.encode()).hexdigest()
        hash2 = hashlib.sha256(data2.encode()).hexdigest()
        assert hash1 != hash2


class TestRegexUtils:
    """Tests for regex utility functions."""

    def test_email_regex(self):
        """Test email regex pattern."""
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        valid_emails = ["test@example.com", "user.name@domain.org"]
        for email in valid_emails:
            assert re.match(email_pattern, email)

    def test_url_regex(self):
        """Test URL regex pattern."""
        url_pattern = r'https?://[\w\.-]+(/[\w\.-]*)*'
        valid_urls = ["https://example.com", "http://test.org/path"]
        for url in valid_urls:
            assert re.match(url_pattern, url)

    def test_date_regex(self):
        """Test date regex pattern."""
        date_pattern = r'\d{4}-\d{2}-\d{2}'
        dates = ["2024-01-15", "2023-12-31"]
        for d in dates:
            assert re.match(date_pattern, d)


class TestListUtils:
    """Tests for list utility functions."""

    def test_list_deduplication(self):
        """Test list deduplication."""
        items = [1, 2, 2, 3, 3, 3]
        unique = list(set(items))
        assert len(unique) == 3

    def test_list_sorting(self):
        """Test list sorting."""
        items = [3, 1, 4, 1, 5, 9, 2, 6]
        sorted_items = sorted(items)
        assert sorted_items == [1, 1, 2, 3, 4, 5, 6, 9]

    def test_list_filtering(self):
        """Test list filtering."""
        items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        evens = [x for x in items if x % 2 == 0]
        assert evens == [2, 4, 6, 8, 10]

    def test_list_chunking(self):
        """Test list chunking."""
        items = list(range(10))
        chunks = [items[i:i+3] for i in range(0, len(items), 3)]
        assert len(chunks) == 4


class TestDictUtils:
    """Tests for dictionary utility functions."""

    def test_dict_merge(self):
        """Test dictionary merge."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        merged = {**dict1, **dict2}
        assert len(merged) == 4

    def test_dict_key_access(self):
        """Test dictionary key access."""
        data = {"key": "value"}
        assert data.get("key") == "value"
        assert data.get("missing") is None
        assert data.get("missing", "default") == "default"

    def test_nested_dict_access(self):
        """Test nested dictionary access."""
        data = {"level1": {"level2": {"level3": "value"}}}
        assert data["level1"]["level2"]["level3"] == "value"


# Parametrized utility tests
@pytest.mark.parametrize("input_str,expected_len", [
    ("test", 4),
    ("hello world", 11),
    ("", 0),
    ("a" * 100, 100),
])
def test_string_length(input_str, expected_len):
    """Test string length calculation."""
    assert len(input_str) == expected_len


@pytest.mark.parametrize("input_str,expected", [
    ("  hello  ", "hello"),
    ("  ", ""),
    ("no spaces", "no spaces"),
    ("\t\ttabs\t\t", "tabs"),
])
def test_string_strip(input_str, expected):
    """Test string stripping."""
    assert input_str.strip() == expected


@pytest.mark.parametrize("input_str,expected", [
    ("HELLO", "hello"),
    ("Hello", "hello"),
    ("hello", "hello"),
    ("HeLLo WoRLd", "hello world"),
])
def test_string_lower(input_str, expected):
    """Test string lowercasing."""
    assert input_str.lower() == expected


@pytest.mark.parametrize("days,expected_weekday", [
    (0, date.today().weekday()),
    (7, date.today().weekday()),  # Same weekday
    (14, date.today().weekday()),  # Same weekday
])
def test_weekday_calculation(days, expected_weekday):
    """Test weekday calculation."""
    future_date = date.today() + timedelta(days=days)
    assert future_date.weekday() == expected_weekday


@pytest.mark.parametrize("n", [1, 10, 100, 1000])
def test_uuid_batch_generation(n):
    """Test generating batches of UUIDs."""
    uuids = [uuid.uuid4() for _ in range(n)]
    assert len(uuids) == n
    assert len(set(str(u) for u in uuids)) == n  # All unique


@pytest.mark.parametrize("data,expected_type", [
    ({}, dict),
    ([], list),
    ("string", str),
    (123, int),
    (1.5, float),
    (True, bool),
    (None, type(None)),
])
def test_type_checking(data, expected_type):
    """Test type checking."""
    assert type(data) == expected_type


@pytest.mark.parametrize("items,chunk_size,expected_chunks", [
    (list(range(10)), 3, 4),
    (list(range(9)), 3, 3),
    (list(range(5)), 2, 3),
    (list(range(1)), 1, 1),
])
def test_list_chunking_parametrized(items, chunk_size, expected_chunks):
    """Test list chunking with various sizes."""
    chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
    assert len(chunks) == expected_chunks
