import fitz  # pymupdf


def extract_text(pdf_path):
    """
    Extract text from PDF while preserving page structure.
    
    Args:
        pdf_path (str): Path to PDF file
        
    Returns:
        str: Extracted text with page markers
    """

    doc = fitz.open(pdf_path)

    full_text = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        text = page.get_text("text")

        # Add clear page markers
        page_block = f"\n\n===== PAGE {page_num + 1} =====\n\n"
        page_block += text

        full_text.append(page_block)

    doc.close()

    return "\n".join(full_text)


if __name__ == "__main__":

    pdf_path = "/home/riya/USDM/usdm/prompt_pipeline/Protocol_IF001_CL201_draft_17Sept2025.pdf"

    text = extract_text(pdf_path)

    print(text[:5000])

    # Optional save
    with open("raw_protocol_text.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("\n Text extraction complete")