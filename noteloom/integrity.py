#!/usr/bin/env python3
"""
integrity.py
------------
This module performs a robust code integrity check using SHA‑256.
If the hash of the file does not match the expected value,
the process will exit with an error. Update EXPECTED_HASH after intentional modifications.
"""

import os
import sys
import hashlib
import logging

logger = logging.getLogger(__name__)

def check_code_integrity(expected_hash):
    """
    Computes the SHA-256 hash of this file and compares it with expected_hash.
    
    Parameters:
      expected_hash (str): The reference SHA-256 hash string.
      
    Exits the program if the hash does not match.
    """
    try:
        current_path = os.path.abspath(__file__)
        with open(current_path, "rb") as f:
            file_data = f.read()
        current_hash = hashlib.sha256(file_data).hexdigest()
        if current_hash != expected_hash:
            logger.error("Integrity check failed for %s! Expected: %s, Found: %s",
                         current_path, expected_hash, current_hash)
            sys.exit("Integrity verification failed!")
        else:
            logger.debug("Integrity check passed for %s", current_path)
    except Exception as e:
        logger.exception("Integrity check error: %s", e)
        sys.exit(f"Integrity check error: {e}")
