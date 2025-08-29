# YouTube Music to Sheet Music Converter

This application converts YouTube music videos into sheet music notation using audio analysis and machine learning techniques.

## Features

- 📥 Download audio from YouTube URLs
- 🎵 Analyze audio to detect musical notes and rhythm
- 🎼 Generate sheet music in multiple formats (MusicXML, MIDI)
- 🎯 Estimate tempo and key signature
- 🖥️ Simple command-line interface

## Requirements

- Python 3.9+
- FFmpeg (for audio processing)
- Virtual environment (recommended)

## Installation

1. Clone or download this project
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic usage:
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### With custom output name:
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --output "my_song"
```

### With verbose output:
```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID" --verbose
```

### All options:
```bash
python main.py --help
```

## Output Formats

The application generates sheet music in multiple formats:

- **MusicXML** (.xml) - Standard format, compatible with MuseScore, Sibelius, etc.
- **MIDI** (.mid) - For playback and further processing
- **PNG** (.png) - Visual sheet music (requires MuseScore installation)

## How It Works

1. **Audio Extraction**: Downloads audio from YouTube using yt-dlp
2. **Preprocessing**: Normalizes audio, removes noise, trims silence
3. **Pitch Detection**: Uses librosa to detect fundamental frequencies
4. **Note Segmentation**: Groups pitches into discrete musical notes
5. **Rhythm Analysis**: Detects note onsets and estimates tempo
6. **Sheet Music Generation**: Creates notation using music21 library

## Limitations

- Works best with monophonic (single melody line) music
- Complex harmonies or multiple instruments may not transcribe accurately
- Audio quality affects transcription accuracy
- Rhythm detection may not be perfect for complex rhythms

## Example Output

After processing, you'll find files in the `output/` directory:
- `song_name.xml` - MusicXML for music notation software
- `song_name.mid` - MIDI file for playback
- `song_name.png` - Sheet music image (if MuseScore is installed)

## Tips for Best Results

- Use videos with clear, single-instrument melodies
- Avoid videos with heavy background music or vocals
- Piano, flute, or violin solos work particularly well
- Shorter clips (30 seconds to 2 minutes) process faster

## Troubleshooting

### "FFmpeg not found" error
Install FFmpeg on your system:
- **Ubuntu/Debian**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/

### "No notes detected" error
- Try a different video with clearer melody
- Check if the audio is primarily instrumental
- Ensure the video has actual music content

### Import errors
Make sure you're in the virtual environment and all dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Development

Project structure:
```
youtube-music-transcriber/
├── src/
│   ├── audio/
│   │   ├── youtube_downloader.py  # YouTube audio extraction
│   │   └── preprocessor.py        # Audio preprocessing
│   ├── transcription/
│   │   └── analyzer.py            # Music analysis & transcription
│   └── sheet_music/
│       └── generator.py           # Sheet music generation
├── main.py                        # Main CLI application
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please respect YouTube's terms of service when downloading content.

## Disclaimer

This tool is for educational and personal use. Ensure you have the right to download and process the audio content you're using.
