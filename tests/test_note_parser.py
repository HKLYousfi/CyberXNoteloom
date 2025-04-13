#!/usr/bin/env python3
"""
tests/test_note_parser.py
-------------------------
Unit tests for the NoteParser module.
Verifies that musical notation is correctly converted into MIDI events.
"""

import unittest
from noteloom.note_parser import NoteParser

class TestNoteParser(unittest.TestCase):
    def test_single_note(self):
        notation = "C4"
        parser = NoteParser(notation, tempo=120)
        events = parser.parse()
        # Expect one note_on and one note_off event
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['type'], 'note_on')
        self.assertEqual(events[1]['type'], 'note_off')

    def test_chord_parsing(self):
        # Test chord notation inside square brackets
        notation = "[C4E4G4]"
        parser = NoteParser(notation, tempo=120)
        events = parser.parse()
        # Chord should yield 3 note_on events and 3 note_off events, total 6 events
        self.assertEqual(len(events), 6)
        # Verify that the notes in the chord are as expected (C4, E4, G4 -> MIDI 60, 64, 67)
        midi_notes = sorted([event['note'] for event in events if event['type'] == 'note_on'])
        self.assertEqual(midi_notes, [60, 64, 67])

    def test_multiple_tokens(self):
        # Test multiple tokens separated by whitespace.
        notation = "C4 D4 E4"
        parser = NoteParser(notation, tempo=120)
        events = parser.parse()
        # 3 tokens x 2 events each = 6 events
        self.assertEqual(len(events), 6)

if __name__ == '__main__':
    unittest.main()
