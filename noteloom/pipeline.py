#!/usr/bin/env python3
"""
pipeline.py
-----------
Implements a professional-grade audio processing pipeline.
Includes:
  - Oversampling using polyphase resampling (via scipy.signal.resample_poly)
  - High-quality anti-alias filtering with a Kaiser-windowed FIR filter
  - Soft-knee dynamics limiting to gently compress peaks
  - Normalization with TPDF dithering for reduced quantization noise
"""

import numpy as np
import scipy.signal
import logging

logger = logging.getLogger(__name__)

class Oversampler:
    """
    Performs oversampling using polyphase resampling.
    This method is more accurate than simple linear interpolation.
    """
    def __init__(self, factor=8):
        self.factor = factor

    def process(self, pcm):
        num_samples, channels = pcm.shape
        # Use resample_poly for each channel
        upsampled_list = []
        for ch in range(channels):
            up_ch = scipy.signal.resample_poly(pcm[:, ch], self.factor, 1)
            upsampled_list.append(up_ch)
        upsampled = np.stack(upsampled_list, axis=1).astype(np.float32)
        logger.debug("Oversampling complete: new shape %s", upsampled.shape)
        return upsampled

class AntiAliasFilter:
    """
    Applies a high-quality low-pass FIR filter using a Kaiser window.
    """
    def __init__(self, cutoff=0.45, numtaps=151, beta=8.0):
        # cutoff is normalized (0 to 1); 1 is Nyquist.
        self.cutoff = cutoff
        self.numtaps = numtaps
        self.beta = beta
        self.kernel = scipy.signal.firwin(self.numtaps, self.cutoff, window=('kaiser', self.beta))
        logger.debug("Designed FIR filter with %d taps and beta=%.2f", self.numtaps, self.beta)

    def process(self, pcm):
        filtered = np.zeros_like(pcm)
        for ch in range(pcm.shape[1]):
            filtered[:, ch] = np.convolve(pcm[:, ch], self.kernel, mode='same')
        logger.debug("Anti-alias filtering complete; output shape %s", filtered.shape)
        return filtered

class DynamicsProcessor:
    """
    Applies soft-knee dynamic limiting.
    This limits peaks gently to avoid hard clipping while preserving dynamic range.
    """
    def __init__(self, threshold=0.9, ratio=10.0):
        self.threshold = threshold
        self.ratio = ratio

    def process(self, pcm):
        magnitude = np.abs(pcm)
        over = magnitude > self.threshold
        # Apply soft compression over threshold
        pcm[over] = np.sign(pcm[over]) * (self.threshold + (magnitude[over] - self.threshold) / self.ratio)
        logger.debug("Dynamics processed with threshold=%.2f, ratio=%.2f", self.threshold, self.ratio)
        return pcm

class Normalizer:
    """
    Normalizes the PCM signal to full scale (±1) and applies TPDF dithering.
    """
    def __init__(self, dither_amp=1e-5):
        self.dither_amp = dither_amp

    def process(self, pcm):
        max_val = np.max(np.abs(pcm))
        if max_val > 0:
            pcm = pcm / max_val
        noise = (np.random.uniform(-self.dither_amp, self.dither_amp, pcm.shape) +
                 np.random.uniform(-self.dither_amp, self.dither_amp, pcm.shape)).astype(np.float32)
        logger.debug("Normalization and TPDF dithering applied; noise shape %s", noise.shape)
        return pcm + noise

class AudioPipeline:
    """
    Chains together multiple processing blocks.
    PCM audio is processed sequentially through each block.
    """
    def __init__(self, blocks):
        self.blocks = blocks

    def process(self, pcm):
        for block in self.blocks:
            pcm = block.process(pcm)
            logger.debug("Intermediate shape after %s: %s", block.__class__.__name__, pcm.shape)
        logger.info("Audio pipeline processing complete. Final shape: %s", pcm.shape)
        return pcm
