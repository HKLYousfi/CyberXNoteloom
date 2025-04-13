"""
effects.py
----------
Implements advanced DSP effects for CyberXNoteloom:
  - Advanced reverb: Creates a composite impulse response from early reflections and a long tail,
    applies FFT-based convolution, and mixes wet/dry signals.
  - Advanced EQ: Applies a cascade of parametric (peaking) EQ filters to the PCM audio.
  
Both functions include extensive shape logging and are optimized for high quality.
"""

import numpy as np
import scipy.signal
import logging

logger = logging.getLogger(__name__)

def apply_advanced_reverb(pcm, sample_rate, early_delay_ms=[20, 40, 60], early_decay=0.6,
                          tail_decay=0.995, tail_length_sec=1.5, wet_mix=0.5):
    """
    Applies an advanced reverb effect to the PCM audio.
    
    The reverb impulse response (IR) is built by:
      - Creating early reflections at specified delays.
      - Generating a long tail with exponential decay.
      - Combining both IR parts.
    A wet/dry mix is applied before returning processed audio.

    Parameters:
      - pcm: float32 NumPy array (num_samples x channels)
      - sample_rate: Sampling rate in Hz
      - early_delay_ms: List of early reflection delays in milliseconds.
      - early_decay: Decay factor for early reflections.
      - tail_decay: Multiplicative decay factor for the tail.
      - tail_length_sec: Duration of the tail in seconds.
      - wet_mix: Mix ratio for the reverberated signal (0: dry, 1: fully wet).
    
    Returns:
      - Processed PCM audio with reverb applied.
    """
    num_channels = pcm.shape[1]
    
    # Early Reflections
    early_ir_length = int(max(early_delay_ms) * sample_rate / 1000) + 1
    early_ir = np.zeros(early_ir_length, dtype=np.float32)
    early_ir[0] = 1.0  # direct sound
    for delay_ms in early_delay_ms:
        delay_samples = int(delay_ms * sample_rate / 1000)
        if delay_samples < early_ir_length:
            early_ir[delay_samples] = early_decay
    if np.max(np.abs(early_ir)) != 0:
        early_ir = early_ir / np.max(np.abs(early_ir))
    logger.debug("Early IR shape: %s", early_ir.shape)
    
    # Long Tail
    tail_length = int(tail_length_sec * sample_rate)
    t = np.linspace(0, tail_length_sec, tail_length, endpoint=False, dtype=np.float32)
    tail_ir = (np.random.randn(tail_length).astype(np.float32) * np.exp(-3*t)) * (tail_decay ** np.arange(tail_length, dtype=np.float32))
    if np.max(np.abs(tail_ir)) != 0:
        tail_ir = tail_ir / np.max(np.abs(tail_ir))
    logger.debug("Tail IR shape: %s", tail_ir.shape)
    
    # Combine Early and Tail IRs
    combined_length = max(early_ir_length, tail_length)
    # Pad both IRs to combined_length
    early_ir_padded = np.pad(early_ir, (0, combined_length - early_ir_length), mode='constant')
    tail_ir_padded = np.pad(tail_ir, (0, combined_length - tail_length), mode='constant')
    ir = early_ir_padded + tail_ir_padded
    logger.debug("Combined IR shape: %s", ir.shape)
    
    # Convolve IR with input signal for each channel
    wet = np.zeros_like(pcm)
    for ch in range(num_channels):
        conv_result = scipy.signal.fftconvolve(pcm[:, ch], ir, mode='full')
        # Ensure output length matches the original pcm shape
        wet[:, ch] = conv_result[:pcm.shape[0]]
    # Mix wet and dry signals
    processed = (1.0 - wet_mix) * pcm + wet_mix * wet
    logger.debug("Advanced reverb applied with wet mix: %.2f", wet_mix)
    return processed.astype(np.float32)

def apply_advanced_eq(pcm, sample_rate, bands=None):
    """
    Applies a multi-band parametric EQ to the PCM audio.
    
    Each band is defined as a dictionary with keys: 'gain_db', 'center_freq', 'Q'.
    Filters are cascaded to produce a flexible multi-band equalizer.
    If no bands are provided, a default band is applied.
    
    Parameters:
      - pcm: float32 NumPy array (num_samples x channels)
      - sample_rate: Sampling rate in Hz
      - bands: List of dictionaries (default: [{'gain_db': 3.0, 'center_freq': 1000, 'Q': 1.0}])
    
    Returns:
      - Processed PCM audio with EQ applied.
    """
    from scipy.signal import lfilter, iirpeak

    if bands is None:
        bands = [{'gain_db': 3.0, 'center_freq': 1000, 'Q': 1.0}]
    
    processed = np.copy(pcm).astype(np.float32)
    num_channels = processed.shape[1]
    
    for band in bands:
        gain_db = band.get('gain_db', 0)
        center_freq = band.get('center_freq', 1000)
        Q = band.get('Q', 1.0)
        
        normalized_center = center_freq / (sample_rate / 2)
        b, a = iirpeak(normalized_center, Q)
        gain_factor = 10 ** (gain_db / 20)
        b = b * gain_factor
        logger.debug("Applying EQ band: gain %.2f dB, center %d Hz, Q=%.2f", gain_db, center_freq, Q)
        
        for ch in range(num_channels):
            processed[:, ch] = lfilter(b, a, processed[:, ch])
        logger.debug("EQ band processed for channel %d", ch)
    
    logger.debug("Advanced EQ processing complete. Processed shape: %s", processed.shape)
    return processed.astype(np.float32)
