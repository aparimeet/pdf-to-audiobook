"""Stitch chapter WAV files into a single audiobook."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import soundfile as sf

from constants import (
    AUDIO_CHUNKS_FOLDER_NAME,
    AUDIO_OUTPUT_FOLDER_NAME,
    CHAPTER_GAP_SECONDS,
    CHAPTER_ORDER_FILENAME,
    CHUNK_GAP_SECONDS,
    PARSED_TEXT_FOLDER_NAME,
    SAMPLE_RATE,
)


def _silence(seconds: float, sample_rate: int) -> np.ndarray:
    return np.zeros(int(seconds * sample_rate), dtype=np.float32)


def _natural_key(path: Path):
    parts = re.split(r"(\d+)", path.stem)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def _load_mono(path: Path) -> tuple[np.ndarray, int]:
    audio, rate = sf.read(path, always_2d=False)
    audio = np.asarray(audio, dtype=np.float32)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return audio, rate


def combine_chunk_dir(chunk_dir: Path, output_path: Path, gap_seconds: float = CHUNK_GAP_SECONDS) -> Path:
    """Combine numbered chunk WAVs inside a directory into one chapter WAV."""
    wavs = sorted(
        (p for p in chunk_dir.iterdir() if p.suffix.lower() == ".wav"),
        key=_natural_key,
    )
    if not wavs:
        raise FileNotFoundError(f"No WAV chunks in {chunk_dir}")

    parts: list[np.ndarray] = []
    rate = SAMPLE_RATE
    gap = None
    for wav in wavs:
        audio, rate = _load_mono(wav)
        if gap is None:
            gap = _silence(gap_seconds, rate)
        elif parts:
            parts.append(gap)
        parts.append(audio)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, np.concatenate(parts), rate)
    return output_path


def _load_chapter_order(*search_dirs: Path) -> list[str]:
    for directory in search_dirs:
        order_path = directory / CHAPTER_ORDER_FILENAME
        if order_path.is_file():
            return [line.strip() for line in order_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return []


def _order_paths(paths: list[Path], order: list[str]) -> list[Path]:
    if not order:
        return sorted(paths, key=_natural_key)
    by_stem = {p.stem: p for p in paths}
    ordered: list[Path] = []
    for stem in order:
        if stem in by_stem:
            ordered.append(by_stem.pop(stem))
    ordered.extend(sorted(by_stem.values(), key=_natural_key))
    return ordered


def combine_chapters(
    audio_dir: str | Path = AUDIO_CHUNKS_FOLDER_NAME,
    output_path: str | Path = "audiobook.wav",
    *,
    gap_seconds: float = CHAPTER_GAP_SECONDS,
) -> Path:
    """Combine chapter WAVs (or legacy chunk folders) into one audiobook file.

    Supports both layouts produced by ``tts.py``:
    - ``audio_chunks/Chapter.wav`` (preferred)
    - ``audio_chunks/Chapter/0.wav, 1.wav, ...`` (legacy)
    """
    root = Path(audio_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"Audio directory not found: {root}")

    order = _load_chapter_order(Path(PARSED_TEXT_FOLDER_NAME), root)
    chapter_wavs = _order_paths(
        [p for p in root.iterdir() if p.is_file() and p.suffix.lower() == ".wav"],
        order,
    )
    chunk_dirs = _order_paths([p for p in root.iterdir() if p.is_dir()], order)

    assembled: list[Path] = []
    staging = Path(AUDIO_OUTPUT_FOLDER_NAME)
    staging.mkdir(parents=True, exist_ok=True)

    if chapter_wavs:
        assembled = chapter_wavs
    else:
        for chunk_dir in chunk_dirs:
            out = staging / f"{chunk_dir.name}.wav"
            combine_chunk_dir(chunk_dir, out)
            assembled.append(out)
            print(f"Combined chunks → {out}")

    if not assembled:
        raise FileNotFoundError(f"No chapter audio found under {root}")

    parts: list[np.ndarray] = []
    rate = SAMPLE_RATE
    gap = None
    for path in assembled:
        audio, rate = _load_mono(path)
        if gap is None:
            gap = _silence(gap_seconds, rate)
        elif parts:
            parts.append(gap)
        parts.append(audio)
        print(f"Adding {path.name} ({len(audio) / rate:.1f}s)")

    out = Path(output_path)
    sf.write(out, np.concatenate(parts), rate)
    print(f"Wrote {out} ({sum(len(p) for p in parts) / rate:.1f}s)")
    return out


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Combine chapter WAV files into an audiobook")
    parser.add_argument(
        "--audio-dir",
        default=AUDIO_CHUNKS_FOLDER_NAME,
        help=f"Directory with chapter WAVs or chunk folders (default: {AUDIO_CHUNKS_FOLDER_NAME})",
    )
    parser.add_argument(
        "--output",
        default="audiobook.wav",
        help="Path for the final audiobook WAV (default: audiobook.wav)",
    )
    parser.add_argument(
        "--gap",
        type=float,
        default=CHAPTER_GAP_SECONDS,
        help=f"Silence between chapters in seconds (default: {CHAPTER_GAP_SECONDS})",
    )
    args = parser.parse_args(argv)
    combine_chapters(args.audio_dir, args.output, gap_seconds=args.gap)


if __name__ == "__main__":
    main()
