"""Convert extracted chapter text into WAV chunks with Kokoro TTS."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

from constants import (
    AUDIO_CHUNKS_FOLDER_NAME,
    CHAPTER_ORDER_FILENAME,
    CHUNK_GAP_SECONDS,
    DEFAULT_LANG,
    DEFAULT_SPEED,
    DEFAULT_VOICE,
    PARSED_TEXT_FOLDER_NAME,
    SAMPLE_RATE,
)
from text_cleanup import clean_text, split_for_tts


def _ordered_text_files(text_root: Path) -> list[Path]:
    files = {p.stem: p for p in text_root.iterdir() if p.suffix.lower() == ".txt"}
    order_path = text_root / CHAPTER_ORDER_FILENAME
    if order_path.is_file():
        ordered: list[Path] = []
        for stem in order_path.read_text(encoding="utf-8").splitlines():
            stem = stem.strip()
            if stem and stem in files:
                ordered.append(files.pop(stem))
        ordered.extend(sorted(files.values(), key=lambda p: p.name.lower()))
        return ordered
    return sorted(files.values(), key=lambda p: p.name.lower())


def _silence(seconds: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


def _to_wave(audio) -> np.ndarray:
    """Convert a Kokoro/torch audio tensor to a 1-D float32 NumPy array."""
    if audio is None:
        return np.zeros(0, dtype=np.float32)
    if hasattr(audio, "detach"):
        audio = audio.detach().cpu().numpy()
    wave = np.asarray(audio, dtype=np.float32).reshape(-1)
    return wave


def build_pipeline(lang_code: str = DEFAULT_LANG, *, use_transformer_g2p: bool = True) -> KPipeline:
    """Create a Kokoro pipeline.

    ``trf=True`` uses Misaki's transformer G2P for English, which improves
    pronunciation of uncommon words compared to the default rule-based path.
    Falls back to rule-based G2P if the transformer extras are unavailable.
    """
    try:
        return KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M", trf=use_transformer_g2p)
    except Exception as exc:  # pragma: no cover - depends on optional spaCy model
        if not use_transformer_g2p:
            raise
        print(f"Transformer G2P unavailable ({exc}); falling back to rule-based G2P")
        return KPipeline(lang_code=lang_code, repo_id="hexgrad/Kokoro-82M", trf=False)


def synthesize_text(
    pipeline: KPipeline,
    text: str,
    *,
    voice: str = DEFAULT_VOICE,
    speed: float = DEFAULT_SPEED,
) -> np.ndarray:
    """Synthesize one chapter's text into a single float32 mono waveform."""
    cleaned = clean_text(text)
    chunks = split_for_tts(cleaned)
    if not chunks:
        return np.zeros(0, dtype=np.float32)

    audio_parts: list[np.ndarray] = []
    gap = _silence(CHUNK_GAP_SECONDS)

    for index, chunk in enumerate(chunks):
        print(f"  chunk {index + 1}/{len(chunks)} ({len(chunk)} chars)")
        # Feed one paragraph/sentence group at a time; disable Kokoro's own
        # newline split so our chunking controls the pauses.
        for result in pipeline(chunk, voice=voice, speed=speed, split_pattern=None):
            wave = _to_wave(result.audio)
            if wave.size == 0:
                continue
            if audio_parts:
                audio_parts.append(gap)
            audio_parts.append(wave)

    if not audio_parts:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(audio_parts)


def convert_folder(
    text_dir: str | Path = PARSED_TEXT_FOLDER_NAME,
    audio_dir: str | Path = AUDIO_CHUNKS_FOLDER_NAME,
    *,
    voice: str = DEFAULT_VOICE,
    lang: str = DEFAULT_LANG,
    speed: float = DEFAULT_SPEED,
    write_chunks: bool = False,
) -> list[Path]:
    """Convert every ``.txt`` in ``text_dir`` to a chapter WAV under ``audio_dir``."""
    text_root = Path(text_dir)
    audio_root = Path(audio_dir)
    audio_root.mkdir(parents=True, exist_ok=True)

    files = _ordered_text_files(text_root)
    if not files:
        raise FileNotFoundError(f"No .txt files found in {text_root}")

    print(f"Loading Kokoro pipeline (lang={lang}, voice={voice}, speed={speed})")
    pipeline = build_pipeline(lang)

    order_src = text_root / CHAPTER_ORDER_FILENAME
    if order_src.is_file():
        (audio_root / CHAPTER_ORDER_FILENAME).write_text(
            order_src.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    outputs: list[Path] = []
    for path in files:
        stem = path.stem
        print(f"Converting {path.name} to speech")
        text = path.read_text(encoding="utf-8")

        if write_chunks:
            chunk_dir = audio_root / stem
            chunk_dir.mkdir(parents=True, exist_ok=True)
            cleaned = clean_text(text)
            parts = split_for_tts(cleaned)
            chapter_parts: list[np.ndarray] = []
            gap = _silence(CHUNK_GAP_SECONDS)
            for i, chunk in enumerate(parts):
                piece_parts: list[np.ndarray] = []
                for result in pipeline(chunk, voice=voice, speed=speed, split_pattern=None):
                    wave = _to_wave(result.audio)
                    if wave.size:
                        piece_parts.append(wave)
                if not piece_parts:
                    continue
                piece = np.concatenate(piece_parts)
                sf.write(chunk_dir / f"{i}.wav", piece, SAMPLE_RATE)
                if chapter_parts:
                    chapter_parts.append(gap)
                chapter_parts.append(piece)
            audio = np.concatenate(chapter_parts) if chapter_parts else np.zeros(0, dtype=np.float32)
        else:
            audio = synthesize_text(pipeline, text, voice=voice, speed=speed)

        out_path = audio_root / f"{stem}.wav"
        sf.write(out_path, audio, SAMPLE_RATE)
        outputs.append(out_path)
        duration = len(audio) / SAMPLE_RATE if len(audio) else 0.0
        print(f"  saved {out_path} ({duration:.1f}s)")

    return outputs


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Convert parsed chapter text to speech with Kokoro")
    parser.add_argument(
        "--text-dir",
        default=PARSED_TEXT_FOLDER_NAME,
        help=f"Directory of chapter .txt files (default: {PARSED_TEXT_FOLDER_NAME})",
    )
    parser.add_argument(
        "--audio-dir",
        default=AUDIO_CHUNKS_FOLDER_NAME,
        help=f"Directory for chapter WAV output (default: {AUDIO_CHUNKS_FOLDER_NAME})",
    )
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Kokoro voice id (default: {DEFAULT_VOICE})")
    parser.add_argument("--lang", default=DEFAULT_LANG, help="Kokoro lang_code: a=US, b=UK (default: a)")
    parser.add_argument(
        "--speed",
        type=float,
        default=DEFAULT_SPEED,
        help=f"Speech speed multiplier (default: {DEFAULT_SPEED} for clearer narration)",
    )
    parser.add_argument(
        "--write-chunks",
        action="store_true",
        help="Also write per-paragraph chunk WAVs (legacy layout) under audio-dir/<chapter>/",
    )
    args = parser.parse_args(argv)

    # Keep cwd-relative defaults working the same way as before.
    os.makedirs(args.audio_dir, exist_ok=True)
    convert_folder(
        args.text_dir,
        args.audio_dir,
        voice=args.voice,
        lang=args.lang,
        speed=args.speed,
        write_chunks=args.write_chunks,
    )


if __name__ == "__main__":
    main()
