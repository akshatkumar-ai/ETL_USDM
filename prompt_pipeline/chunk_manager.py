from chunking.section_chunker import section_chunking
from chunking.semantic_chunker import semantic_chunking
from chunking.hierarchical_chunker import hierarchical_chunking
from chunking.llm_dynamic_chunker import llm_dynamic_chunking
from chunking.recursive_chunker import recursive_chunking
from chunking.hybrid_chunker import hybrid_chunking






CHUNKING_STRATEGY = "hybrid"


def chunk_document(raw_text,
                   strategy="section"):

    if strategy == "section":

        return section_chunking(raw_text)

    elif strategy == "semantic":

        return semantic_chunking(raw_text)

    elif strategy == "hierarchical":

        return hierarchical_chunking(raw_text)

    elif strategy == "recursive":

        return recursive_chunking(raw_text)

    elif strategy == "llm_dynamic":

        return llm_dynamic_chunking(raw_text)

    elif strategy == "hybrid":

        return hybrid_chunking(raw_text)

    else:

        raise ValueError(
            f"Unknown chunking strategy: {strategy}"
        )

if __name__ == "__main__":

    with open(
        "raw_protocol_text.txt",
        "r",
        encoding="utf-8"
    ) as f:

        raw_text = f.read()

    chunks = chunk_document(
        raw_text,
        strategy=CHUNKING_STRATEGY
    )

    for chunk in chunks:

        print("=" * 80)

        print("HEADER:")
        print(chunk["header"])

        print("-" * 80)

        print("TEXT:")
        print(chunk["text"])