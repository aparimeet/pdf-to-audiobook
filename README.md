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

Run the extract text script with pdf and index specified:
```bash
python3 extract_text.py --pdf <path to PDF file> --index <path to page index json>
```

Run the TTS conversion:
```bash
python3 tts.py
```
