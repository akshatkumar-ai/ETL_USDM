from .base_chunker import is_header


def section_chunking(raw_text):

    lines = raw_text.split("\n")

    sections = []

    current_header = "DOCUMENT_START"

    current_text = []


    for line in lines:

        if is_header(line):

            if current_text:

                sections.append({

                    "header": current_header,

                    "text": "\n".join(current_text)
                })

            current_header = line.strip()

            current_text = []

        else:

            current_text.append(line)


    if current_text:

        sections.append({

            "header": current_header,

            "text": "\n".join(current_text)
        })

    return sections