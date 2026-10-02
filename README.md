# PDF to Audiobook

Convert a PDF into a spoken audiobook with [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), an open-weight text-to-speech model.

## Stack

- **Python** 3.12
- **PyPDF2** for text extraction
- **Kokoro** + **PyTorch** for TTS
- **soundfile** / **NumPy** for WAV stitching

## Setup

```bash
# 1. Create a virtualenv and install PyTorch for your platform:
#    https://pytorch.org/
python3 -m venv .venv
source .venv/bin/activate
pip install torch

# 2. Install the remaining dependencies
pip install -r requirements.txt

# 3. (Optional) Log in to Hugging Face if model downloads require it
python -c "from huggingface_hub import login; login()"
```

## Page index

Create a JSON file that maps chapter names to page ranges. Values are **0-based**
indexes into the PDF (page 0 is the first page). Pass `--one-based` if you prefer
printed page numbers starting at 1.

```json
{
  "Prologue": { "start": 6, "end": 8 },
  "Chapter 1": { "start": 11, "end": 56 }
}
```

## Usage

### One command

```bash
python main.py all --pdf book.pdf --index chapters.json --output audiobook.wav
```

### Step by step

```bash
python main.py extract --pdf book.pdf --index chapters.json
python main.py speak --voice af_heart --speed 0.95
python main.py combine --output audiobook.wav
```

The individual scripts (`extract_text.py`, `tts.py`, `combine_wavs.py`) still work
and accept the same flags.

### Useful options

| Flag | Meaning |
|------|---------|
| `--voice af_heart` | Kokoro voice (default: `af_heart`) |
| `--lang a` / `b` | American / British English |
| `--speed 0.95` | Slightly slower narration for clarity |
| `--one-based` | Treat index pages as 1-based |
| `--write-chunks` | Also save per-paragraph WAVs |

## What improved

- **Simpler flow**: one `main.py` entry point runs extract → speak → combine.
- **Cleaner speech**: PDF line-wraps, hyphen breaks, watermarks, and bare page
  numbers are removed before synthesis; text is split on paragraphs/sentences
  for steadier prosody.
- **Better TTS defaults**: transformer G2P (`trf=True`), `af_heart` voice, and a
  slightly slower default speed.
- **Reliable stitching**: chapter audio is concatenated with NumPy/soundfile
  (no FFmpeg required). Short pauses are inserted between chunks and chapters.
- **Leaner deps**: `requirements.txt` lists only what the project imports.

## System notes

Tested with Python 3.12 and a 64-bit CPU. A GPU speeds up Kokoro but is optional.
