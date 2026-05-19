MAX_CHARS = 4000


def recursive_split(text):

    if len(text) <= MAX_CHARS:

        return [text]

    paragraphs = text.split("\n\n")

    chunks = []

    current = ""


    for para in paragraphs:

        if len(current) + len(para) < MAX_CHARS:

            current += "\n\n" + para

        else:

            chunks.append(current)

            current = para


    if current:

        chunks.append(current)

    return chunks


def recursive_chunking(raw_text):

    chunks = recursive_split(raw_text)

    return [

        {
            "header": f"recursive_chunk_{i}",

            "text": chunk
        }

        for i, chunk in enumerate(chunks)
    ]