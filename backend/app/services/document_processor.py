from pathlib import Path
import re

from pypdf import PdfReader # type: ignore


def extract_pages_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF while preserving page numbers.

    Returns:
        A list of dictionaries containing:
        - page_number
        - text
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {file_path}"
        )

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text()

        if text:
            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    return pages


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from all pages of a PDF.

    This function is kept for compatibility with
    existing parts of the application.
    """

    pages = extract_pages_from_pdf(file_path)

    return "\n\n".join(
        page["text"]
        for page in pages
    )


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.

    Removes excessive whitespace and normalizes
    line breaks while preserving paragraph structure.
    """

    if not text:
        return ""

    # Normalize Windows/Mac line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Replace tabs with spaces
    text = text.replace("\t", " ")

    # Remove excessive spaces
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove spaces at the beginning/end of lines
    text = "\n".join(
        line.strip()
        for line in text.split("\n")
    )

    # Collapse 3+ consecutive newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_clean_pages_from_pdf(
    file_path: str,
) -> list[dict]:
    """
    Extract and clean PDF text while preserving
    page numbers.
    """

    pages = extract_pages_from_pdf(file_path)

    cleaned_pages = []

    for page in pages:
        cleaned_text = clean_text(
            page["text"]
        )

        if cleaned_text:
            cleaned_pages.append(
                {
                    "page_number": page["page_number"],
                    "text": cleaned_text,
                }
            )

    return cleaned_pages