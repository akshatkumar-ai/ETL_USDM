from .hierarchical_chunker import (
    hierarchical_chunking
)

from .semantic_chunker import (
    split_semantically
)


def hybrid_chunking(raw_text):

    hierarchy = hierarchical_chunking(
        raw_text
    )

    final_chunks = []

    for section in hierarchy:

        semantic_subchunks = split_semantically(
            section["text"]
        )

        for sub in semantic_subchunks:

            final_chunks.append({

                "header": section["header"],

                "level": section["level"],

                "text": sub
            })

    return final_chunks