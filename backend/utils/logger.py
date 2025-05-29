import logging
import os
from datetime import datetime

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger with both file and console handlers.
    
    Args:
        name (str): Name of the logger
        log_file (str, optional): Path to log file. If None, logs to 'logs/{name}_{date}.log'
        level (int, optional): Logging level. Defaults to logging.INFO
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file is None:
        os.makedirs('logs', exist_ok=True)
        date_str = datetime.now().strftime('%Y%m%d')
        log_file = f'logs/{name}_{date_str}.log'
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create specific loggers for different components
resume_logger = setup_logger('resume_parser')
job_scraper_logger = setup_logger('job_scraper') 