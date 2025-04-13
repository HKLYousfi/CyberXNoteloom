#!/usr/bin/env python3
"""
main.py
-------
CLI for CyberXNoteloom.
Usage:
    python -m cli.main --input path/to/file.mid --output output_base
    (For musical notation files, support .txt or .docx is provided.)
"""

import sys
import argparse
import logging
from noteloom.converter import UniversalConverter
from noteloom.file_loader import FileLoader
from noteloom.note_parser import NoteParser

logger = logging.getLogger(__name__)

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,  # Set to INFO or WARNING for less verbosity
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    parser = argparse.ArgumentParser(description="CyberXNoteloom: Notation/MIDI-to-Audio Converter")
    parser.add_argument("--input", required=True, help="Path to input file (.mid, .txt, or .docx)")
    parser.add_argument("--output", required=False, help="Output base filename (e.g., output_base)", default="output")
    args = parser.parse_args()

    input_path = args.input
    output_base = args.output

    # Determine file type from extension
    ext = input_path.split(".")[-1].lower()
    if ext in ["txt", "docx"]:
        logger.info("Loading musical notation file: %s", input_path)
        loader = FileLoader(input_path)
        notation = loader.load()
        logger.info("Parsing musical notation...")
        note_parser = NoteParser(notation, tempo=120)
        events = note_parser.parse()
        converter = UniversalConverter(events=events, sample_rate=44100, channels=2, default_duration=1.0)
    elif ext == "mid":
        logger.info("Loading MIDI file: %s", input_path)
        converter = UniversalConverter(midi_path=input_path, sample_rate=44100, channels=2, default_duration=1.0)
    else:
        logger.error("Unsupported input file type: %s", ext)
        sys.exit(f"Unsupported file type: {ext}")

    # Define output formats – you may adjust as required.
    formats = ['WAV', 'FLAC', 'MP3', 'AAC', 'WMA']
    results = converter.convert(formats)

    # Rename output files based on output_base name
    for fmt, fname in results.items():
        if fmt != "Certification":
            new_fname = f"{output_base}.{fmt.lower()}"
            try:
                # Rename file if different
                if fname != new_fname:
                    import os
                    os.rename(fname, new_fname)
                    results[fmt] = new_fname
                    logger.info("Renamed %s to %s", fname, new_fname)
            except Exception as e:
                logger.exception("Error renaming file: %s", e)
    for fmt, fname in results.items():
        print(f"{fmt} output: {fname}")

if __name__ == '__main__':
    main()
