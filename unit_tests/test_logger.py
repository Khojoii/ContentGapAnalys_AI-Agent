import os
import logging
from logger import get_logger

def test_logger_creates_log_file(tmp_path):
    # Reset logging config to avoid conflicts
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    log_file = tmp_path / "test.log"
    logging.basicConfig(filename=log_file, level=logging.INFO, encoding="utf-8")

    logger = get_logger()
    test_message = "This is a test log entry"
    logger.info(test_message)

    # Flush and close handlers to ensure the message is written
    for handler in logger.handlers:
        handler.flush()

    # Verify the log file was created
    assert log_file.exists(), "Log file should be created"

    # Verify the message is written in the file
    content = log_file.read_text(encoding="utf-8")
    assert test_message in content, "Log message should appear in the log file"
# === To run the tests, navigate to the "tests" directory or specify a test file, then run: pytest ===