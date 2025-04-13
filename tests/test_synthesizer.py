#!/usr/bin/env python3
"""
tests/test_synthesizer.py
-------------------------
Unit tests for the HybridSynthesizer module in CyberXNoteloom.
Verifies that synthesized notes have the expected length, envelope behavior,
and overall properties (e.g., two-channel output, normalized amplitude).
"""

import unittest
import numpy as np
from noteloom.synthesizer import HybridSynthesizer, apply_adsr_envelope

class TestSynthesizer(unittest.TestCase):
    def test_synthesize_single_note(self):
        # Create a synthesizer instance with a 2-second duration
        synth = HybridSynthesizer(sample_rate=48000, channels=2, duration=2.0, mode='adsr')
        # Create a simple event: note_on at time 0 and note_off at 0.5 seconds
        events = [
            {'type': 'note_on', 'note': 60, 'velocity': 100, 'time': 0, 'channel': 0},
            {'type': 'note_off', 'note': 60, 'velocity': 0, 'time': int(0.5 * 1e6), 'channel': 0}
        ]
        # Render the audio using the synthesizer
        audio = synth.render(events)
        # Check the audio array shape: should be (num_samples, 2) for stereo output.
        self.assertEqual(len(audio.shape), 2)
        self.assertEqual(audio.shape[1], 2)
        # Ensure the synthesized signal is in float32.
        self.assertEqual(audio.dtype, np.float32)
        # Ensure the maximum absolute amplitude is less than or equal to 1 (normalized).
        self.assertLessEqual(np.max(np.abs(audio)), 1.0 + 1e-3)

    def test_adsr_envelope_length(self):
        # Test the ADSR envelope generator directly.
        duration_sec = 0.5
        sample_rate = 48000
        envelope = apply_adsr_envelope(duration_sec, sample_rate)
        expected_samples = int(duration_sec * sample_rate)
        self.assertEqual(envelope.shape[0], expected_samples)
        # Check that the envelope starts at 0 and ends at 0.
        self.assertAlmostEqual(envelope[0], 0.0, places=4)
        self.assertAlmostEqual(envelope[-1], 0.0, places=4)

if __name__ == '__main__':
    unittest.main()
