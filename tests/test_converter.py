#!/usr/bin/env python3
"""
tests/test_converter.py
-----------------------
Unit tests for the UniversalConverter module in CyberXNoteloom.
Verifies that the converter produces output files for all requested formats,
and that these files exist.
"""

import unittest
import os
from noteloom.converter import UniversalConverter

class TestConverter(unittest.TestCase):
    def test_conversion_outputs(self):
        # Specify a known MIDI file for testing; adjust the path as needed.
        midi_file = "tests/sample.mid"
        converter = UniversalConverter(midi_path=midi_file, sample_rate=44100, channels=2, default_duration=1.0)
        output_formats = ['WAV', 'FLAC', 'MP3', 'AAC', 'WMA']
        results = converter.convert(output_formats)
        
        # Check that each requested format has an output filename and that the file exists.
        for fmt in output_formats:
            self.assertIn(fmt, results)
            output_path = results[fmt]
            self.assertTrue(os.path.exists(output_path), f"File for {fmt} does not exist.")
        
        # Optionally clean up generated test files.
        for fmt in output_formats:
            try:
                os.remove(results[fmt])
            except Exception:
                pass

if __name__ == '__main__':
    unittest.main()
