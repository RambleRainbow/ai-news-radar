"""
State management for AI News Radar.

This module provides state tracking for incremental updates.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class State:
    """
    State manager for tracking incremental updates.

    Stores last fetch timestamp and other state information.
    """

    def __init__(self, state_file: Path):
        """
        Initialize state manager.

        Args:
            state_file: Path to state JSON file
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        """
        Load state from file.

        Returns:
            Dictionary containing state information
        """
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded state from {self.state_file}")
            return data
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load state from {self.state_file}: {e}")
            return {}

    def save(self, state: Dict[str, Any]) -> None:
        """
        Save state to file.

        Args:
            state: Dictionary containing state information
        """
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, default=str)
            logger.debug(f"Saved state to {self.state_file}")
        except (IOError, TypeError) as e:
            logger.error(f"Failed to save state to {self.state_file}: {e}")
            raise

    def get_last_fetch_time(self) -> Optional[datetime]:
        """
        Get the last fetch timestamp.

        Returns:
            Datetime of last fetch, or None if no previous fetch
        """
        state = self.load()
        last_fetch = state.get("last_fetch_time")
        if not last_fetch:
            return None

        try:
            if isinstance(last_fetch, str):
                return datetime.fromisoformat(last_fetch.replace("Z", "+00:00"))
            elif isinstance(last_fetch, (int, float)):
                return datetime.fromtimestamp(last_fetch, tz=timezone.utc)
            return None
        except (ValueError, TypeError):
            logger.warning(f"Invalid last_fetch_time in state: {last_fetch}")
            return None

    def set_last_fetch_time(self, timestamp: datetime) -> None:
        """
        Set the last fetch timestamp.

        Args:
            timestamp: Datetime of last fetch
        """
        state = self.load()
        state["last_fetch_time"] = timestamp.isoformat()
        self.save(state)

    def update_source_stats(self, source: str, articles_count: int) -> None:
        """
        Update article count statistics for a source.

        Args:
            source: Source name
            articles_count: Number of articles fetched
        """
        state = self.load()
        if "source_stats" not in state:
            state["source_stats"] = {}

        stats = state["source_stats"].get(source, {})
        stats["total_articles"] = stats.get("total_articles", 0) + articles_count
        stats["last_fetch"] = datetime.now(timezone.utc).isoformat()
        stats["fetch_count"] = stats.get("fetch_count", 0) + 1

        state["source_stats"][source] = stats
        self.save(state)

    def get_source_stats(self, source: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific source.

        Args:
            source: Source name

        Returns:
            Dictionary with source statistics, or None if not found
        """
        state = self.load()
        return state.get("source_stats", {}).get(source)

    def clear(self) -> None:
        """Clear all state information."""
        if self.state_file.exists():
            self.state_file.unlink()
            logger.info(f"Cleared state file: {self.state_file}")
