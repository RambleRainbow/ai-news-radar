"""
Text processing utilities for AI News Radar.

This module provides functions for cleaning and processing text.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove HTML entities
    text = re.sub(r"&[a-z]+;", "", text)

    # Remove special characters (keep letters, numbers, basic punctuation)
    text = re.sub(r"[^\w\s.,!?;:()-]", "", text)

    # Strip
    text = text.strip()

    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.

    Args:
        text: Input text
        min_length: Minimum keyword length

    Returns:
        List of keywords
    """
    if not text:
        return []

    # Clean and lowercase
    text = clean_text(text.lower())

    # Split into words
    words = re.findall(r"\b[a-z]{3,}\b", text)

    # Count word frequency
    word_count: dict[str, int] = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    # Sort by frequency and return top words
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    return [word for word, count in sorted_words[:10] if count >= 1]


def detect_language(text: str) -> str:
    """
    Detect language of text.

    Simple heuristic-based detection (English vs non-English).

    Args:
        text: Input text

    Returns:
        Language code ('en' for English, 'other' for others)
    """
    if not text:
        return "en"

    # Check for non-Latin characters
    non_latin = len(re.findall(r"[^\x00-\x7F]", text))

    # If more than 20% non-Latin, assume non-English
    if len(text) > 0 and non_latin / len(text) > 0.2:
        return "other"

    return "en"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    # Truncate at word boundary
    truncated = text[: max_length - len(suffix)]
    last_space = truncated.rfind(" ")

    if last_space > 0:
        truncated = truncated[:last_space]

    return truncated + suffix


def normalize_title(title: str) -> str:
    """
    Normalize article title for comparison.

    Args:
        title: Title text

    Returns:
        Normalized title
    """
    if not title:
        return ""

    # Lowercase
    title = title.lower()

    # Remove common prefixes
    prefixes = [
        r"^breaking:\s*",
        r"^update:\s*",
        r"^news:\s*",
        r"^\s*-\s*",
    ]

    for prefix in prefixes:
        title = re.sub(prefix, "", title)

    # Remove extra whitespace
    title = re.sub(r"\s+", " ", title)

    return title.strip()


def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from text.

    Args:
        text: Input text

    Returns:
        List of URLs
    """
    if not text:
        return []

    url_pattern = r"https?://[^\s<>\"]+|www\.[^\s<>\"]+"
    return re.findall(url_pattern, text)
