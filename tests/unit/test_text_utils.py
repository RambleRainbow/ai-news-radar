"""
Tests for text utilities.
"""

from skill.utils.text_utils import (
    clean_text,
    detect_language,
    extract_keywords,
    extract_urls,
    normalize_title,
    truncate_text,
)


class TestCleanText:
    """Test text cleaning."""

    def test_clean_text_basic(self):
        """Test basic text cleaning."""
        text = "  Hello   World  "
        result = clean_text(text)
        assert result == "Hello World"

    def test_clean_text_html_entities(self):
        """Test removing HTML entities."""
        text = "Hello &nbsp; World &amp; Test"
        result = clean_text(text)
        assert "nbsp" not in result
        assert "amp" not in result

    def test_clean_text_special_chars(self):
        """Test removing special characters."""
        text = "Hello@#$%^&*()World"
        result = clean_text(text)
        assert "@" not in result
        assert "#" not in result
        assert "%" not in result
        assert "Hello" in result
        assert "World" in result

    def test_clean_text_empty(self):
        """Test cleaning empty text."""
        result = clean_text("")
        assert result == ""

    def test_clean_text_none(self):
        """Test cleaning None returns empty."""
        result = clean_text(None)
        assert result == ""


class TestExtractKeywords:
    """Test keyword extraction."""

    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "artificial intelligence machine learning deep learning neural network"
        result = extract_keywords(text)
        assert "artificial" in result
        assert "intelligence" in result
        assert "machine" in result

    def test_extract_keywords_min_length(self):
        """Test minimum length filter."""
        text = "AI is hot now"
        result = extract_keywords(text, min_length=3)
        assert "AI" not in result

    def test_extract_keywords_empty(self):
        """Test extracting from empty text."""
        result = extract_keywords("")
        assert result == []

    def test_extract_keywords_frequency_sort(self):
        """Test keywords sorted by frequency."""
        text = "machine learning machine learning neural"
        result = extract_keywords(text)
        # Check that multiple keywords are present and sorted
        assert len(result) > 0
        assert "machine" in result
        assert "learning" in result
        assert "neural" in result


class TestDetectLanguage:
    """Test language detection."""

    def test_detect_english(self):
        """Test detecting English text."""
        text = "This is a normal English sentence."
        result = detect_language(text)
        assert result == "en"

    def test_detect_empty(self):
        """Test detecting empty text."""
        result = detect_language("")
        assert result == "en"

    def test_detect_non_latin(self):
        """Test detecting non-Latin characters."""
        text = "这是一段中文文本" * 10
        result = detect_language(text)
        assert result == "other"


class TestTruncateText:
    """Test text truncation."""

    def test_truncate_short_text(self):
        """Test truncating short text (no change)."""
        text = "Short text"
        result = truncate_text(text, max_length=50)
        assert result == "Short text"

    def test_truncate_long_text(self):
        """Test truncating long text."""
        text = "This is a very long text that needs to be truncated"
        result = truncate_text(text, max_length=20)
        assert len(result) <= 23  # 20 + "..."
        assert result.endswith("...")

    def test_truncate_empty(self):
        """Test truncating empty text."""
        result = truncate_text("")
        assert result == ""

    def test_truncate_custom_suffix(self):
        """Test custom suffix."""
        text = "This is a very long text"
        result = truncate_text(text, max_length=15, suffix=" [more]")
        assert len(result) <= 21
        assert "[more]" in result


class TestNormalizeTitle:
    """Test title normalization."""

    def test_normalize_lowercase(self):
        """Test converting to lowercase."""
        result = normalize_title("AI News")
        assert result.islower()
        assert "ai news" == result

    def test_remove_prefixes(self):
        """Test removing common prefixes."""
        result = normalize_title("Breaking: AI News")
        assert not result.startswith("breaking")

        result = normalize_title("Update: New Model")
        assert not result.startswith("update")

    def test_remove_leading_dash(self):
        """Test removing leading dashes."""
        result = normalize_title("- Test Title")
        assert not result.startswith("-")
        assert not result.startswith(" ")

    def test_empty_title(self):
        """Test normalizing empty title."""
        result = normalize_title("")
        assert result == ""

    def test_none_title(self):
        """Test normalizing None."""
        result = normalize_title(None)
        assert result == ""

    def test_remove_extra_whitespace(self):
        """Test removing extra whitespace."""
        result = normalize_title("AI   News    Test")
        assert "AI   News" not in result
        assert "ai news test" == result


class TestExtractUrls:
    """Test URL extraction."""

    def test_extract_http_urls(self):
        """Test extracting HTTP URLs."""
        text = "Visit https://example.com for more info"
        result = extract_urls(text)
        assert "https://example.com" in result

    def test_extract_www_urls(self):
        """Test extracting www URLs."""
        text = "Go to www.example.com"
        result = extract_urls(text)
        assert "www.example.com" in result

    def test_extract_multiple_urls(self):
        """Test extracting multiple URLs."""
        text = "See https://example.com and www.test.com"
        result = extract_urls(text)
        assert len(result) == 2

    def test_extract_no_urls(self):
        """Test extracting from text without URLs."""
        result = extract_urls("Just some text")
        assert result == []

    def test_extract_empty(self):
        """Test extracting from empty text."""
        result = extract_urls("")
        assert result == []
