import unittest
from noteloom.parser import MidiParser

class TestMidiParser(unittest.TestCase):
    def test_parse_midi_file(self):
        # Use a known small MIDI file for testing; please update the path as needed.
        midi_file = "tests/sample.mid"
        parser = MidiParser(midi_file)
        events = parser.parse()
        # Ensure events are returned and are in increasing order of time.
        self.assertGreater(len(events), 0)
        times = [event['time'] for event in events]
        self.assertEqual(times, sorted(times))

if __name__ == '__main__':
    unittest.main()
