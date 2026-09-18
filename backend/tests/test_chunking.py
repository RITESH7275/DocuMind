from app.services.chunker import chunk_text
from app.services.document_processor import (
    extract_text_from_pdf,
    clean_text,
)


PDF_PATH = "uploads/7/new_Resume.pdf"


# Extract PDF text
raw_text = extract_text_from_pdf(PDF_PATH)

# Clean text
cleaned_text = clean_text(raw_text)

# Create chunks
chunks = chunk_text(
    cleaned_text,
    chunk_size=1000,
    chunk_overlap=200,
)


print("CHUNKING SUCCESSFUL!")
print("-" * 60)

print(f"Total characters: {len(cleaned_text)}")
print(f"Total chunks: {len(chunks)}")

print("-" * 60)

for index, chunk in enumerate(chunks[:5], start=1):
    print(f"\nCHUNK {index}")
    print("-" * 40)
    print(chunk)