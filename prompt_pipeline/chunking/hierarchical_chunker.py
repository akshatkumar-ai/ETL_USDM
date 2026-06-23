import re


def get_level(header):

    match = re.match(r"^(\d+(\.\d+)*)",
                     header)

    if not match:

        return 0

    return match.group(1).count(".")


def hierarchical_chunking(raw_text):

    lines = raw_text.split("\n")

    chunks = []

    stack = []

    current = None


    for line in lines:

        stripped = line.strip()

        if re.match(r"^\d+(\.\d+)*\s+",
                    stripped):

            level = get_level(stripped)

            current = {

                "header": stripped,

                "level": level,

                "text": ""
            }

            chunks.append(current)

        elif current:

            current["text"] += line + "\n"

    return chunks