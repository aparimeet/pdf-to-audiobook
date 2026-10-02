"""Shared paths and defaults for the PDF → audiobook pipeline."""

PARSED_TEXT_FOLDER_NAME = "parsed_text"
AUDIO_CHUNKS_FOLDER_NAME = "audio_chunks"
AUDIO_OUTPUT_FOLDER_NAME = "audio_files"
CHAPTER_ORDER_FILENAME = "chapter_order.txt"

SAMPLE_RATE = 24_000
DEFAULT_VOICE = "af_heart"
DEFAULT_LANG = "a"
DEFAULT_SPEED = 0.95
# Short pause inserted between Kokoro chunks when stitching a chapter.
CHUNK_GAP_SECONDS = 0.18
# Longer pause between chapters in the final audiobook.
CHAPTER_GAP_SECONDS = 0.75
