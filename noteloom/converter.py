#!/usr/bin/env python3
"""
converter.py
-------------
UniversalConverter integrates:
  - MIDI parsing and sanitization (or accepts external note events),
  - Advanced synthesis with proper note durations and ADSR envelopes,
  - A high-performance audio processing pipeline (including oversampling, high-quality FIR filtering, soft-knee dynamics, and TPDF dithering),
  - Advanced DSP effects (composite reverb and multi-band EQ),
  - Professional multi-format encoding into WAV, FLAC, MP3, AAC, and WMA via native libraries and FFmpeg,
  - Additional parameters such as style, target length, transposition, tempo, and piano type.

Certification: Audio conversion certified by Haykel Yousfi.
Mission: Deliver a fully self-contained digital piano experience of the highest quality.
"""

import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy.signal import resample_poly

from .parser import MidiParser
from .sanitizer import MidiSanitizer
from .synthesizer import HybridSynthesizer
from .encoder import WavEncoder, FlacEncoder, Mp3Encoder, AacEncoder, WmaEncoder
from .pipeline import AudioPipeline, Oversampler, AntiAliasFilter, DynamicsProcessor, Normalizer
from .effects import apply_advanced_reverb, apply_advanced_eq

logger = logging.getLogger(__name__)

def parse_target_length(target_length_str):
    """Converts a time string in MM:SS format to seconds."""
    try:
        minutes, seconds = target_length_str.strip().split(":")
        return int(minutes) * 60 + int(seconds)
    except Exception as e:
        logger.error("Invalid target length format. Use MM:SS, e.g., 02:51")
        raise ValueError("Invalid target length format. Use MM:SS") from e

