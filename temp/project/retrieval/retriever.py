def retrieve_chunks(
    query,
    chunks,
    top_k=5
):

    query_words = query.lower().split()

    scored_chunks = []

    for chunk in chunks:

        chunk_lower = chunk.lower()

        score = sum(
            word in chunk_lower
            for word in query_words
        )

        scored_chunks.append(
            (score, chunk)
        )

    scored_chunks.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    top_chunks = [
        chunk
        for score, chunk in scored_chunks[:top_k]
    ]

    return top_chunks