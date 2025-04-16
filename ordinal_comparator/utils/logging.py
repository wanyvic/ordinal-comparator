"""
Logging configuration for the Ordinal Comparator application.
"""

import logging
import logging.config
import os
import sys
from typing import Optional, Dict, Any


def setup_logging(log_file: Optional[str] = None, log_level: str = 'INFO') -> None:
    """
    Configure the application logging system.
    
    Args:
        log_file: Optional path to a log file. If provided, logs will be written to this file
                  in addition to the console.
        log_level: The minimum log level to record (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Define logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '%(asctime)s [%(levelname)s] %(message)s',
                'datefmt': '%H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            '': {  # Root logger
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True,
            },
            'urllib3': {  # Suppress noisy libraries
                'level': 'WARNING',
            },
            'requests': {
                'level': 'WARNING',
            },
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        try:
            # Ensure the directory exists
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            config['handlers']['file'] = {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'formatter': 'detailed',
                'filename': log_file,
                'encoding': 'utf-8',
            }
            config['loggers']['']['handlers'].append('file')
        except (IOError, OSError) as e:
            print(f"Warning: Could not set up log file: {e}", file=sys.stderr)
    
    # Set the root logger level from command line argument
    try:
        numeric_level = getattr(logging, log_level.upper())
        config['loggers']['']['level'] = numeric_level
    except (AttributeError, TypeError):
        print(f"Warning: Invalid log level: {log_level}, using INFO", file=sys.stderr)
        config['loggers']['']['level'] = logging.INFO
    
    # Apply configuration
    try:
        logging.config.dictConfig(config)
    except (ValueError, TypeError, AttributeError) as e:
        # Fall back to basic configuration if dictConfig fails
        print(f"Warning: Could not configure logging: {e}", file=sys.stderr)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        ) 