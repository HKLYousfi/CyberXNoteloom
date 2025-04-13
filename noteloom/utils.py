#!/usr/bin/env python3
"""
utils.py
--------
Utility functions for CyberXNoteloom.
Includes functions for ensuring directory existence and sanitizing filenames.
"""

import os
import logging

logger = logging.getLogger(__name__)

def ensure_dir(path):
    """
    Ensures that a directory exists; creates it if necessary.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            logger.info("Directory created: %s", path)
        except Exception as e:
            logger.exception("Failed to create directory %s: %s", path, e)
            raise

def sanitize_filename(name):
    """
    Sanitizes a string to make a safe filename.
    """
    valid_chars = "-_.() %s%s" % (os.path.sep, os.path.altsep or "")
    sanitized = ''.join(c for c in name if c.isalnum() or c in valid_chars)
    logger.debug("Sanitized filename: %s", sanitized)
    return sanitized.strip()

def get_paypal_donation_link():
    """
    Returns a mailto link for PayPal donations.
    """
    return "mailto:cyberxtech.haykel@outlook.com"
