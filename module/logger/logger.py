"""
Module: logger.py
Description: Logging system for the AutoBus.
"""
import logging
import os
from utils.singletonmeta import SingletonMeta


class AutoBusLogger(metaclass=SingletonMeta):
    """
        Singleton Logger class that manages both file and console output.

        Ensures all modules record logs to a unified stream
    """
    def __init__(self, log_name: str = "AutoBusLog.log") -> None:
        """
        Initializes the logger with absolute pathing to prevent directory clutter.
        """
        current_file_path = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))

        log_dir = os.path.join(project_root, "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_path = os.path.join(log_dir, log_name)

        self._logger = logging.getLogger("AutoBus")
        # Critical > Error > Warning > Info > Debug
        # Change if you want to see which assets matching fail
        self._logger.setLevel(logging.INFO)

        # Check if there's existing logs to avoid duplication
        if not self._logger.handlers:
            # 'w' overwrites the file, ‘a’ keeps history.
            file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')

            # Console handler
            console_handler = logging.StreamHandler()

            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # 4. Add handlers to the logger
            self._logger.addHandler(file_handler)
            self._logger.addHandler(console_handler)

    def get_logger(self) -> logging.getLogger():
        """
        Provides access to logger instance
        """
        return self._logger


# Initialize a global instance so we can import it anywhere
logger = AutoBusLogger().get_logger()
