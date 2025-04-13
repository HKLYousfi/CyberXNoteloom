# CyberXNoteloom: MIDI-to-Multi-Format Audio Converter

**Under Development – Do Not Distribute Unauthorized Copies**

---

## Overview

CyberXNoteloom is a fully optimized, professional-grade digital piano solution that converts MIDI files or musical notation (from TXT or DOCX files) into high-quality audio formats (WAV, FLAC, MP3, AAC, WMA) without any external instruments. The project uses an advanced synthesis engine with dynamic ADSR envelopes, a robust signal processing pipeline featuring polyphase oversampling, high-end FIR filtering, soft-knee dynamics, and TPDF dithering, combined with state-of-the-art DSP effects (composite reverb and multi-band EQ) and superior encoding techniques leveraging SoundFile and FFmpeg.

---

## Mission Statement

This project was created for a noble cause—to empower those passionate about piano but who cannot afford expensive instruments. CyberXNoteloom enables aspiring musicians (including children) to practice and develop their skills by providing a full, software-based digital piano experience.

As a music enthusiast, electromechanical, and marine engineer, I (Haykel Yousfi) believe that music should be accessible to everyone. Your support fosters further innovative projects and encourages building high-quality musical tools.

---

## How a Piano Works

### The Basics
- **Keys & Hammer Mechanism:** When you press a piano key, it triggers a hammer to strike the corresponding strings. The vibration produces the musical sound.
- **Soundboard:** Amplifies the sound created by the vibrating strings.
- **Pedals:** For sustain, softening, and selective note sustain.

### Keyboard Layout
- **White Keys:** Represent natural notes (A, B, C, D, E, F, G).
- **Black Keys:** Represent sharps/flats grouped in twos and threes.
- **Middle C (C4):** A central reference point.
- **Octaves & Chords:** Understand the grouping and how scales/chords (e.g., major and minor) are built.

---

## Features

- **Realistic Synthesis Engine:**  
  - Uses sine-wave oscillators enriched with harmonics.
  - Applies ADSR envelopes for natural attack, decay, sustain, and release.
  - Supports dynamic parameters based on the musical style, transposition, and piano type.

- **Robust Note Parsing:**  
  - Parses standard MIDI files.
  - Converts musical notation from TXT or DOCX files into MIDI events (e.g., "[G3A#3]| [G3A#3] ...").

- **Advanced DSP Processing:**  
  - Oversampling with polyphase resampling.
  - Kaiser-windowed FIR filtering for anti-aliasing.
  - Soft-knee dynamics processing and TPDF dithering for pristine audio.
  - Advanced reverb (composite of early reflections and long tail) and multi-band EQ.

- **Multi-Format Encoding:**  
  - Exports audio using SoundFile for WAV and FLAC.
  - Leverages FFmpeg for MP3, AAC, and WMA conversion.
  
- **Additional Parameters:**  
  - Style (e.g., "Pop")
  - Target Length (formatted as "MM:SS")
  - Transposition (e.g., shift notes by semitones)
  - Tempo (BPM override)
  - Piano Type (e.g., "CLASSICAL PIANO", "GRAND CLASSICAL PIANO", etc.)

- **Modular Design & Testing:**  
  - Clear separation into modules with unit tests for reliability.

---

## Installation

### Prerequisites

- Python 3.6 or higher
- FFmpeg must be installed and available in your PATH.

### Python Dependencies

Install the required packages using:

```bash
pip install -r requirements.txt
