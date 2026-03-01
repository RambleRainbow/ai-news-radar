"""
Tests for logger utilities.
"""

import logging

from skill.utils.logger import setup_logger


class TestSetupLogger:
    """Test logger setup."""

    def test_setup_logger_basic(self):
        """Test basic logger setup."""
        logger = setup_logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO

    def test_setup_logger_verbose(self):
        """Test logger with verbose mode."""
        logger = setup_logger("test_logger", verbose=True)
        assert logger.level == logging.DEBUG

    def test_setup_logger_custom_level(self):
        """Test logger with custom level."""
        logger = setup_logger("test_logger", level=logging.WARNING)
        assert logger.level == logging.WARNING

    def test_setup_logger_with_file(self, temp_dir):
        """Test logger with file output."""
        log_file = temp_dir / "test.log"
        logger = setup_logger("test_logger", log_file=log_file)

        # Check that handlers are added
        assert len(logger.handlers) == 2  # Console + File

    def test_setup_logger_clears_handlers(self):
        """Test that setup clears existing handlers."""
        logger1 = setup_logger("test_logger")
        handler_count1 = len(logger1.handlers)

        # Setup again should clear and add new handlers
        logger2 = setup_logger("test_logger")
        assert len(logger2.handlers) == handler_count1

    def test_setup_logger_log_message(self, caplog):
        """Test that logger can log messages."""
        logger = setup_logger("test_logger")

        with caplog.at_level(logging.INFO):
            logger.info("Test message")

        assert len(caplog.records) > 0
        assert caplog.records[-1].message == "Test message"

    def test_setup_logger_console_format(self, caplog):
        """Test console log format."""
        logger = setup_logger("test_logger")

        with caplog.at_level(logging.INFO):
            logger.info("Test")

        # Check that timestamp is in the log
        record = caplog.records[-1]
        assert hasattr(record, "asctime")

    def test_setup_logger_default_name(self):
        """Test default logger name."""
        logger = setup_logger()
        assert logger.name == "ai_news_radar"
