#!/usr/bin/env python3
"""
encoder.py
----------
Provides professional-grade encoding for output formats.
WAV and FLAC are directly written using the SoundFile library for maximum accuracy.
For MP3, AAC, and WMA, a temporary WAV file is created and FFmpeg is used for conversion.
"""

import os
import tempfile
import subprocess
import logging
import soundfile as sf

logger = logging.getLogger(__name__)

class WavEncoder:
    def __init__(self, bit_depth=32):
        self.bit_depth = bit_depth  # Reported for consistency; sf.write uses subtype.

    def encode(self, pcm, filename="output.wav", sample_rate=48000):
        # Write 32-bit float WAV using SoundFile
        sf.write(file=filename, data=pcm, samplerate=sample_rate, subtype='FLOAT')
        logger.info("WAV file saved as %s", filename)
        return filename

class FlacEncoder:
    def __init__(self, compression=5):
        self.compression = compression  # Not used explicitly here.

    def encode(self, pcm, filename="output.flac", sample_rate=48000):
        sf.write(file=filename, data=pcm, samplerate=sample_rate, format='FLAC')
        logger.info("FLAC file saved as %s", filename)
        return filename

class FFmpegEncoderMixin:
    def _convert_with_ffmpeg(self, temp_wav, out_filename, extra_params=None):
        command = ['ffmpeg', '-y', '-i', temp_wav]
        if extra_params:
            command.extend(extra_params)
        command.append(out_filename)
        logger.debug("Running FFmpeg: " + " ".join(command))
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            logger.error("FFmpeg error: %s", result.stderr.decode())
            raise Exception("FFmpeg conversion failed.")
        return out_filename

class Mp3Encoder(FFmpegEncoderMixin):
    def __init__(self, mode='VBR', quality=0):
        self.mode = mode
        self.quality = quality

    def encode(self, pcm, filename="output.mp3", sample_rate=48000):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_wav = tmp.name
        sf.write(file=temp_wav, data=pcm, samplerate=sample_rate, subtype='FLOAT')
        logger.debug("Temporary WAV file created for MP3: %s", temp_wav)
        extra_params = ['-q:a', '2']  # Adjust quality as needed
        out_file = self._convert_with_ffmpeg(temp_wav, filename, extra_params)
        os.remove(temp_wav)
        logger.info("MP3 file saved as %s", out_file)
        return out_file

class AacEncoder(FFmpegEncoderMixin):
    def __init__(self, profile='LC'):
        self.profile = profile

    def encode(self, pcm, filename="output.aac", sample_rate=48000):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_wav = tmp.name
        sf.write(file=temp_wav, data=pcm, samplerate=sample_rate, subtype='FLOAT')
        logger.debug("Temporary WAV file created for AAC: %s", temp_wav)
        extra_params = ['-c:a', 'aac', '-b:a', '192k']
        out_file = self._convert_with_ffmpeg(temp_wav, filename, extra_params)
        os.remove(temp_wav)
        logger.info("AAC file saved as %s", out_file)
        return out_file

class WmaEncoder(FFmpegEncoderMixin):
    def __init__(self, bitrate=192):
        self.bitrate = bitrate

    def encode(self, pcm, filename="output.wma", sample_rate=48000):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_wav = tmp.name
        sf.write(file=temp_wav, data=pcm, samplerate=sample_rate, subtype='FLOAT')
        logger.debug("Temporary WAV file created for WMA: %s", temp_wav)
        extra_params = ['-c:a', 'wmav2', '-b:a', f'{self.bitrate}k']
        out_file = self._convert_with_ffmpeg(temp_wav, filename, extra_params)
        os.remove(temp_wav)
        logger.info("WMA file saved as %s", out_file)
        return out_file