class UniversalConverter:
    def __init__(self, midi_path=None, events=None, sample_rate=44100, channels=2, default_duration=1.0,
                 style="Pop", target_length="00:00", transposition=0, tempo=120, piano_type="CLASSICAL PIANO"):
        """
        Initializes the UniversalConverter.
        
        Parameters:
          - midi_path: Path to a MIDI file (if events not provided)
          - events: List of pre-parsed note events (each a dict)
          - sample_rate: Sampling rate in Hz
          - channels: Number of audio channels (e.g., 2 for stereo)
          - default_duration: Fallback duration (in seconds) if no events are found.
          - style: Musical style (affects synthesis parameters)
          - target_length: Desired output length in "MM:SS" format. If "00:00", no time-stretching is applied.
          - transposition: Semitone shift applied to all notes.
          - tempo: Beats per minute (overrides MIDI tempo events)
          - piano_type: The type of piano (e.g., "CLASSICAL PIANO")
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.default_duration = default_duration
        self.bit_depth = 32
        self.style = style
        self.transposition = transposition
        self.tempo = tempo
        self.piano_type = piano_type

        if target_length != "00:00":
            self.target_length_sec = parse_target_length(target_length)
        else:
            self.target_length_sec = None

        if events is not None:
            self.midi_events = events
        elif midi_path is not None:
            raw_events = MidiParser(midi_path).parse()
            self.midi_events = MidiSanitizer(raw_events).validate_note_events()
        else:
            raise ValueError("Either midi_path or events must be provided.")

        # Apply transposition to note events.
        for event in self.midi_events:
            if 'note' in event:
                event['note'] += self.transposition

        # Override tempo events with provided tempo.
        for event in self.midi_events:
            if event['type'] == 'tempo':
                event['value'] = self.tempo

        if self.midi_events:
            last_time = self.midi_events[-1]['time'] / 1e6
            self.duration = max(self.default_duration, last_time + 0.5)
        else:
            self.duration = self.default_duration

        logger.info("UniversalConverter initialized: sample_rate=%d, channels=%d, duration=%.2f s, transposition=%d, tempo=%d, style=%s, piano_type=%s, events=%d",
                    self.sample_rate, self.channels, self.duration, self.transposition, self.tempo, self.style, self.piano_type, len(self.midi_events))

    def _generate_waveform(self):
        """
        Generates raw PCM waveform using HybridSynthesizer.
        Synthesis parameters (ADSR, harmonic mix, etc.) may be adjusted based on style and piano type.
        """
        synth = HybridSynthesizer(sample_rate=self.sample_rate,
                                  channels=self.channels,
                                  duration=self.duration,
                                  mode='adsr')
        logger.info("Synthesizing waveform (style=%s, piano_type=%s)...", self.style, self.piano_type)
        pcm = synth.render(self.midi_events).astype(np.float32)
        logger.debug("Generated waveform shape: %s", pcm.shape)
        return pcm

    def _process_audio(self, pcm):
        """
        Processes the raw PCM using a high-end audio pipeline:
          - Oversampling using polyphase resampling
          - High-quality anti-alias FIR filtering using a Kaiser window
          - Soft-knee dynamics processing for gentle compression
          - Normalization with TPDF dithering
        Then downsamples to original sample rate and applies advanced DSP effects (reverb, EQ).
        """
        pipeline = AudioPipeline([
            Oversampler(factor=8),
            AntiAliasFilter(cutoff=0.45, numtaps=151),
            DynamicsProcessor(threshold=0.9, ratio=10.0),
            Normalizer(dither_amp=1e-5)
        ])
        logger.info("Processing audio through pipeline...")
        processed = pipeline.process(pcm)
        processed = processed[::8]  # Downsample by oversampling factor
        logger.debug("Processed audio shape after downsampling: %s", processed.shape)
        logger.info("Applying advanced DSP effects...")
        processed = apply_advanced_reverb(processed, self.sample_rate)
        processed = apply_advanced_eq(processed, self.sample_rate)
        return processed

    def _encode_format(self, pcm, fmt):
        """
        Encodes the processed PCM into the specified output format.
        """
        encoders = {
            'WAV': WavEncoder(self.bit_depth),
            'FLAC': FlacEncoder(compression=5),
            'MP3': Mp3Encoder(mode='VBR', quality=0),
            'AAC': AacEncoder(profile='LC'),
            'WMA': WmaEncoder(bitrate=192)
        }
        encoder = encoders.get(fmt.upper())
        if not encoder:
            logger.error("Unsupported format requested: %s", fmt)
            raise ValueError(f"Format {fmt} is not supported.")
        filename = f"output.{fmt.lower()}"
        logger.info("Encoding to %s...", fmt)
        return encoder.encode(pcm, filename, self.sample_rate)

    def _time_stretch(self, pcm, target_duration_sec):
        """
        Time-stretches the PCM data to match target_duration_sec.
        This uses a basic resampling method (which does change pitch).
        In a production setup, a pitch-preserving time-stretch algorithm is recommended.
        """
        current_duration = pcm.shape[0] / self.sample_rate
        if current_duration <= 0:
            return pcm
        ratio = target_duration_sec / current_duration
        new_num_samples = int(pcm.shape[0] * ratio)
        from scipy.signal import resample_poly
        stretched = np.zeros((new_num_samples, pcm.shape[1]), dtype=np.float32)
        for ch in range(pcm.shape[1]):
            # Simple resampling; for pitch preservation, use an advanced technique
            stretched[:, ch] = resample_poly(pcm[:, ch], new_num_samples, pcm.shape[0])
        logger.info("Time-stretched audio from %.2f s to %.2f s", current_duration, target_duration_sec)
        return stretched

    def convert(self, output_formats):
        """
        Converts the input (MIDI file or note events) into audio files in the specified formats.
        Applies synthesis, processing, optional time stretching, and encoding.
        Returns a dictionary mapping each format to its output filename.
        """
        pcm = self._generate_waveform()
        processed_pcm = self._process_audio(pcm)

        # If target length is specified, time-stretch the output.
        if self.target_length_sec is not None:
            processed_pcm = self._time_stretch(processed_pcm, self.target_length_sec)

        results = {}

        def encode_format(fmt):
            try:
                file_out = self._encode_format(processed_pcm, fmt)
                results[fmt] = file_out
                logger.info("Encoded %s file: %s", fmt, file_out)
            except Exception as e:
                results[fmt] = f"Error encoding {fmt}: {e}"
                logger.exception("Error encoding %s", fmt)

        with ThreadPoolExecutor(max_workers=len(output_formats)) as executor:
            executor.map(encode_format, output_formats)

        results["Certification"] = "Audio conversion certified by Haykel Yousfi"
        logger.info("Conversion complete with certification.")
        return results

if __name__ == '__main__':
    # Standalone test example (replace the MIDI path with an actual file for testing)
    converter = UniversalConverter(
        midi_path="path/to/sample.mid",
        sample_rate=44100,
        channels=2,
        default_duration=1.0,
        style="Pop",
        target_length="02:51",
        transposition=4,
        tempo=120,
        piano_type="CLASSICAL PIANO"
    )
    output_files = converter.convert(['WAV', 'FLAC', 'MP3', 'AAC', 'WMA'])
    print(output_files)
