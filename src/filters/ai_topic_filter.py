"""
AI topic filter for AI News Radar.

This module filters articles by AI-related keywords and topics.
"""

import logging
import re
from typing import List, Dict, Set, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AITopicFilter:
    """
    Filter articles by AI-related keywords and topics.

    Supports primary keywords (required), secondary keywords (optional boost),
    and aliases for matching.
    """

    def __init__(self, keywords_file: Optional[Path] = None, keywords: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the AI topic filter.

        Args:
            keywords_file: Path to YAML file containing keyword categories
            keywords: Direct keywords dictionary (overrides file)
        """
        if keywords:
            self.keywords = keywords
        elif keywords_file:
            self.keywords = self._load_keywords(keywords_file)
        else:
            self.keywords = {
                "primary": [
                    "artificial intelligence",
                    "machine learning",
                    "deep learning",
                    "neural network",
                    "natural language processing",
                    "computer vision",
                    "generative ai",
                    "large language model",
                    "llm",
                ],
                "secondary": [
                    "chatgpt",
                    "gpt",
                    "openai",
                    "anthropic",
                    "claude",
                    "hugging face",
                    "transformer",
                    "bert",
                    "stable diffusion",
                    "midjourney",
                ],
                "aliases": [
                    "ai",
                    "ml",
                    "ai/ml",
                    "nlp",
                    "cv",
                ],
            }

        # Compile regex patterns for efficient matching
        self.primary_patterns = self._compile_patterns(self.keywords.get("primary", []))
        self.secondary_patterns = self._compile_patterns(self.keywords.get("secondary", []))
        self.alias_patterns = self._compile_patterns(self.keywords.get("aliases", []))

        logger.debug(f"AI Topic Filter initialized with {len(self.primary_patterns)} primary patterns")

    def _load_keywords(self, keywords_file: Path) -> Dict[str, List[str]]:
        """
        Load keywords from YAML file.

        Args:
            keywords_file: Path to keywords YAML file

        Returns:
            Dictionary of keyword categories
        """
        try:
            import yaml

            with open(keywords_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            return {
                "primary": data.get("primary", []),
                "secondary": data.get("secondary", []),
                "aliases": data.get("aliases", []),
            }
        except Exception as e:
            logger.error(f"Failed to load keywords from {keywords_file}: {e}")
            return {"primary": [], "secondary": [], "aliases": []}

    def _compile_patterns(self, keywords: List[str]) -> List[re.Pattern]:
        """
        Compile regex patterns from keywords.

        Args:
            keywords: List of keyword strings

        Returns:
            List of compiled regex patterns
        """
        patterns = []
        for keyword in keywords:
            # Case-insensitive word boundary matching
            pattern = re.compile(rf"\b{re.escape(keyword.lower())}\b", re.IGNORECASE)
            patterns.append(pattern)
        return patterns

    def filter(self, articles: List[Dict], min_score: float = 0.5) -> List[Dict]:
        """
        Filter articles by AI topic relevance.

        Args:
            articles: List of article dictionaries
            min_score: Minimum relevance score (0.0 to 1.0)

        Returns:
            Filtered list of articles
        """
        filtered = []

        for article in articles:
            score = self.score(article)
            if score >= min_score:
                article["_ai_score"] = score
                filtered.append(article)

        logger.info(f"AI Topic Filter: {len(filtered)}/{len(articles)} articles passed (min_score={min_score})")
        return filtered

    def score(self, article: Dict) -> float:
        """
        Score article by AI topic relevance.

        Scoring:
        - Primary keyword match: 1.0
        - Secondary keyword match: 0.7
        - Alias match: 0.5
        - Multiple matches: use highest score

        Args:
            article: Article dictionary

        Returns:
            Relevance score (0.0 to 1.0)
        """
        text = self._get_searchable_text(article)
        if not text:
            return 0.0

        text_lower = text.lower()

        # Check primary patterns (highest priority)
        for pattern in self.primary_patterns:
            if pattern.search(text_lower):
                return 1.0

        # Check secondary patterns
        for pattern in self.secondary_patterns:
            if pattern.search(text_lower):
                return 0.7

        # Check alias patterns
        for pattern in self.alias_patterns:
            if pattern.search(text_lower):
                return 0.5

        return 0.0

    def _get_searchable_text(self, article: Dict) -> str:
        """
        Get searchable text from article.

        Args:
            article: Article dictionary

        Returns:
            Combined searchable text
        """
        parts = []

        for key in ["title", "description", "tags"]:
            if key in article and article[key]:
                if isinstance(article[key], list):
                    parts.append(" ".join(str(item) for item in article[key]))
                else:
                    parts.append(str(article[key]))

        return " ".join(parts)

    def get_matched_keywords(self, article: Dict) -> List[str]:
        """
        Get list of keywords that matched in the article.

        Args:
            article: Article dictionary

        Returns:
            List of matched keyword strings
        """
        text = self._get_searchable_text(article)
        if not text:
            return []

        text_lower = text.lower()
        matched = []

        # Check all patterns
        for pattern in self.primary_patterns + self.secondary_patterns + self.alias_patterns:
            if pattern.search(text_lower):
                matched.append(pattern.pattern)

        return matched

    def sort_by_relevance(self, articles: List[Dict], reverse: bool = True) -> List[Dict]:
        """
        Sort articles by AI relevance score.

        Args:
            articles: List of article dictionaries
            reverse: Sort in descending order if True

        Returns:
            Sorted list of articles
        """
        # Add scores if not present
        for article in articles:
            if "_ai_score" not in article:
                article["_ai_score"] = self.score(article)

        return sorted(articles, key=lambda a: a.get("_ai_score", 0), reverse=reverse)
