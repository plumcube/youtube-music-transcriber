# YouTube Music Transcriber - System Diagram

## High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│   YouTube URL   │───▶│  Audio Download  │───▶│  Audio Processing   │───▶│ Music Transcriber│
│  (User Input)   │    │    (yt-dlp)      │    │   (Preprocessing)   │    │   (Analysis)     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘    └──────────────────┘
                                                                                      │
                                                                                      ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐    ┌──────────────────┐
│  Output Files   │◀───│ Sheet Music Gen  │◀───│   Note Segments     │◀───│  Pitch/Rhythm    │
│ (XML/MIDI/PNG)  │    │    (music21)     │    │   (Discrete Notes)  │    │   Detection      │
└─────────────────┘    └──────────────────┘    └─────────────────────┘    └──────────────────┘
```

## Detailed Component Diagram

```
                            YouTube Music Transcriber System
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                                                                                     │
    │  ┌─────────────┐                                                                    │
    │  │    CLI      │  User Interface Layer                                             │
    │  │  (main.py)  │                                                                    │
    │  └─────┬───────┘                                                                    │
    │        │                                                                            │
    │        ▼                                                                            │
    │  ┌─────────────┐                                                                    │
    │  │YouTubeMusicT│  Application Controller                                           │
    │  │ranscriber   │                                                                    │
    │  └─────┬───────┘                                                                    │
    │        │                                                                            │
    │        ▼                                                                            │
    │ ┌──────────────────────────────────────────────────────────────────────────────┐   │
    │ │                        Processing Pipeline                                   │   │
    │ │                                                                              │   │
    │ │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │   │
    │ │  │   YouTube   │    │    Audio    │    │   Music     │    │Sheet Music  │  │   │
    │ │  │ Downloader  │───▶│Preprocessor │───▶│Transcriber  │───▶│ Generator   │  │   │
    │ │  │ (yt-dlp)    │    │ (librosa)   │    │ (librosa)   │    │ (music21)   │  │   │
    │ │  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │   │
    │ └──────────────────────────────────────────────────────────────────────────────┘   │
    │                                                                                     │
    └─────────────────────────────────────────────────────────────────────────────────────┘

                                        │
                                        ▼
                          ┌─────────────────────────────┐
                          │        File System          │
                          │                             │
                          │  ┌─────────┐ ┌─────────┐   │
                          │  │ temp/   │ │ output/ │   │
                          │  │ .wav    │ │ .xml    │   │
                          │  │ files   │ │ .mid    │   │
                          │  │         │ │ .png    │   │
                          │  └─────────┘ └─────────┘   │
                          └─────────────────────────────┘
```

## Data Flow Diagram

```
┌─────────────┐
│YouTube URL  │
│"youtube.com"│
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌──────────────┐
│ yt-dlp      │───▶│  Raw Audio   │
│ Download    │    │  (.wav file) │
└─────────────┘    └──────┬───────┘
                          │
                          ▼
┌─────────────┐    ┌──────────────┐
│Audio Preproc│───▶│ Clean Audio  │
│• Normalize  │    │ (numpy array)│
│• Filter     │    │              │
│• Trim       │    │              │
└─────────────┘    └──────┬───────┘
                          │
                          ▼
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│Pitch Detect │───▶│  Frequencies │───▶│ MIDI Numbers │
│(librosa)    │    │  (Hz array)  │    │ (note array) │
└─────────────┘    └──────────────┘    └──────┬───────┘
                                              │
┌─────────────┐    ┌──────────────┐           │
│Onset Detect │───▶│  Time Points │           │
│(librosa)    │    │  (seconds)   │           │
└─────────────┘    └──────┬───────┘           │
                          │                   │
                          ▼                   ▼
                   ┌──────────────┐    ┌──────────────┐
                   │ Tempo (BPM)  │    │ Note Objects │
                   │   120.5      │    │ (pitch,time, │
                   │              │    │  duration)   │
                   └──────┬───────┘    └──────┬───────┘
                          │                   │
                          └─────────┬─────────┘
                                    ▼
                          ┌──────────────┐
                          │ music21      │
                          │ Score Object │
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐
            │.xml file │  │.mid file │  │.png file │
            │(MusicXML)│  │ (MIDI)   │  │(optional)│
            └──────────┘  └──────────┘  └──────────┘
```

## Component Interaction

```
    main.py (CLI)
         │
         ▼
YouTubeMusicTranscriber
         │
    ┌────┴─────┬─────────┬─────────────┐
    ▼          ▼         ▼             ▼
YouTube    Audio    Music       Sheet Music
Downloader Preproc  Transcriber Generator
    │          │         │             │
    │          │    ┌────┴────┐        │
    │          │    ▼         ▼        │
    │          │ Pitch    Onset        │
    │          │ Detect   Detect       │
    │          │    │         │        │
    │          │    └────┬────┘        │
    │          │         │             │
    └──────────┼─────────┼─────────────┘
               │         │
               ▼         ▼
           Temp Files  Output Files
           (.wav)      (.xml/.mid/.png)
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  Python 3.12 + Click (CLI) + Logging + Error Handling     │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                    Core Libraries                           │
│  • yt-dlp (YouTube download)                               │
│  • librosa (Audio analysis)                                │
│  • music21 (Music notation)                                │
│  • numpy/scipy (Numerical processing)                      │
│  • soundfile (Audio I/O)                                   │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   System Dependencies                       │
│  • FFmpeg (Audio processing)                               │
│  • Python Virtual Environment                              │
│  • File System (temp/ and output/ directories)            │
└─────────────────────────────────────────────────────────────┘
```

## Processing Flow States

```
[Start] ──▶ [URL Input] ──▶ [Validate URL] ──▶ [Download Audio]
   │                                              │
   │                                              ▼
   │                                         [Preprocess]
   │                                              │
   │                                              ▼
   │                                       [Pitch Analysis]
   │                                              │
   │                                              ▼
   │                                       [Rhythm Analysis]
   │                                              │
   │                                              ▼
   │                                       [Note Segmentation]
   │                                              │
   │                                              ▼
   │                                       [Generate Score]
   │                                              │
   │                                              ▼
   │                                       [Export Files]
   │                                              │
   │                                              ▼
   └─────────── [Error Handling] ◀─────────── [Success]
                      │
                      ▼
                   [Cleanup]
                      │
                      ▼
                    [End]
```
