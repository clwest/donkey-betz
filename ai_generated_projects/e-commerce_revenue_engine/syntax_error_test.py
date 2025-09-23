#!/usr/bin/env python3
"""
Test syntax error auto-fix
"""

print("Testing syntax error fix")

# Intentional syntax error - missing colon
if True:  # Fixed by adding a colon
    print("This should be fixed")

print("End of test")

# Example of using a logger
import logging

# Configure the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("This is a log message.")