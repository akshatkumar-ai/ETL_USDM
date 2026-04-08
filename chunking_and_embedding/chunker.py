# chunker.py

from config import CHUNK_SIZE, CHUNK_OVERLAP

import re


def is_heading(line: str) -> bool:
    line = line.strip()

    if not line:
        return False

    if len(line) < 80 and not line.endswith("."):
        if len(line.split()) <= 10:
            return True

    return False


def semantic_chunk(pages):
    """
    Chunk based on headings + fallback size chunking
    """
    chunks = []
    current_chunk = ""
    current_section = "Unknown"

    for page in pages:
        lines = page["text"].split("\n")

        for line in lines:
            if is_heading(line):
                if current_chunk:
                    chunks.append({
                        "section": current_section,
                        "text": current_chunk.strip()
                    })
                    current_chunk = ""

                current_section = line.strip()

            current_chunk += " " + line.strip()

            # fallback size-based split
            if len(current_chunk) > CHUNK_SIZE:
                chunks.append({
                    "section": current_section,
                    "text": current_chunk.strip()
                })
                current_chunk = current_chunk[-CHUNK_OVERLAP:]

    if current_chunk:
        chunks.append({
            "section": current_section,
            "text": current_chunk.strip()
        })

    return chunks