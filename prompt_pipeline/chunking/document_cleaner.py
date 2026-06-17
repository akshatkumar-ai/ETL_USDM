import re


def clean_document(raw_text):

    text = raw_text

    # --------------------------------------------------
    # Remove page markers
    # --------------------------------------------------

    text = re.sub(
        r"===== PAGE \d+ =====",
        "",
        text
    )

    # --------------------------------------------------
    # Remove page numbers
    # --------------------------------------------------

    text = re.sub(
        r"Page \d+ of \d+",
        "",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # Remove isolated confidentiality labels
    # --------------------------------------------------

    text = re.sub(
        r"CONFIDENTIA\s*L",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"CONFIDENTIAL",
        "",
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------
    # Remove excessive whitespace
    # --------------------------------------------------

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    # --------------------------------------------------
    # Fix broken line wrapping
    # --------------------------------------------------

    # text = re.sub(
    #     r"(?<!\n)\n(?!\n)",
    #     " ",
    #     text
    # )

    # --------------------------------------------------
    # Normalize paragraph spacing
    # --------------------------------------------------

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    # --------------------------------------------------
    # Clean repeated spaces
    # --------------------------------------------------

    # text = re.sub(
    #     r"\s{2,}",
    #     " ",
    #     text
    # )

    return text.strip()