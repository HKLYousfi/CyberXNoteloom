import numpy as np
import logging
from threading import Thread, Lock

logger = logging.getLogger(__name__)

def apply_adsr_envelope(note_duration, sample_rate, attack=0.01, decay=0.1, sustain_level=0.7, release=0.2):
    """
    Generate an ADSR envelope for a note.
    - note_duration: duration in seconds.
    - Returns an envelope as a float32 array.
    """
    total_samples = int(note_duration * sample_rate)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - (attack_samples + decay_samples + release_samples)
    if sustain_samples < 0:
        sustain_samples = 0

    attack_env = np.linspace(0, 1, attack_samples, endpoint=False, dtype=np.float32)
    decay_env = np.linspace(1, sustain_level, decay_samples, endpoint=False, dtype=np.float32)
    sustain_env = np.full(sustain_samples, sustain_level, dtype=np.float32)
    release_env = np.linspace(sustain_level, 0, release_samples, endpoint=True, dtype=np.float32)
    
    envelope = np.concatenate((attack_env, decay_env, sustain_env, release_env))
    # Log envelope shape for debugging
    logger.debug("ADSR envelope shape: %s (total_samples=%d)", envelope.shape, total_samples)
    if envelope.shape[0] < total_samples:
        envelope = np.pad(envelope, (0, total_samples - envelope.shape[0]), mode='constant')
    return envelope.astype(np.float32)

class HybridSynthesizer:
    """
    HybridSynthesizer implements an ADSR-based synthesis engine.
    It uses sine-wave oscillators combined with an ADSR envelope to generate realistic notes.
    """
    def __init__(self, sample_rate=48000, channels=2, duration=10.0, mode='adsr'):
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration = duration
        self.mode = mode

    def synthesize_note(self, freq, duration, velocity):
        """
        Synthesize a single note.
        - freq: Frequency in Hz.
        - duration: Note duration in seconds.
        - velocity: MIDI velocity (0-127).
        Returns a 1D float32 NumPy array representing the note's waveform.
        """
        num_samples = int(duration * self.sample_rate)
        # Use float32 throughout to save memory
        t = np.linspace(0, duration, num_samples, endpoint=False, dtype=np.float32)
        tone = np.sin(2 * np.pi * freq * t).astype(np.float32)
        envelope = apply_adsr_envelope(duration, self.sample_rate)
        # Ensure tone and envelope have the same length
        if len(tone) != len(envelope):
            min_len = min(len(tone), len(envelope))
            tone = tone[:min_len]
            envelope = envelope[:min_len]
            logger.debug("Trimmed tone/envelope to length: %d", min_len)
        velocity_factor = np.float32(velocity / 127.0)
        return (tone * envelope * velocity_factor).astype(np.float32)

    def render(self, midi_events):
        """
        Renders PCM audio from MIDI events.
        Determines note duration by matching note_on with corresponding note_off events.
        Returns a float32 PCM NumPy array with shape (num_samples, channels).
        """
        num_samples = int(self.sample_rate * self.duration)
        audio = np.zeros((num_samples, self.channels), dtype=np.float32)
        voices = []
        lock = Lock()
        default_duration_sec = 0.5  # Fallback duration

        def synthesize(event, duration_sec):
            note = event['note']
            velocity = event['velocity']
            start_sample = int(event['time'] * self.sample_rate / 1e6)
            freq = 440.0 * (2 ** ((note - 69) / 12.0))
            try:
                note_wave = self.synthesize_note(freq, duration_sec, velocity)
            except Exception as e:
                logger.error("Error synthesizing note %d: %s", note, e)
                return
            # Log shape of synthesized note
            logger.debug("Synthesized note %d: waveform length %d", note, len(note_wave))
            end_sample = min(start_sample + len(note_wave), num_samples)
            with lock:
                # Broadcast note_wave to all channels
                audio[start_sample:end_sample, :] += np.tile(note_wave[:end_sample - start_sample, np.newaxis], (1, self.channels))
            logger.debug("Rendered note %d from sample %d to %d", note, start_sample, end_sample)

        for idx, event in enumerate(midi_events):
            if event['type'] == 'note_on':
                duration_sec = default_duration_sec
                for subsequent in midi_events[idx+1:]:
                    if (subsequent.get('type') == 'note_off' and
                        subsequent.get('note') == event['note'] and
                        subsequent.get('channel') == event['channel']):
                        note_off_time = subsequent['time'] / 1e6
                        note_on_time = event['time'] / 1e6
                        duration_sec = max(0.1, note_off_time - note_on_time)
                        break
                thread = Thread(target=synthesize, args=(event, duration_sec))
                thread.start()
                voices.append(thread)
        for t in voices:
            t.join()
        logger.info("Synthesis complete. Final audio shape: %s", audio.shape)
        return audio.astype(np.float32)

# Advanced features

class ResonanceModel:
    """
    Placeholder for sympathetic string resonance simulation.
    """
    def __init__(self):
        self.factors = np.zeros(128, dtype=np.float32)

    def update(self, active_notes):
        for note in active_notes:
            self.factors += 0.2 / (1 + np.abs(np.arange(128, dtype=np.float32) - note))
        logger.debug("Resonance updated.")

def generate_pedal_noise(sample_rate, pedal_value):
    """
    Generates sustain pedal noise (click) based on the pedal value.
    Returns a float32 NumPy array.
    """
    click_samples = int(0.02 * sample_rate)
    noise = np.random.uniform(-0.1, 0.1, click_samples).astype(np.float32)
    return noise * (pedal_value / 127.0)
