# Excalidraw System Diagram Guide

## Main Components to Draw (Rectangles)

### Top Row (Input Layer):
1. **YouTube URL** (User Input) - Green rectangle
2. **CLI Interface** (main.py) - Blue rectangle
3. **YouTube Downloader** (yt-dlp) - Orange rectangle

### Middle Row (Processing Layer):
4. **Audio Preprocessor** (librosa) - Purple rectangle  
5. **Music Transcriber** (analysis) - Red rectangle
6. **Pitch Detection** - Small red rectangle
7. **Onset Detection** - Small red rectangle

### Bottom Row (Output Layer):
8. **Sheet Music Generator** (music21) - Teal rectangle
9. **MusicXML Output** - Light green rectangle
10. **MIDI Output** - Light blue rectangle
11. **PNG Output** (optional) - Light gray rectangle

## Data Flow Arrows:
- Use thick arrows to show main data flow
- Use dashed arrows for optional/alternative paths
- Add labels on arrows for data types:
  - "Raw Audio (.wav)"
  - "Clean Audio Array"  
  - "Frequency Data"
  - "Note Objects"
  - "Score Object"

## File System (Bottom):
- **temp/** folder - Gray rectangle (temporary files)
- **output/** folder - Green rectangle (final outputs)

## Color Scheme:
- **Input/User**: Green
- **CLI/Interface**: Blue  
- **Download/External**: Orange
- **Audio Processing**: Purple
- **Analysis/AI**: Red
- **Music Generation**: Teal
- **Outputs**: Light colors (green, blue, gray)
- **File System**: Gray/neutral

## Layout Suggestion:
```
[YouTube URL] → [CLI] → [Downloader]
      ↓               ↓
[Audio Preprocessor] → [Music Transcriber]
                           ↓
                    [Pitch] [Onset]
                           ↓
              [Sheet Music Generator]
                     ↓
        [XML] [MIDI] [PNG]
              ↓
    [temp/] [output/]
```

## Key Labels to Add:
- "User Input" (top)
- "Processing Pipeline" (middle section)
- "Audio Analysis" (transcriber section)
- "Output Generation" (bottom section)
- "File System" (storage section)

## Additional Elements:
- Add a title: "YouTube Music Transcriber - System Architecture"
- Use rounded rectangles for main components
- Use regular rectangles for data/files
- Add error handling flow with dashed red lines
- Include dependency labels (librosa, music21, yt-dlp)
