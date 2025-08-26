"""
Audio preprocessing module.
Handles audio normalization, noise reduction, and format conversion.
"""

import librosa
import numpy as np
import soundfile as sf
from pathlib import Path
from scipy.signal import butter, filtfilt
import logging

class AudioPreprocessor:
    """Preprocess audio for better transcription results."""
    
    def __init__(self, target_sr=22050):
        self.target_sr = target_sr
    
    def load_audio(self, file_path: str) -> tuple:
        """
        Load audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        try:
            audio, sr = librosa.load(file_path, sr=self.target_sr)
            return audio, sr
        except Exception as e:
            logging.error(f"Failed to load audio file {file_path}: {str(e)}")
            raise
    
    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio amplitude.
        
        Args:
            audio: Audio signal
            
        Returns:
            Normalized audio signal
        """
        # Normalize to [-1, 1] range
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio
    
    def apply_highpass_filter(self, audio: np.ndarray, sr: int, cutoff: float = 80.0) -> np.ndarray:
        """
        Apply highpass filter to remove low-frequency noise.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            cutoff: Cutoff frequency in Hz
            
        Returns:
            Filtered audio signal
        """
        try:
            nyquist = sr * 0.5
            normal_cutoff = cutoff / nyquist
            b, a = butter(6, normal_cutoff, btype='high', analog=False)
            return filtfilt(b, a, audio)
        except Exception as e:
            logging.warning(f"Failed to apply highpass filter: {str(e)}")
            return audio
    
    def trim_silence(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Trim silence from beginning and end of audio.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Trimmed audio signal
        """
        try:
            # Use librosa's trim function
            audio_trimmed, _ = librosa.effects.trim(audio, top_db=20)
            return audio_trimmed
        except Exception as e:
            logging.warning(f"Failed to trim silence: {str(e)}")
            return audio
    
    def reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Simple noise reduction using spectral gating.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Noise-reduced audio signal
        """
        try:
            # Compute spectral centroid to identify noise
            S = np.abs(librosa.stft(audio))
            centroid = librosa.feature.spectral_centroid(S=S, sr=sr)[0]
            
            # Simple noise gate based on energy
            frame_length = 2048
            hop_length = 512
            frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
            energy = np.sum(frames**2, axis=0)
            energy_threshold = np.percentile(energy, 30)  # Keep frames above 30th percentile
            
            # Reconstruct audio keeping only high-energy frames
            result = np.zeros_like(audio)
            for i, frame_energy in enumerate(energy):
                start_idx = i * hop_length
                end_idx = min(start_idx + frame_length, len(audio))
                if frame_energy > energy_threshold:
                    result[start_idx:end_idx] = audio[start_idx:end_idx]
            
            return result
        except Exception as e:
            logging.warning(f"Failed to reduce noise: {str(e)}")
            return audio
    
    def preprocess_audio(self, file_path: str, output_path: str = None) -> tuple:
        """
        Complete audio preprocessing pipeline.
        
        Args:
            file_path: Input audio file path
            output_path: Optional output file path
            
        Returns:
            Tuple of (processed_audio, sample_rate, output_file_path)
        """
        try:
            # Load audio
            audio, sr = self.load_audio(file_path)
            logging.info(f"Loaded audio: {len(audio)} samples at {sr} Hz")
            
            # Preprocessing steps
            audio = self.trim_silence(audio, sr)
            audio = self.normalize_audio(audio)
            audio = self.apply_highpass_filter(audio, sr)
            # Note: Noise reduction can be aggressive, so it's optional
            # audio = self.reduce_noise(audio, sr)
            
            # Save processed audio if output path is provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                sf.write(str(output_path), audio, sr)
                logging.info(f"Saved processed audio to {output_path}")
                return audio, sr, str(output_path)
            
            return audio, sr, None
            
        except Exception as e:
            logging.error(f"Failed to preprocess audio {file_path}: {str(e)}")
            raise
    
    def get_audio_stats(self, audio: np.ndarray, sr: int) -> dict:
        """
        Get basic audio statistics.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Dictionary with audio statistics
        """
        return {
            'duration': len(audio) / sr,
            'sample_rate': sr,
            'channels': 1,  # We load as mono
            'max_amplitude': np.max(np.abs(audio)),
            'rms_energy': np.sqrt(np.mean(audio**2)),
            'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(audio)[0]),
        }
