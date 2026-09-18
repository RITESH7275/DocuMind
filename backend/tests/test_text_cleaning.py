from app.services.document_processor import (
    extract_text_from_pdf,
    clean_text,
)


PDF_PATH = "uploads/7/new_resume.pdf"


raw_text = extract_text_from_pdf(PDF_PATH)

cleaned_text = clean_text(raw_text)

print("TEXT CLEANING SUCCESSFUL!")
print("-" * 60)

print(cleaned_text[:5000])