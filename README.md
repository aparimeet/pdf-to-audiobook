# PDF to Audiobook

A project to convert PDFs into audiobooks using text-to-speech technology.

## System Requirements

- **CPU**: Tested on 64-bit AMD64 CPU with 16GB RAM
- **Python**: Version 3.12.1

## Installation

### 1. Install PyTorch
Visit [PyTorch official website](https://pytorch.org/) for installation instructions.

### 2. Install Text-to-Speech Model
This project uses the [Suno Bark TTS model](https://huggingface.co/suno/bark) from Hugging Face.

### 3. Hugging Face Authentication
Before running the TTS script, you need to authenticate with Hugging Face:

```python
python3
>>> from huggingface_hub import login
>>> login()
# Enter your Hugging Face token when prompted
```

## Audio Processing

To stitch together the generated WAV files, install [FFmpeg](https://ffmpeg.org/).

## Usage

### 1. Create an Index File
Create a JSON file that defines the sections of your PDF with their corresponding page ranges. The file should follow this example format:

```json
{
    "Prologue" : {
        "start" : 6,
        "end" : 8
    },
    "Chapter 1" : {
        "start" : 11,
        "end" : 56
    },
    "Chapter 2" : {
        "start" : 58,
        "end" : 148
    },
    "Chapter 3" : {
        "start" : 150,
        "end" : 185
    },
    "Chapter 4" : {
        "start" : 187,
        "end" : 255
    },
    "Chapter 5" : {
        "start" : 257,
        "end" : 353
    }
}
```

Each key represents a chapter or section name, with `start` and `end` values indicating the page numbers for that section.

### 2. Extract Text
Run the extract text script with your PDF and index file:
```bash
python3 extract_text.py --pdf <path to PDF file> --index <path to page index json>
```

### 3. Generate Audio
Run the TTS conversion:
```bash
python3 tts.py
```
