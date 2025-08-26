"""
YouTube audio downloader module.
Downloads audio from YouTube URLs using yt-dlp.
"""

import os
import yt_dlp
from pathlib import Path
import logging

class YouTubeAudioDownloader:
    """Download audio from YouTube URLs."""
    
    def __init__(self, output_dir="temp"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configure yt-dlp options for audio extraction
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
        }
    
    def download_audio(self, url: str) -> str:
        """
        Download audio from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Path to downloaded audio file
            
        Raises:
            Exception: If download fails
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'unknown')
                
                # Sanitize filename
                safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                output_file = self.output_dir / f"{safe_title}.wav"
                
                # Update output template
                self.ydl_opts['outtmpl'] = str(self.output_dir / f"{safe_title}.%(ext)s")
                
                # Download
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl_download:
                    ydl_download.download([url])
                
                if output_file.exists():
                    return str(output_file)
                else:
                    raise Exception(f"Audio file not found after download: {output_file}")
                    
        except Exception as e:
            logging.error(f"Failed to download audio from {url}: {str(e)}")
            raise
    
    def get_video_info(self, url: str) -> dict:
        """
        Get video information without downloading.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video information dictionary
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            logging.error(f"Failed to extract video info from {url}: {str(e)}")
            raise
    
    def cleanup(self):
        """Remove temporary files."""
        for file in self.output_dir.glob("*"):
            if file.is_file():
                file.unlink()
