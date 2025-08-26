#!/usr/bin/env python3
"""
Simple test script for the YouTube Music Transcriber
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audio.preprocessor import AudioPreprocessor
from transcription.analyzer import MusicTranscriber, Note
from sheet_music.generator import SheetMusicGenerator

def test_components():
    """Test individual components without YouTube download."""
    
    print("🧪 Testing YouTube Music Transcriber Components")
    print("=" * 50)
    
    # Test 1: Audio preprocessor
    print("1. Testing Audio Preprocessor...")
    try:
        preprocessor = AudioPreprocessor()
        print("   ✅ AudioPreprocessor initialized successfully")
    except Exception as e:
        print(f"   ❌ AudioPreprocessor failed: {e}")
        return False
    
    # Test 2: Music transcriber
    print("2. Testing Music Transcriber...")
    try:
        transcriber = MusicTranscriber()
        print("   ✅ MusicTranscriber initialized successfully")
    except Exception as e:
        print(f"   ❌ MusicTranscriber failed: {e}")
        return False
    
    # Test 3: Sheet music generator
    print("3. Testing Sheet Music Generator...")
    try:
        generator = SheetMusicGenerator()
        print("   ✅ SheetMusicGenerator initialized successfully")
    except Exception as e:
        print(f"   ❌ SheetMusicGenerator failed: {e}")
        return False
    
    # Test 4: Create sample notes and generate sheet music
    print("4. Testing sheet music generation with sample notes...")
    try:
        # Create some sample notes (C major scale)
        sample_notes = [
            Note(pitch=60, start_time=0.0, end_time=0.5, velocity=80),    # C4
            Note(pitch=62, start_time=0.5, end_time=1.0, velocity=80),    # D4
            Note(pitch=64, start_time=1.0, end_time=1.5, velocity=80),    # E4
            Note(pitch=65, start_time=1.5, end_time=2.0, velocity=80),    # F4
            Note(pitch=67, start_time=2.0, end_time=2.5, velocity=80),    # G4
            Note(pitch=69, start_time=2.5, end_time=3.0, velocity=80),    # A4
            Note(pitch=71, start_time=3.0, end_time=3.5, velocity=80),    # B4
            Note(pitch=72, start_time=3.5, end_time=4.0, velocity=80),    # C5
        ]
        
        # Generate sheet music
        output_files = generator.generate_sheet_music(
            sample_notes, 
            tempo_bpm=120, 
            output_dir="output", 
            filename="test_scale"
        )
        
        print(f"   ✅ Generated sheet music files:")
        for format_type, file_path in output_files.items():
            print(f"      - {format_type.upper()}: {file_path}")
        
    except Exception as e:
        print(f"   ❌ Sheet music generation failed: {e}")
        return False
    
    # Test 5: Check dependencies
    print("5. Checking required dependencies...")
    try:
        import librosa
        import music21
        import yt_dlp
        print("   ✅ All dependencies are available")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        return False
    
    print("\n🎉 All tests passed! The application should work correctly.")
    print("\nTo test with a real YouTube video, run:")
    print('python main.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"')
    
    return True

if __name__ == "__main__":
    success = test_components()
    sys.exit(0 if success else 1)
