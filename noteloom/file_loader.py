#!/usr/bin/env python3
"""
file_loader.py
--------------
This module loads musical notation from .txt and .docx files.
It reads the file content and returns it as a text string.
"""

import os
import logging
from docx import Document

logger = logging.getLogger(__name__)

class FileLoader:
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = None

    def load(self):
        ext = os.path.splitext(self.filepath)[1].lower()
        if ext == '.txt':
            return self._load_txt()
        elif ext == '.docx':
            return self._load_docx()
        else:
            logger.error("Unsupported file format: %s", ext)
            raise ValueError(f"Unsupported file format: {ext}")

    def _load_txt(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.content = f.read()
            logger.info("Text file loaded successfully: %s", self.filepath)
            return self.content
        except Exception as e:
            logger.exception("Failed to load text file: %s", e)
            raise

    def _load_docx(self):
        try:
            doc = Document(self.filepath)
            self.content = "\n".join([para.text for para in doc.paragraphs])
            logger.info("DOCX file loaded successfully: %s", self.filepath)
            return self.content
        except Exception as e:
            logger.exception("Failed to load DOCX file: %s", e)
            raise
