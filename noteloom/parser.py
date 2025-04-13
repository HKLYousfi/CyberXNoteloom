#!/usr/bin/env python3
"""
parser.py
---------
Parses a MIDI file into a list of event dictionaries with microsecond timing.
Handles tempo changes, note-on/off events, sustain (control change 64), and pitch bends.
"""

import logging
import mido

logger = logging.getLogger(__name__)

class MidiParser:
    def __init__(self, midi_path):
        self.midi_path = midi_path
        self.events = []
        self.tempo = 500000  # Default tempo: 120 BPM
        self.current_time = 0

    def _handle_pitch_bend(self, msg):
        normalized_bend = (msg.pitch + 8192) / 16384.0
        self.events.append({
            'time': self.current_time,
            'type': 'pitch_bend',
            'value': normalized_bend,
            'channel': msg.channel
        })
        logger.debug("Pitch bend at %d µs: %.3f", self.current_time, normalized_bend)

    def parse(self):
        try:
            mid = mido.MidiFile(self.midi_path)
            logger.info("Opened MIDI file: %s", self.midi_path)
        except Exception as e:
            logger.exception("Error reading MIDI file: %s", e)
            raise Exception(f"Error reading MIDI file: {e}")

        for track in mid.tracks:
            for msg in track:
                delta = mido.tick2second(msg.time, mid.ticks_per_beat, self.tempo) * 1e6
                self.current_time += delta
                if msg.type == 'set_tempo':
                    self.tempo = msg.tempo
                    self.events.append({'time': self.current_time, 'type': 'tempo', 'value': msg.tempo})
                    logger.debug("Tempo change at %d µs: %d", self.current_time, msg.tempo)
                elif msg.type in ['note_on', 'note_off']:
                    velocity = max(0, min(127, msg.velocity))
                    event_type = 'note_off' if (msg.type == 'note_on' and velocity == 0) else msg.type
                    self.events.append({
                        'time': self.current_time,
                        'type': event_type,
                        'note': msg.note,
                        'velocity': velocity,
                        'channel': msg.channel
                    })
                    logger.debug("Note event: %s note %d, velocity %d at %d µs", event_type, msg.note, velocity, self.current_time)
                elif msg.type == 'control_change' and msg.control == 64:
                    self.events.append({
                        'time': self.current_time,
                        'type': 'sustain',
                        'value': msg.value,
                        'channel': msg.channel
                    })
                    logger.debug("Sustain event: value %d at %d µs", msg.value, self.current_time)
                elif msg.type == 'pitchwheel':
                    self._handle_pitch_bend(msg)
        self.events.sort(key=lambda x: x['time'])
        logger.info("Parsed %d MIDI events.", len(self.events))
        return self.events
