"""Single entry point for PDF → text → speech → audiobook."""

from __future__ import annotations

import argparse

from combine_wavs import combine_chapters
from constants import (
    AUDIO_CHUNKS_FOLDER_NAME,
    DEFAULT_LANG,
    DEFAULT_SPEED,
    DEFAULT_VOICE,
    PARSED_TEXT_FOLDER_NAME,
)
from extract_text import extract_organize_pages
from tts import convert_folder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert a PDF into an audiobook with Kokoro TTS",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    extract = sub.add_parser("extract", help="Extract and clean chapter text from a PDF")
    extract.add_argument("--pdf", required=True, help="Path to the PDF file")
    extract.add_argument("--index", required=True, help="Path to the page index JSON file")
    extract.add_argument("--output-dir", default=PARSED_TEXT_FOLDER_NAME)
    extract.add_argument("--one-based", action="store_true")

    speak = sub.add_parser("speak", help="Convert parsed text chapters to speech")
    speak.add_argument("--text-dir", default=PARSED_TEXT_FOLDER_NAME)
    speak.add_argument("--audio-dir", default=AUDIO_CHUNKS_FOLDER_NAME)
    speak.add_argument("--voice", default=DEFAULT_VOICE)
    speak.add_argument("--lang", default=DEFAULT_LANG)
    speak.add_argument("--speed", type=float, default=DEFAULT_SPEED)
    speak.add_argument("--write-chunks", action="store_true")

    combine = sub.add_parser("combine", help="Combine chapter WAVs into one audiobook")
    combine.add_argument("--audio-dir", default=AUDIO_CHUNKS_FOLDER_NAME)
    combine.add_argument("--output", default="audiobook.wav")
    combine.add_argument("--gap", type=float, default=None)

    all_cmd = sub.add_parser("all", help="Run extract → speak → combine")
    all_cmd.add_argument("--pdf", required=True, help="Path to the PDF file")
    all_cmd.add_argument("--index", required=True, help="Path to the page index JSON file")
    all_cmd.add_argument("--output", default="audiobook.wav", help="Final audiobook path")
    all_cmd.add_argument("--text-dir", default=PARSED_TEXT_FOLDER_NAME)
    all_cmd.add_argument("--audio-dir", default=AUDIO_CHUNKS_FOLDER_NAME)
    all_cmd.add_argument("--voice", default=DEFAULT_VOICE)
    all_cmd.add_argument("--lang", default=DEFAULT_LANG)
    all_cmd.add_argument("--speed", type=float, default=DEFAULT_SPEED)
    all_cmd.add_argument("--one-based", action="store_true")
    all_cmd.add_argument("--write-chunks", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "extract":
        extract_organize_pages(
            args.pdf,
            args.index,
            args.output_dir,
            one_based=args.one_based,
        )
    elif args.command == "speak":
        convert_folder(
            args.text_dir,
            args.audio_dir,
            voice=args.voice,
            lang=args.lang,
            speed=args.speed,
            write_chunks=args.write_chunks,
        )
    elif args.command == "combine":
        kwargs = {}
        if args.gap is not None:
            kwargs["gap_seconds"] = args.gap
        combine_chapters(args.audio_dir, args.output, **kwargs)
    elif args.command == "all":
        extract_organize_pages(
            args.pdf,
            args.index,
            args.text_dir,
            one_based=args.one_based,
        )
        convert_folder(
            args.text_dir,
            args.audio_dir,
            voice=args.voice,
            lang=args.lang,
            speed=args.speed,
            write_chunks=args.write_chunks,
        )
        combine_chapters(args.audio_dir, args.output)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
