from loguru import logger
from datetime import datetime
import time
import sys
import functools

class LoggerManager:
    """
    Manages structured logging configuration using Loguru.
    Logs are filtered by level and rotated to maintain system performance.
    """

    @classmethod
    def setup_logger(cls):
        log_folder = "logs/"
        file_prefix = "system-"
        rotation = "10 MB"
        retention = "30 days"
        encoding = "utf-8"
        
        # Log format includes metadata for easier debugging in multi-threaded/process environments
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
            "|<level>{level: <7}</level>"
            "|<cyan>{name}</cyan>:<cyan>{function}</cyan>:<yellow>{line}</yellow>"
            "|<level>{message}</level>"
        )

        # Clear existing default loggers to avoid duplicates
        logger.remove()

        # Define logging levels for file storage
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            logger.add(
                f"{log_folder}{file_prefix}{level.lower()}.log",
                level=level,
                format=log_format,
                rotation=rotation,
                retention=retention,
                encoding=encoding,
                filter=lambda record, lvl=level: record["level"].no >= logger.level(lvl).no,
                backtrace=True,
                diagnose=True,
                colorize=False
            )

        # Add console output for critical issues
        logger.add(
            sys.stderr,
            level="CRITICAL",
            format=log_format,
            colorize=True
        )

        return logger

# Initialize the logger
logger = LoggerManager.setup_logger()

def time_execution(func):
    """
    Decorator to log the execution time of a function.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info(f"Function [{func.__name__}] executed in {duration:.4f} seconds.")
        return result

    return wrapper