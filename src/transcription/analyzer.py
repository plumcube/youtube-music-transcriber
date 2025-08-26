"""
Music transcription module.
Analyzes audio to detect pitch, rhythm, and musical notes.
"""

import librosa
import numpy as np
from scipy.signal import find_peaks
import pretty_midi
from dataclasses import dataclass
from typing import List, Tuple
import logging

@dataclass
class Note:
    """Represents a musical note."""
    pitch: float  # MIDI note number
    start_time: float  # seconds
    end_time: float  # seconds
    velocity: int  # 0-127

class MusicTranscriber:
    """Transcribe audio to musical notes."""
    
    def __init__(self, hop_length=512, n_fft=2048):
        self.hop_length = hop_length
        self.n_fft = n_fft
        self.min_note_duration = 0.1  # minimum note duration in seconds
        self.pitch_threshold = 0.3  # minimum confidence for pitch detection
        
    def detect_pitches(self, audio: np.ndarray, sr: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect fundamental frequencies (pitches) in audio.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Tuple of (times, pitches) arrays
        """
        try:
            # Use librosa's pitch detection
            pitches, magnitudes = librosa.core.piptrack(
                y=audio, 
                sr=sr, 
                hop_length=self.hop_length,
                fmin=librosa.note_to_hz('C2'),  # ~65 Hz
                fmax=librosa.note_to_hz('C7')   # ~2093 Hz
            )
            
            # Extract the most confident pitch per time frame
            pitch_track = []
            magnitude_track = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                magnitude = magnitudes[index, t]
                
                # Only keep confident pitches
                if magnitude > self.pitch_threshold and pitch > 0:
                    pitch_track.append(pitch)
                    magnitude_track.append(magnitude)
                else:
                    pitch_track.append(0)
                    magnitude_track.append(0)
            
            # Convert to time array
            times = librosa.frames_to_time(
                range(len(pitch_track)), 
                sr=sr, 
                hop_length=self.hop_length
            )
            
            return times, np.array(pitch_track)
            
        except Exception as e:
            logging.error(f"Failed to detect pitches: {str(e)}")
            raise
    
    def hz_to_midi(self, freq: float) -> float:
        """Convert frequency in Hz to MIDI note number."""
        if freq <= 0:
            return 0
        return 69 + 12 * np.log2(freq / 440.0)
    
    def detect_onset_times(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Detect note onset times.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Array of onset times in seconds
        """
        try:
            # Detect onsets
            onset_frames = librosa.onset.onset_detect(
                y=audio,
                sr=sr,
                hop_length=self.hop_length,
                delta=0.02,
                wait=int(0.03 * sr / self.hop_length)  # minimum time between onsets
            )
            
            # Convert to time
            onset_times = librosa.frames_to_time(
                onset_frames, 
                sr=sr, 
                hop_length=self.hop_length
            )
            
            return onset_times
            
        except Exception as e:
            logging.error(f"Failed to detect onsets: {str(e)}")
            return np.array([])
    
    def estimate_tempo(self, audio: np.ndarray, sr: int) -> float:
        """
        Estimate the tempo (BPM) of the audio.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Estimated tempo in BPM
        """
        try:
            tempo, _ = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.hop_length)
            return float(tempo)
        except Exception as e:
            logging.error(f"Failed to estimate tempo: {str(e)}")
            return 120.0  # default tempo
    
    def segment_notes(self, times: np.ndarray, pitches: np.ndarray, onset_times: np.ndarray) -> List[Note]:
        """
        Segment continuous pitches into discrete notes.
        
        Args:
            times: Time array
            pitches: Pitch array (in Hz)
            onset_times: Onset time array
            
        Returns:
            List of Note objects
        """
        notes = []
        
        if len(pitches) == 0 or len(times) == 0:
            return notes
        
        # Convert pitches to MIDI notes
        midi_pitches = np.array([self.hz_to_midi(p) for p in pitches])
        
        # Group consecutive frames with similar pitches
        current_pitch = 0
        start_time = 0
        start_idx = 0
        
        for i, (time, midi_pitch) in enumerate(zip(times, midi_pitches)):
            # Check if pitch changed significantly (more than 1 semitone)
            pitch_changed = abs(midi_pitch - current_pitch) > 1.0 if current_pitch > 0 else False
            
            if midi_pitch > 0 and (current_pitch == 0 or not pitch_changed):
                # Continue current note or start new note
                if current_pitch == 0:
                    start_time = time
                    start_idx = i
                current_pitch = midi_pitch
                
            else:
                # End current note if it exists
                if current_pitch > 0 and time - start_time >= self.min_note_duration:
                    # Calculate average pitch over the note duration
                    avg_pitch = np.mean(midi_pitches[start_idx:i])
                    if avg_pitch > 0:
                        note = Note(
                            pitch=round(avg_pitch),
                            start_time=start_time,
                            end_time=time,
                            velocity=80  # default velocity
                        )
                        notes.append(note)
                
                # Start new note if current pitch is valid
                if midi_pitch > 0:
                    current_pitch = midi_pitch
                    start_time = time
                    start_idx = i
                else:
                    current_pitch = 0
        
        # Handle the last note
        if current_pitch > 0 and len(times) > 0:
            end_time = times[-1]
            if end_time - start_time >= self.min_note_duration:
                avg_pitch = np.mean(midi_pitches[start_idx:])
                if avg_pitch > 0:
                    note = Note(
                        pitch=round(avg_pitch),
                        start_time=start_time,
                        end_time=end_time,
                        velocity=80
                    )
                    notes.append(note)
        
        return notes
    
    def transcribe_audio(self, audio: np.ndarray, sr: int) -> Tuple[List[Note], float]:
        """
        Complete audio transcription pipeline.
        
        Args:
            audio: Audio signal
            sr: Sample rate
            
        Returns:
            Tuple of (notes_list, estimated_tempo)
        """
        try:
            logging.info("Starting audio transcription...")
            
            # Detect pitches
            times, pitches = self.detect_pitches(audio, sr)
            logging.info(f"Detected {np.sum(pitches > 0)} pitch frames")
            
            # Detect onsets
            onset_times = self.detect_onset_times(audio, sr)
            logging.info(f"Detected {len(onset_times)} onsets")
            
            # Estimate tempo
            tempo = self.estimate_tempo(audio, sr)
            logging.info(f"Estimated tempo: {tempo:.1f} BPM")
            
            # Segment into notes
            notes = self.segment_notes(times, pitches, onset_times)
            logging.info(f"Segmented {len(notes)} notes")
            
            return notes, tempo
            
        except Exception as e:
            logging.error(f"Failed to transcribe audio: {str(e)}")
            raise
    
    def get_transcription_stats(self, notes: List[Note]) -> dict:
        """
        Get statistics about the transcription.
        
        Args:
            notes: List of Note objects
            
        Returns:
            Dictionary with transcription statistics
        """
        if not notes:
            return {
                'total_notes': 0,
                'duration': 0,
                'pitch_range': (0, 0),
                'average_note_duration': 0
            }
        
        pitches = [note.pitch for note in notes]
        durations = [note.end_time - note.start_time for note in notes]
        total_duration = max(note.end_time for note in notes) if notes else 0
        
        return {
            'total_notes': len(notes),
            'duration': total_duration,
            'pitch_range': (min(pitches), max(pitches)),
            'average_note_duration': np.mean(durations),
            'unique_pitches': len(set(pitches))
        }
