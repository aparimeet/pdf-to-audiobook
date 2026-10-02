"""Normalize PDF-extracted text so Kokoro produces cleaner speech."""

from __future__ import annotations

import re
import unicodedata

# Common ebook watermark / site stamps that should never be spoken.
_WATERMARKS = (
    "OceanofPDF.com",
    "OceanofPDF",
    "www.oceanofpdf.com",
)

_HYPHEN_LINEBREAK = re.compile(r"([A-Za-z]{2,})-\n([A-Za-z]+)")
_SOFT_LINEBREAK = re.compile(r"(?<![.!?…:\"”'’])\n(?!\n)")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MULTI_BLANK = re.compile(r"\n{3,}")
# Lone page numbers on their own line (common PDF footer/header noise).
_PAGE_NUMBER_LINE = re.compile(r"(?m)^\s*\d{1,4}\s*$")


def _rejoin_hyphen_wrap(match: re.Match[str]) -> str:
    """Repair PDF line-wrap hyphens without destroying real compounds.

    Short right-hand fragments ("exam-\\nple") are syllable wraps → join.
    Longer fragments ("open-\\nsource") are usually compounds → keep hyphen.
    """
    left, right = match.group(1), match.group(2)
    if len(right) <= 3:
        return f"{left}{right}"
    return f"{left}-{right}"


def clean_text(content: str) -> str:
    """Clean extracted PDF text for higher-quality TTS.

    Why these transforms:
    - PDF extractors insert hard line breaks mid-sentence; Kokoro reads those
      as awkward pauses unless we rejoin them.
    - Hyphenated wrap breaks ("exam-\\nple") become wrong phonemes if left alone.
    - Watermarks and bare page numbers add junk speech.
    """
    if not content:
        return ""

    text = unicodedata.normalize("NFKC", content)

    for mark in _WATERMARKS:
        text = text.replace(mark, "")

    # Normalize quotes/dashes that often confuse phonemizers.
    text = (
        text.replace("“", '"')
        .replace("”", '"')
        .replace("„", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", " - ")
        .replace("…", "...")
    )

    text = _HYPHEN_LINEBREAK.sub(_rejoin_hyphen_wrap, text)
    text = _PAGE_NUMBER_LINE.sub("", text)
    # Soft-wrap newlines become spaces; blank lines stay as paragraph breaks.
    text = _SOFT_LINEBREAK.sub(" ", text)
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_BLANK.sub("\n\n", text)

    # Drop duplicate consecutive lines (headers/footers stamped on every page).
    lines = [line.strip() for line in text.splitlines()]
    deduped: list[str] = []
    prev = None
    for line in lines:
        if line and line == prev:
            continue
        deduped.append(line)
        prev = line if line else None

    text = "\n".join(deduped)
    text = _MULTI_BLANK.sub("\n\n", text).strip()
    return text


def _force_split(text: str, max_chars: int) -> list[str]:
    """Split an oversized fragment on spaces when sentence boundaries are absent."""
    words = text.split()
    if not words:
        return []
    pieces: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            pieces.append(current)
            current = word
    pieces.append(current)
    return pieces


def split_for_tts(text: str, max_chars: int = 450) -> list[str]:
    """Split cleaned text into paragraph/sentence chunks for stable prosody.

    Kokoro already phoneme-chunks long input, but feeding it short paragraph-
    sized pieces yields more natural pauses and recovers better from bad PDF
    glue. Chunks stay under ``max_chars`` when possible.
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[str] = []

    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
            continue

        sentences = re.split(r"(?<=[.!?…])\s+", paragraph)
        current = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(sentence) > max_chars:
                if current:
                    chunks.append(current)
                    current = ""
                chunks.extend(_force_split(sentence, max_chars))
                continue
            if not current:
                current = sentence
            elif len(current) + 1 + len(sentence) <= max_chars:
                current = f"{current} {sentence}"
            else:
                chunks.append(current)
                current = sentence
        if current:
            chunks.append(current)

    return chunks
