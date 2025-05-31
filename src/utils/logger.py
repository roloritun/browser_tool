import logging
import os
import sys


# Set up logging
class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'CRITICAL': '\033[95m', # Magenta
        'RESET': '\033[0m',     # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        return f"{color}{log_message}{reset}"


# Create logger
logger = logging.getLogger("browser_tools")
logger.setLevel(logging.WARNING)

# Avoid adding handlers multiple times
if not logger.handlers:
    # Create console handler with colored formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    
    # Optionally add file handler if LOG_FILE env var is set
    log_file = os.environ.get("LOG_FILE")
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)

# Function to set log level from environment variable
def set_log_level_from_env(env_var: str = "LOG_LEVEL", default: str = "INFO") -> None:
    """Set the log level from an environment variable.
    
    Args:
        env_var (str, optional): The environment variable name. Defaults to "LOG_LEVEL".
        default (str, optional): The default log level. Defaults to "INFO".
    """
    log_level = os.environ.get(env_var, default).upper()
    numeric_level = getattr(logging, log_level, None)
    
    if not isinstance(numeric_level, int):
        logger.warning(f"Invalid log level: {log_level}. Using INFO instead.")
        numeric_level = logging.INFO
    
    logger.setLevel(numeric_level)

# Set log level from environment
set_log_level_from_env()
