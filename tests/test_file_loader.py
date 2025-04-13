#!/usr/bin/env python3
"""
tests/test_file_loader.py
-------------------------
Unit tests for the FileLoader module in CyberXNoteloom.
Tests both .txt and .docx file loading capabilities.
"""

import os
import unittest
from noteloom.file_loader import FileLoader

class TestFileLoader(unittest.TestCase):
    def setUp(self):
        # Prepare small sample text and DOCX files for testing.
        self.txt_path = "tests/sample_notation.txt"
        self.docx_path = "tests/sample_notation.docx"
        sample_content = "[C4E4G4]\nD4 F4 A4"
        # Write sample TXT file.
        with open(self.txt_path, "w", encoding="utf-8") as f:
            f.write(sample_content)
        # Create a sample DOCX file using python-docx.
        from docx import Document
        doc = Document()
        doc.add_paragraph(sample_content)
        doc.save(self.docx_path)

    def tearDown(self):
        # Clean up sample files.
        if os.path.exists(self.txt_path):
            os.remove(self.txt_path)
        if os.path.exists(self.docx_path):
            os.remove(self.docx_path)

    def test_load_txt(self):
        loader = FileLoader(self.txt_path)
        content = loader.load()
        self.assertIn("[C4E4G4]", content)
        self.assertIn("D4", content)

    def test_load_docx(self):
        loader = FileLoader(self.docx_path)
        content = loader.load()
        self.assertIn("[C4E4G4]", content)
        self.assertIn("F4", content)

if __name__ == '__main__':
    unittest.main()
