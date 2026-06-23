import re

from .section_chunker import section_chunking

MAX_CHARS = 4000


def recursive_split(text):
    if len(text) <= MAX_CHARS:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if not current:
            current = para
        elif len(current) + 2 + len(para) <= MAX_CHARS:
            current += "\n\n" + para
        else:
            chunks.append(current)
            current = para

    if current:
        chunks.append(current)

    return chunks


def _split_long_paragraph(paragraph):
    if len(paragraph) <= MAX_CHARS:
        return [paragraph]

    lines = [line for line in paragraph.split("\n") if line.strip()]
    chunks = []
    current = ""

    for line in lines:
        if not current:
            current = line
        elif len(current) + 1 + len(line) <= MAX_CHARS:
            current += "\n" + line
        else:
            chunks.append(current)
            current = line

    if current:
        chunks.append(current)

    if any(len(chunk) > MAX_CHARS for chunk in chunks):
        overflow = []
        for chunk in chunks:
            if len(chunk) <= MAX_CHARS:
                overflow.append(chunk)
            else:
                for i in range(0, len(chunk), MAX_CHARS):
                    overflow.append(chunk[i:i + MAX_CHARS])
        chunks = overflow

    return chunks


def _get_header_level(header):
    match = re.match(r"^\s*(\d+(?:\.\d+)*)", header)
    if not match:
        return 0

    return match.group(1).count(".") + 1


def recursive_chunking(raw_text):
    sections = section_chunking(raw_text)
    final_chunks = []
    chunk_id = 1

    for section in sections:
        section_header = section["header"]
        level = _get_header_level(section_header)
        paragraph_chunks = recursive_split(section["text"])

        for subsection_index, paragraph_chunk in enumerate(paragraph_chunks, start=1):
            subchunks = _split_long_paragraph(paragraph_chunk)

            for subchunk_index, subchunk in enumerate(subchunks, start=1):
                final_chunks.append({
                    "chunk_id": f"chunk_{chunk_id:04}",
                    "section": section_header,
                    "subsection": f"{section_header}_{subsection_index}.{subchunk_index}",
                    "level": level,
                    "text": subchunk.strip(),
                })
                chunk_id += 1

    return final_chunks
