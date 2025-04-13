#!/usr/bin/env python3
"""
sanitizer.py
------------
Validates and sanitizes MIDI events to ensure proper note-on/note-off pairing.
Logs warnings for orphan note-off events.
"""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class MidiSanitizer:
    def __init__(self, events):
        self.events = events

    def validate_note_events(self):
        open_notes = defaultdict(list)
        sanitized = []

        for event in self.events:
            if event['type'] == 'note_on':
                open_notes[event['channel']].append(event['note'])
                sanitized.append(event)
            elif event['type'] == 'note_off':
                if event['note'] in open_notes[event['channel']]:
                    open_notes[event['channel']].remove(event['note'])
                    sanitized.append(event)
                else:
                    logger.warning("Orphan note_off detected: %s", event)
            else:
                sanitized.append(event)
        logger.info("Sanitized events: %d events validated.", len(sanitized))
        return sanitized
