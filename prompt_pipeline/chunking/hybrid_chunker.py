from .hierarchical_chunker import (
    hierarchical_chunking
)

from .recursive_chunker import (
    recursive_chunking
)

from .semantic_chunker import (
    split_semantically
)

from .document_cleaner import (
    clean_document 
)

def hybrid_chunking(raw_text):

    cleaned_text = clean_document(raw_text)

    hierarchy = recursive_chunking(
        cleaned_text
    )

    final_chunks = []

    chunk_id = 1

    for section in hierarchy:

        semantic_subchunks = split_semantically(
            section["text"]
        )

        for idx, sub in enumerate(semantic_subchunks):

            final_chunks.append({

                "chunk_id": f"chunk_{chunk_id:04}",

                "section": section["header"],

                "subsection": f"{section['header']}_{idx+1}",

                "level": section["level"],

                "text": sub,

                
            })

            chunk_id += 1

    return final_chunks