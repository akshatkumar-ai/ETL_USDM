import re

from .section_chunker import section_chunking


SEMANTIC_BOUNDARIES = [

    r"Primary Objective",

    r"Secondary Objective",

    r"Primary Endpoint",

    r"Secondary Endpoint",

    r"Inclusion Criteria",

    r"Exclusion Criteria",

    r"Study Procedures",

    r"Safety Assessments"
]


def split_semantically(text):

    pattern = "|".join(SEMANTIC_BOUNDARIES)

    splits = re.split(f"({pattern})",
                      text,
                      flags=re.IGNORECASE)

    chunks = []

    current = ""

    for piece in splits:

        if re.match(pattern,
                    piece,
                    re.IGNORECASE):

            if current.strip():

                chunks.append(current.strip())

            current = piece

        else:

            current += "\n" + piece


    if current.strip():

        chunks.append(current.strip())

    return chunks


def semantic_chunking(raw_text):

    sections = section_chunking(raw_text)

    final_chunks = []

    for section in sections:

        subchunks = split_semantically(
            section["text"]
        )

        for sub in subchunks:

            final_chunks.append({

                "header": section["header"],

                "text": sub
            })

    return final_chunks