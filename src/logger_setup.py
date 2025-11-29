#!/usr/bin/env python3
"""
Logging Configuration Module

Provides centralized logging configuration for the internship sync pipeline.
This module sets up consistent logging format and handlers across all
components of the application.

Features:
- Standardized log format with timestamp, level, module name, and message
- Console output with proper formatting
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Singleton pattern to prevent duplicate handlers
- UTF-8 compatible output for international characters

Log Format:
    YYYY-MM-DD HH:MM:SS,mmm | LEVEL   | module_name | message
    
Example:
    2025-11-29 10:30:45,123 | INFO    | main | Pipeline started
    2025-11-29 10:30:46,456 | WARNING | jobspy | Rate limit hit
    
Usage:
    from src.logger_setup import get_logger
    logger = get_logger("my_module", "DEBUG")
    logger.info("This is an info message")
    
Supported Log Levels:
- DEBUG: Detailed diagnostic information
- INFO: General operational messages
- WARNING: Warning messages for non-critical issues
- ERROR: Error messages for recoverable problems
- CRITICAL: Critical error messages for severe problems

Author: El Moujahid Marouane
Version: 1.0
"""

import logging
import sys

def get_logger(name=__name__, level="INFO"):
    level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger