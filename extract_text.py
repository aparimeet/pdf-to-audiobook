"""Extract chapter text from a PDF using a page-index JSON file."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from PyPDF2 import PdfReader

from constants import CHAPTER_ORDER_FILENAME, PARSED_TEXT_FOLDER_NAME
from text_cleanup import clean_text


def _safe_filename(name: str) -> str:
    """Turn a chapter title into a filesystem-safe stem."""
    cleaned = re.sub(r"[^\w\s.-]", "", name, flags=re.UNICODE).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "section"


def load_index(file_path: str | Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as handle:
        index = json.load(handle)
    if not isinstance(index, dict) or not index:
        raise ValueError("Index JSON must be a non-empty object of chapter → {start, end}")
    return index


def extract_organize_pages(
    pdf_name: str | Path,
    index_file_name: str | Path,
    output_dir: str | Path = PARSED_TEXT_FOLDER_NAME,
    *,
    one_based: bool = False,
) -> list[Path]:
    """Extract text for each index entry and write cleaned ``.txt`` files.

    Page numbers in the index address ``PdfReader.pages`` directly (0-based)
    unless ``one_based=True``, in which case page 1 is the first PDF page.
    """
    reader = PdfReader(str(pdf_name))
    page_count = len(reader.pages)
    print(f"Total number of pages: {page_count}")

    index = load_index(index_file_name)
    out_root = Path(output_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    order: list[str] = []
    for key, value in index.items():
        start = int(value["start"])
        end = int(value["end"])
        if one_based:
            start -= 1
            end -= 1
        if start < 0 or end >= page_count or start > end:
            raise ValueError(
                f"Invalid page range for '{key}': start={value['start']}, "
                f"end={value['end']} (PDF has {page_count} pages, "
                f"{'1-based' if one_based else '0-based'} indexing)"
            )

        parts: list[str] = []
        for page in range(start, end + 1):
            page_text = reader.pages[page].extract_text() or ""
            parts.append(page_text)
        content = clean_text("\n".join(parts))

        stem = _safe_filename(key)
        out_path = out_root / f"{stem}.txt"
        out_path.write_text(content, encoding="utf-8")
        written.append(out_path)
        order.append(stem)
        print(f"Wrote {out_path} ({len(content)} chars, pages {start}-{end})")

    # Persist index order so combine/speak follow the book, not filesystem sort.
    (out_root / CHAPTER_ORDER_FILENAME).write_text("\n".join(order) + "\n", encoding="utf-8")
    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Extract text from a PDF into chapter files")
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    parser.add_argument("--index", required=True, help="Path to the page index JSON file")
    parser.add_argument(
        "--output-dir",
        default=PARSED_TEXT_FOLDER_NAME,
        help=f"Directory for chapter .txt files (default: {PARSED_TEXT_FOLDER_NAME})",
    )
    parser.add_argument(
        "--one-based",
        action="store_true",
        help="Treat index start/end as 1-based page numbers (default is 0-based)",
    )
    args = parser.parse_args(argv)
    extract_organize_pages(args.pdf, args.index, args.output_dir, one_based=args.one_based)


if __name__ == "__main__":
    main()
