"""
CyberXNoteloom Package

This package includes all modules necessary for a fully optimized, professional-grade
MIDI-to-Multi-Format Audio Converter with advanced synthesis, DSP effects, and musical notation support.

Modules:
  - converter: Main conversion flow (MIDI/notation → synthesis → processing → encoding)
  - parser: MIDI file parsing.
  - sanitizer: Validates MIDI event consistency.
  - synthesizer: Advanced synthesis engine with ADSR envelopes and dynamic note rendering.
  - effects: Advanced DSP effects (composite reverb, multi-band EQ).
  - file_loader: Loads musical notation from TXT or DOCX files.
  - note_parser: Parses musical notation strings into MIDI events.
  - encoder: High-quality multi-format audio encoders (WAV, FLAC, MP3, AAC, WMA).
  - pipeline: High-performance audio processing pipeline.
  - utils: Utility functions (e.g., directory handling, filename sanitization, donation link).
  - integrity: Code integrity checking.
"""

from .converter import UniversalConverter
from .parser import MidiParser
from .sanitizer import MidiSanitizer
from .synthesizer import HybridSynthesizer, ResonanceModel, generate_pedal_noise, apply_adsr_envelope
from .effects import apply_advanced_reverb, apply_advanced_eq
from .file_loader import FileLoader
from .note_parser import NoteParser
from .encoder import WavEncoder, FlacEncoder, Mp3Encoder, AacEncoder, WmaEncoder
from .pipeline import AudioPipeline, Oversampler, AntiAliasFilter, DynamicsProcessor, Normalizer
from .utils import ensure_dir, sanitize_filename, get_paypal_donation_link
from .integrity import check_code_integrity
