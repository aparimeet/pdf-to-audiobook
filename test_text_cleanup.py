"""Lightweight tests for PDF text cleanup (no model download required)."""

from text_cleanup import clean_text, split_for_tts


def test_rejoins_hyphenated_wraps_and_soft_breaks():
    raw = "This is an exam-\nple sentence that\nwas wrapped in the PDF."
    cleaned = clean_text(raw)
    assert "example" in cleaned
    assert "\n" not in cleaned
    assert "sentence that was wrapped" in cleaned


def test_keeps_compound_hyphens_across_wraps():
    raw = "A small open-\nsource tool."
    cleaned = clean_text(raw)
    assert "open-source" in cleaned
    assert "opensource" not in cleaned


def test_strips_watermark_and_page_numbers():
    raw = "Hello world.\n\n42\n\nOceanofPDF.com\n\nMore text."
    cleaned = clean_text(raw)
    assert "OceanofPDF" not in cleaned
    assert "42" not in cleaned
    assert "Hello world." in cleaned
    assert "More text." in cleaned


def test_split_for_tts_keeps_paragraphs_and_bounds_length():
    text = "First paragraph. It has two sentences.\n\n" + ("Word " * 200)
    chunks = split_for_tts(text, max_chars=120)
    assert chunks[0].startswith("First paragraph")
    assert all(len(chunk) <= 130 for chunk in chunks[1:])


if __name__ == "__main__":
    test_rejoins_hyphenated_wraps_and_soft_breaks()
    test_keeps_compound_hyphens_across_wraps()
    test_strips_watermark_and_page_numbers()
    test_split_for_tts_keeps_paragraphs_and_bounds_length()
    print("All text cleanup tests passed.")
