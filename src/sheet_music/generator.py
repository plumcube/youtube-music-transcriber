"""
Sheet music generation module.
Converts transcribed notes into sheet music notation using music21.
"""

import music21
from music21 import stream, note, duration, tempo, meter, key, pitch
import pretty_midi
from typing import List, Optional
from pathlib import Path
import logging

# Import our Note class from transcription module
import sys
sys.path.append('..')
from transcription.analyzer import Note

class SheetMusicGenerator:
    """Generate sheet music from transcribed notes."""
    
    def __init__(self):
        self.default_tempo = 120
        self.default_time_signature = "4/4"
        self.default_key_signature = "C major"
    
    def midi_to_note_name(self, midi_number: float) -> str:
        """
        Convert MIDI note number to note name.
        
        Args:
            midi_number: MIDI note number (0-127)
            
        Returns:
            Note name string (e.g., 'C4', 'F#3')
        """
        try:
            p = pitch.Pitch()
            p.midi = int(midi_number)
            return p.nameWithOctave
        except:
            return 'C4'  # fallback
    
    def quantize_duration(self, duration_seconds: float, tempo_bpm: float = 120) -> str:
        """
        Quantize note duration to standard musical durations.
        
        Args:
            duration_seconds: Duration in seconds
            tempo_bpm: Tempo in beats per minute
            
        Returns:
            Music21 duration string
        """
        # Convert seconds to beats (assuming 4/4 time)
        beats_per_second = tempo_bpm / 60
        duration_beats = duration_seconds * beats_per_second
        
        # Quantize to nearest standard duration
        if duration_beats >= 3.5:
            return "whole"
        elif duration_beats >= 1.75:
            return "half"
        elif duration_beats >= 0.875:
            return "quarter"
        elif duration_beats >= 0.4375:
            return "eighth"
        elif duration_beats >= 0.21875:
            return "16th"
        else:
            return "32nd"
    
    def create_music21_score(self, notes: List[Note], tempo_bpm: float = 120) -> stream.Stream:
        """
        Create a music21 Score from transcribed notes.
        
        Args:
            notes: List of Note objects
            tempo_bpm: Tempo in BPM
            
        Returns:
            music21 Stream object
        """
        try:
            # Create a new score
            score = stream.Score()
            
            # Add metadata
            score.metadata = music21.metadata.Metadata()
            score.metadata.title = 'YouTube Music Transcription'
            score.metadata.composer = 'Auto-transcribed'
            
            # Create a part
            part = stream.Part()
            
            # Add tempo marking
            tempo_mark = tempo.MetronomeMark(number=tempo_bpm)
            part.insert(0, tempo_mark)
            
            # Add time signature
            time_sig = meter.TimeSignature(self.default_time_signature)
            part.insert(0, time_sig)
            
            # Add key signature (try to detect or use default)
            key_sig = key.KeySignature(0)  # C major
            part.insert(0, key_sig)
            
            if not notes:
                # Add a rest if no notes
                rest = note.Rest(duration=duration.Duration("whole"))
                part.append(rest)
            else:
                # Sort notes by start time
                sorted_notes = sorted(notes, key=lambda n: n.start_time)
                
                current_time = 0
                
                for n in sorted_notes:
                    # Add rest if there's a gap
                    if n.start_time > current_time:
                        rest_duration = n.start_time - current_time
                        rest_duration_type = self.quantize_duration(rest_duration, tempo_bpm)
                        rest = note.Rest(duration=duration.Duration(rest_duration_type))
                        part.append(rest)
                    
                    # Create the note
                    note_duration = n.end_time - n.start_time
                    note_duration_type = self.quantize_duration(note_duration, tempo_bpm)
                    
                    # Create music21 note
                    try:
                        m21_note = note.Note(
                            pitch.Pitch(midi=int(n.pitch)),
                            duration=duration.Duration(note_duration_type)
                        )
                        m21_note.volume.velocity = n.velocity
                        part.append(m21_note)
                    except Exception as e:
                        logging.warning(f"Failed to create note for MIDI {n.pitch}: {e}")
                        # Add a rest instead
                        rest = note.Rest(duration=duration.Duration(note_duration_type))
                        part.append(rest)
                    
                    current_time = n.end_time
            
            # Add the part to the score
            score.append(part)
            
            return score
            
        except Exception as e:
            logging.error(f"Failed to create music21 score: {str(e)}")
            raise
    
    def save_musicxml(self, score: stream.Stream, output_path: str) -> str:
        """
        Save score as MusicXML file.
        
        Args:
            score: music21 Stream object
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Ensure .xml extension
            if output_path.suffix.lower() != '.xml':
                output_path = output_path.with_suffix('.xml')
            
            # Save as MusicXML
            score.write('musicxml', fp=str(output_path))
            logging.info(f"Saved MusicXML to {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Failed to save MusicXML: {str(e)}")
            raise
    
    def save_midi(self, score: stream.Stream, output_path: str) -> str:
        """
        Save score as MIDI file.
        
        Args:
            score: music21 Stream object
            output_path: Output file path
            
        Returns:
            Path to saved file
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Ensure .mid extension
            if output_path.suffix.lower() not in ['.mid', '.midi']:
                output_path = output_path.with_suffix('.mid')
            
            # Save as MIDI
            score.write('midi', fp=str(output_path))
            logging.info(f"Saved MIDI to {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logging.error(f"Failed to save MIDI: {str(e)}")
            raise
    
    def save_png(self, score: stream.Stream, output_path: str) -> Optional[str]:
        """
        Save score as PNG image (requires additional software).
        
        Args:
            score: music21 Stream object
            output_path: Output file path
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Ensure .png extension
            if output_path.suffix.lower() != '.png':
                output_path = output_path.with_suffix('.png')
            
            # This requires MuseScore or LilyPond to be installed
            score.write('musicxml.png', fp=str(output_path))
            logging.info(f"Saved PNG to {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            logging.warning(f"Failed to save PNG (requires MuseScore): {str(e)}")
            return None
    
    def generate_sheet_music(self, notes: List[Note], tempo_bpm: float, 
                           output_dir: str, filename: str = "transcription") -> dict:
        """
        Generate sheet music in multiple formats.
        
        Args:
            notes: List of Note objects
            tempo_bpm: Tempo in BPM
            output_dir: Output directory
            filename: Base filename (without extension)
            
        Returns:
            Dictionary with paths to generated files
        """
        try:
            # Create music21 score
            score = self.create_music21_score(notes, tempo_bpm)
            
            output_files = {}
            
            # Save MusicXML
            try:
                xml_path = self.save_musicxml(score, f"{output_dir}/{filename}.xml")
                output_files['musicxml'] = xml_path
            except Exception as e:
                logging.error(f"Failed to save MusicXML: {e}")
            
            # Save MIDI
            try:
                midi_path = self.save_midi(score, f"{output_dir}/{filename}.mid")
                output_files['midi'] = midi_path
            except Exception as e:
                logging.error(f"Failed to save MIDI: {e}")
            
            # Try to save PNG (optional)
            try:
                png_path = self.save_png(score, f"{output_dir}/{filename}.png")
                if png_path:
                    output_files['png'] = png_path
            except Exception as e:
                logging.warning(f"PNG export not available: {e}")
            
            return output_files
            
        except Exception as e:
            logging.error(f"Failed to generate sheet music: {str(e)}")
            raise
    
    def get_score_info(self, score: stream.Stream) -> dict:
        """
        Get information about the generated score.
        
        Args:
            score: music21 Stream object
            
        Returns:
            Dictionary with score information
        """
        try:
            # Analyze the score
            parts = score.parts
            if not parts:
                return {'error': 'No parts found'}
            
            part = parts[0]
            notes = part.flatten().notes
            
            return {
                'total_measures': len(part.getElementsByClass('Measure')),
                'total_notes': len([n for n in notes if isinstance(n, note.Note)]),
                'total_rests': len([n for n in notes if isinstance(n, note.Rest)]),
                'key_signature': str(part.getElementsByClass(key.KeySignature)[0]) if part.getElementsByClass(key.KeySignature) else 'Unknown',
                'time_signature': str(part.getElementsByClass(meter.TimeSignature)[0]) if part.getElementsByClass(meter.TimeSignature) else 'Unknown',
                'tempo': str(part.getElementsByClass(tempo.TempoIndication)[0]) if part.getElementsByClass(tempo.TempoIndication) else 'Unknown'
            }
            
        except Exception as e:
            logging.error(f"Failed to analyze score: {str(e)}")
            return {'error': str(e)}
