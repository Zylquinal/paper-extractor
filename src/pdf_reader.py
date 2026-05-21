import pdfplumber

from src.exceptions import PDFReadError


def extract_text(pdf_path: str) -> str:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = [page.extract_text() for page in pdf.pages]
    except FileNotFoundError:
        raise PDFReadError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise PDFReadError(f"Failed to open PDF '{pdf_path}': {e}")

    text = "\n\n".join(p for p in pages if p)
    if not text.strip():
        raise PDFReadError(
            "No extractable text found in PDF. "
            "The file may be a scanned image with no embedded text layer."
        )

    return text
