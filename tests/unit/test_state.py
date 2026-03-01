"""
Tests for state management module.
"""

from datetime import datetime, timezone, timedelta

from skill.state import State


class TestState:
    """Test State functionality."""

    def test_init(self, temp_dir):
        """Test state initialization."""
        state_file = temp_dir / "state.json"
        state = State(state_file)
        assert state.state_file == state_file
        assert state_file.parent.exists()

    def test_save_and_load(self, temp_dir):
        """Test saving and loading state."""
        state_file = temp_dir / "state.json"
        state = State(state_file)

        test_state = {"key": "value", "number": 42}
        state.save(test_state)

        loaded = state.load()
        assert loaded == test_state

    def test_load_nonexistent(self, temp_dir):
        """Test loading from nonexistent state file."""
        state_file = temp_dir / "nonexistent.json"
        state = State(state_file)

        loaded = state.load()
        assert loaded == {}

    def test_get_last_fetch_time(self, temp_dir):
        """Test getting last fetch time."""
        state_file = temp_dir / "state.json"
        state = State(state_file)

        # Set last fetch time
        now = datetime.now(timezone.utc)
        state.set_last_fetch_time(now)

        # Get it back
        retrieved = state.get_last_fetch_time()
        assert retrieved is not None
        assert retrieved.isoformat() == now.isoformat()

    def test_get_last_fetch_time_none(self, temp_dir):
        """Test getting last fetch time when not set."""
        state_file = temp_dir / "state.json"
        state = State(state_file)

        retrieved = state.get_last_fetch_time()
        assert retrieved is None

    def test_update_source_stats(self, temp_dir):
        """Test updating source statistics."""
        state_file = temp_dir / "state.json"
        state = State(state_file)

        # Update stats for source
        state.update_source_stats("TechNews", 5)
        state.update_source_stats("TechNews", 3)
        state.update_source_stats("AI Weekly", 10)

        stats_tech = state.get_source_stats("TechNews")
        assert stats_tech["total_articles"] == 8
        assert stats_tech["fetch_count"] == 2

        stats_ai = state.get_source_stats("AI Weekly")
        assert stats_ai["total_articles"] == 10
        assert stats_ai["fetch_count"] == 1

    def test_get_source_stats_none(self, temp_dir):
        """Test getting stats for nonexistent source."""
        state_file = temp_dir / "state.json"
        state = State(state_file)

        stats = state.get_source_stats("nonexistent")
        assert stats is None

    def test_clear(self, temp_dir):
        """Test clearing state."""
        state_file = temp_dir / "state.json"
        state = State(state_file)

        # Set some state
        state.set_last_fetch_time(datetime.now(timezone.utc))
        state.update_source_stats("Test", 5)

        # Clear it
        state.clear()

        # Verify it's cleared
        assert not state_file.exists()
        assert state.load() == {}
