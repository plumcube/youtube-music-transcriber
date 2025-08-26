#!/usr/bin/env python3
"""
YouTube Music to Sheet Music Converter
Main application entry point.
"""

import sys
import os
import logging
from pathlib import Path
import click
from tqdm import tqdm

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audio.youtube_downloader import YouTubeAudioDownloader
from audio.preprocessor import AudioPreprocessor
from transcription.analyzer import MusicTranscriber
from sheet_music.generator import SheetMusicGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeMusicTranscriber:
    """Main application class."""
    
    def __init__(self, output_dir="output", temp_dir="temp"):
        self.output_dir = Path(output_dir)
        self.temp_dir = Path(temp_dir)
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.downloader = YouTubeAudioDownloader(str(self.temp_dir))
        self.preprocessor = AudioPreprocessor()
        self.transcriber = MusicTranscriber()
        self.sheet_generator = SheetMusicGenerator()
    
    def transcribe_youtube_url(self, url: str, output_name: str = None) -> dict:
        """
        Complete transcription pipeline from YouTube URL to sheet music.
        
        Args:
            url: YouTube URL
            output_name: Base name for output files
            
        Returns:
            Dictionary with results and file paths
        """
        try:
            # Step 1: Download audio
            logger.info("Downloading audio from YouTube...")
            audio_file = self.downloader.download_audio(url)
            
            # Get video info for filename
            if not output_name:
                try:
                    video_info = self.downloader.get_video_info(url)
                    title = video_info.get('title', 'unknown')
                    output_name = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    output_name = output_name.replace(' ', '_')[:50]  # Limit length
                except:
                    output_name = "transcription"
            
            # Step 2: Preprocess audio
            logger.info("Preprocessing audio...")
            audio, sr, _ = self.preprocessor.preprocess_audio(audio_file)
            audio_stats = self.preprocessor.get_audio_stats(audio, sr)
            logger.info(f"Audio stats: {audio_stats}")
            
            # Step 3: Transcribe music
            logger.info("Transcribing music...")
            notes, tempo = self.transcriber.transcribe_audio(audio, sr)
            transcription_stats = self.transcriber.get_transcription_stats(notes)
            logger.info(f"Transcription stats: {transcription_stats}")
            
            # Step 4: Generate sheet music
            logger.info("Generating sheet music...")
            output_files = self.sheet_generator.generate_sheet_music(
                notes, tempo, str(self.output_dir), output_name
            )
            
            # Cleanup temporary files
            self.downloader.cleanup()
            
            # Prepare results
            results = {
                'success': True,
                'video_title': output_name,
                'audio_stats': audio_stats,
                'transcription_stats': transcription_stats,
                'estimated_tempo': tempo,
                'output_files': output_files,
                'message': f"Successfully transcribed {transcription_stats.get('total_notes', 0)} notes"
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            # Cleanup on error
            try:
                self.downloader.cleanup()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'message': f"Transcription failed: {str(e)}"
            }

@click.command()
@click.argument('url')
@click.option('--output', '-o', default=None, help='Output filename (without extension)')
@click.option('--output-dir', default='output', help='Output directory')
@click.option('--temp-dir', default='temp', help='Temporary directory')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(url, output, output_dir, temp_dir, verbose):
    """
    Convert YouTube music to sheet music notation.
    
    URL: YouTube URL to transcribe
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🎵 YouTube Music to Sheet Music Converter 🎵")
    print("=" * 50)
    
    # Validate URL
    if not ('youtube.com' in url or 'youtu.be' in url):
        print("❌ Error: Please provide a valid YouTube URL")
        sys.exit(1)
    
    # Initialize transcriber
    try:
        transcriber = YouTubeMusicTranscriber(output_dir, temp_dir)
    except Exception as e:
        print(f"❌ Error initializing transcriber: {e}")
        sys.exit(1)
    
    # Run transcription
    print(f"🔗 Processing URL: {url}")
    results = transcriber.transcribe_youtube_url(url, output)
    
    if results['success']:
        print("\n✅ Transcription completed successfully!")
        print(f"📊 Stats:")
        print(f"   - Duration: {results['audio_stats']['duration']:.1f} seconds")
        print(f"   - Notes detected: {results['transcription_stats']['total_notes']}")
        print(f"   - Estimated tempo: {results['estimated_tempo']:.1f} BPM")
        
        print(f"\n📁 Output files:")
        for format_type, file_path in results['output_files'].items():
            print(f"   - {format_type.upper()}: {file_path}")
        
        print(f"\n💡 Tip: Open the MusicXML file in MuseScore or similar software to view/edit the sheet music!")
        
    else:
        print(f"\n❌ Transcription failed: {results['message']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
