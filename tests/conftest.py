"""
Global pytest fixtures and configuration for AI News Radar tests.
"""

import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Generator, List

import pytest
import yaml

# Add src to path for imports
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# ============================================================================
# Pytest Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (slower)")
    config.addinivalue_line("markers", "e2e: End-to-end tests (slowest)")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow tests")
    config.addinivalue_line("markers", "network: Tests requiring network")


# ============================================================================
# Path Fixtures
# ============================================================================


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def fixtures_dir(project_root: Path) -> Path:
    """Get the test fixtures directory."""
    return project_root / "tests" / "fixtures"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for tests.

    Yields the directory path and cleans up after the test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# ============================================================================
# Sample Data Fixtures
# ============================================================================


@pytest.fixture
def sample_articles() -> List[Dict[str, Any]]:
    """Sample article data for testing."""
    return [
        {
            "title": "AI Breakthrough in Natural Language Processing",
            "url": "https://example.com/ai-breakthrough",
            "description": "Researchers achieve new milestones in NLP.",
            "date": datetime.now(timezone.utc) - timedelta(hours=2),
            "source": "Tech News",
            "author": "Jane Doe",
            "tags": ["AI", "NLP"],
            "language": "en",
        },
        {
            "title": "Latest Machine Learning Trends",
            "url": "https://example.com/ml-trends",
            "description": "Exploring the future of ML.",
            "date": datetime.now(timezone.utc) - timedelta(hours=5),
            "source": "AI Weekly",
            "language": "en",
        },
        {
            "title": "Non-AI Article",
            "url": "https://example.com/other-news",
            "description": "This is not about AI.",
            "date": datetime.now(timezone.utc) - timedelta(hours=1),
            "source": "General News",
            "language": "en",
        },
    ]


@pytest.fixture
def sample_ai_articles() -> List[Dict[str, Any]]:
    """Sample AI-related articles."""
    now = datetime.now(timezone.utc)
    return [
        {
            "title": "GPT-4 Announces New Capabilities",
            "url": "https://example.com/gpt4-news",
            "description": "OpenAI announces new GPT-4 features.",
            "date": now,
            "source": "Tech News",
        },
        {
            "title": "Deep Learning Research Advances",
            "url": "https://example.com/dl-research",
            "description": "Breakthrough in deep learning.",
            "date": now - timedelta(hours=2),
            "source": "AI Research",
        },
    ]


@pytest.fixture
def test_keywords() -> Dict[str, List[str]]:
    """Create test keyword configuration."""
    return {
        "primary": ["artificial intelligence", "machine learning", "deep learning"],
        "secondary": ["chatgpt", "gpt", "openai", "anthropic"],
        "aliases": ["ai", "ml", "llm"],
    }


# ============================================================================
# Component Fixtures
# ============================================================================


@pytest.fixture
def sample_config(temp_dir: Path) -> Generator[Dict[str, Any], None, None]:
    """Create a sample RadarConfig."""
    from src.config import RadarConfig

    config = RadarConfig(
        cache_dir=temp_dir / "cache",
        request_timeout=10,
        max_articles_per_source=5,
        update_interval_hours=24,
        enable_cache=True,
        enable_deduplication=True,
    )
    config.ensure_directories()
    yield config


# ============================================================================
# Test Data Files Setup
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_test_data_files(fixtures_dir: Path):
    """
    Create test data files if they don't exist.
    This fixture runs once per session.
    """
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    # Create test keywords file
    test_keywords_file = fixtures_dir / "test_keywords.yaml"
    if not test_keywords_file.exists():
        test_keywords = {
            "keywords": {
                "primary": [
                    "artificial intelligence",
                    "machine learning",
                    "deep learning",
                ],
                "secondary": ["chatgpt", "gpt", "openai", "anthropic"],
                "aliases": ["ai", "ml", "llm"],
            }
        }
        with open(test_keywords_file, "w", encoding="utf-8") as f:
            yaml.dump(test_keywords, f)
