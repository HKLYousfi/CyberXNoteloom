#!/usr/bin/env python3
"""
note_parser.py
--------------
This module parses musical notation strings into MIDI events.
It converts note symbols (e.g., C4, D#5) into MIDI note numbers, and creates note_on/note_off events.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Mapping for note names to semitone offsets
NOTE_OFFSETS = {
    'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
}

class NoteParser:
    def __init__(self, notation_str, tempo=120):
        """
        notation_str: String containing musical notation.
        tempo: Beats per minute (affects note durations).
        """
        self.notation_str = notation_str
        self.tempo = tempo  # default tempo (BPM)

    def parse(self):
        """
        Converts notation into MIDI events.
        Uses a simple approach: each token corresponds to a note (or chord if inside brackets)
        and is assigned a default duration equal to a quarter note.
        """
        events = []
        time = 0.0  # time in seconds
        beat_duration = 60.0 / self.tempo  # quarter note duration (can be refined)
        default_duration = beat_duration  # for simplicity

        # Regular expression to match either chord groups "[...]" or individual note tokens (e.g., G3, A#3)
        tokens = re.findall(r'\[.*?\]|[A-Ga-g][#b]?\d', self.notation_str)
        logger.info("Found %d tokens in notation", len(tokens))

        for token in tokens:
            if token.startswith('[') and token.endswith(']'):
                # Remove brackets and split the chord into note strings
                chord_str = token[1:-1]
                notes = re.findall(r'[A-Ga-g][#b]?\d', chord_str)
            else:
                notes = [token]

            for note in notes:
                midi_note = self._note_to_midi(note)
                # Create a note_on event
                events.append({
                    'type': 'note_on',
                    'note': midi_note,
                    'velocity': 100,
                    'time': int(time * 1e6),
                    'channel': 0
                })
                # Create a corresponding note_off event after default_duration seconds
                events.append({
                    'type': 'note_off',
                    'note': midi_note,
                    'velocity': 0,
                    'time': int((time + default_duration) * 1e6),
                    'channel': 0
                })
            time += default_duration
        logger.info("Parsed %d MIDI events from notation", len(events))
        return events

    def _note_to_midi(self, note_str):
        """
        Converts a note string (e.g., "C4", "D#5") to its MIDI note number.
        """
        match = re.match(r'([A-Ga-g])([#b]?)(\d)', note_str)
        if not match:
            logger.error("Invalid note format: %s", note_str)
            raise ValueError(f"Invalid note format: {note_str}")
        note, accidental, octave = match.groups()
        note = note.upper() + accidental
        semitone = NOTE_OFFSETS.get(note)
        if semitone is None:
            logger.error("Unknown note: %s", note)
            raise ValueError(f"Unknown note: {note}")
        midi_note = (int(octave) + 1) * 12 + semitone
        return midi_note
