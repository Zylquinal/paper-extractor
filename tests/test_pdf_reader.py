import os

import pytest

from src.exceptions import PDFReadError
from src.pdf_reader import extract_text


def test_extract_text_from_valid_pdf(sample_pdf_path):
    text = extract_text(sample_pdf_path)
    assert len(text) > 0
    assert "Predicting Crime Time Interval" in text


def test_extract_text_file_not_found():
    with pytest.raises(PDFReadError, match="not found"):
        extract_text("/nonexistent/path/to/file.pdf")


def test_extract_text_corrupt_pdf(tmp_path):
    corrupt_path = tmp_path / "corrupt.pdf"
    corrupt_path.write_text("this is not a real PDF file")
    with pytest.raises(PDFReadError, match="Failed to open PDF"):
        extract_text(str(corrupt_path))


def test_extract_text_image_only_pdf(tmp_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    blank_path = tmp_path / "blank.pdf"
    c = canvas.Canvas(str(blank_path), pagesize=letter)
    c.showPage()
    c.save()

    with pytest.raises(PDFReadError, match="No extractable text"):
        extract_text(str(blank_path))
