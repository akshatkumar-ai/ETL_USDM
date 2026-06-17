from .base_chunker import is_header_like


def section_chunking(raw_text):
    """
    Split document into sections using heuristic header detection.
    """

    lines = raw_text.split("\n")

    sections = []

    current_header = "DOCUMENT_START"

    current_content = []

    for raw_line in lines:

        line = raw_line.strip()

        # -----------------------------------------
        # Skip empty lines
        # -----------------------------------------

        if not line:
            continue

        # -----------------------------------------
        # Header Detection
        # -----------------------------------------

        if is_header_like(line):

            # Save previous section
            if current_content:

                section_text = "\n".join(current_content).strip()

                if section_text:

                    sections.append({

                        "header": current_header,

                        "text": section_text
                    })

            # Start new section
            current_header = line

            current_content = []

        else:

            current_content.append(line)

    # -----------------------------------------
    # Save final section
    # -----------------------------------------

    if current_content:

        section_text = "\n".join(current_content).strip()

        if section_text:

            sections.append({

                "header": current_header,

                "text": section_text
            })

    # -----------------------------------------
    # Merge tiny OCR-noise sections
    # -----------------------------------------

    cleaned_sections = []

    for section in sections:

        text = section["text"].strip()

        # Very tiny sections are usually noise
        if len(text) < 20 and cleaned_sections:

            cleaned_sections[-1]["text"] += "\n" + text

        else:

            cleaned_sections.append(section)

    return cleaned_sections