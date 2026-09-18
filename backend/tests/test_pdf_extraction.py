from app.services.document_processor import (
    extract_clean_pages_from_pdf,
)


PDF_PATH = "uploads/6/final_expolaratory_project.pdf"


pages = extract_clean_pages_from_pdf(PDF_PATH)


print("PDF page extraction successful!")

print("-" * 50)

print(f"Pages containing text: {len(pages)}")


for page in pages[:5]:
    print("\n" + "=" * 50)
    print(f"PAGE {page['page_number']}")
    print("=" * 50)

    print(page["text"][:500])