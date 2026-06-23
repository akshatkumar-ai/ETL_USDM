import re


# ---------------------------------------------------
# REMOVE PAGE MARKERS
# ---------------------------------------------------

def remove_page_markers(text):

    text = re.sub(
        r"=+\s*PAGE\s+\d+\s*=+",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text


# ---------------------------------------------------
# REMOVE FOOTER / HEADER NOISE
# ---------------------------------------------------

def remove_footer_noise(lines):

    cleaned = []

    skip_next_confidential = False

    for line in lines:

        line = line.strip()

        if not line:
            cleaned.append("")
            continue

        # Remove footer page count
        if re.match(r"^Page\s+\d+\s+of\s+\d+$", line):
            continue

        # Remove CONFIDENTIAL OCR noise
        if line.upper() in ["CONFIDENTIAL", "CONFIDENTIA"]:
            skip_next_confidential = True
            continue

        if skip_next_confidential and line.upper() == "L":
            skip_next_confidential = False
            continue

        # Remove protocol/version lines
        if re.match(r"^PSIL\d+.*Protocol.*$", line, re.IGNORECASE):
            continue

        cleaned.append(line)

    return cleaned


# ---------------------------------------------------
# GENERIC HEADER DETECTION
# ---------------------------------------------------

def is_header_like(line):

    line = line.strip()

    if not line:
        return False

    # Too long → likely paragraph
    if len(line) > 120:
        return False

    # Ends like normal sentence
    if re.search(r"[.;,:]$", line):
        return False

    score = 0

    # -----------------------------------
    # Numbered headers
    # -----------------------------------

    if re.match(r"^\d+(\.\d+)*\s+", line):
        score += 3

    # -----------------------------------
    # ALL CAPS short lines
    # -----------------------------------

    if line.isupper() and len(line.split()) <= 10:
        score += 3

    # -----------------------------------
    # Title Case
    # -----------------------------------

    if line == line.title():
        score += 2

    # -----------------------------------
    # Short lines
    # -----------------------------------

    if len(line.split()) <= 12:
        score += 1

    # -----------------------------------
    # No common verbs
    # -----------------------------------

    common_verbs = [
        "is", "are", "was", "were",
        "have", "has", "had",
        "will", "would", "should"
    ]

    lower_words = line.lower().split()

    if not any(v in lower_words for v in common_verbs):
        score += 1

    return score >= 4


# ---------------------------------------------------
# NORMALIZE WHITESPACE
# ---------------------------------------------------

def normalize_whitespace(lines):

    normalized = []

    for line in lines:

        line = re.sub(r"\s+", " ", line)

        normalized.append(line.strip())

    return normalized


# ---------------------------------------------------
# MERGE BROKEN LINES
# ---------------------------------------------------

def merge_broken_lines(lines):

    merged = []

    current = ""

    for line in lines:

        line = line.strip()

        if not line:

            if current:
                merged.append(current.strip())
                current = ""

            continue

        # ---------------------------------------
        # Preserve headers
        # ---------------------------------------

        if is_header_like(line):

            if current:
                merged.append(current.strip())
                current = ""

            merged.append(line)

            continue

        # ---------------------------------------
        # Preserve numbered lists
        # ---------------------------------------

        if re.match(r"^\d+\.", line):

            if current:
                merged.append(current.strip())

            current = line

            continue

        # ---------------------------------------
        # Merge wrapped text
        # ---------------------------------------

        if current:

            if not re.search(r"[.:!?]$", current):

                current += " " + line

            else:

                merged.append(current.strip())
                current = line

        else:

            current = line

    if current:
        merged.append(current.strip())

    return merged


# ---------------------------------------------------
# RESTORE STRUCTURE
# ---------------------------------------------------

def restore_structure(text):

    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    lines = text.split("\n")

    restored = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # -----------------------------------
        # Standalone headers
        # -----------------------------------

        if is_header_like(line):

            restored.append(f"\n{line}\n")

            continue

        # -----------------------------------
        # Numbered criteria
        # -----------------------------------

        line = re.sub(
            r"\s(?=\d+\.\s)",
            "\n",
            line
        )

        # -----------------------------------
        # Alpha sub-items
        # -----------------------------------

        line = re.sub(
            r"\s(?=[a-zA-Z]\.\s)",
            "\n",
            line
        )

        # -----------------------------------
        # Bullet points
        # -----------------------------------

        line = re.sub(
            r"\s*•\s*",
            "\n• ",
            line
        )

        # -----------------------------------
        # Notes
        # -----------------------------------

        line = re.sub(
            r"\s*o Note:",
            "\no Note:",
            line
        )

        restored.append(line)

    text = "\n".join(restored)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------

def preprocess_protocol_text(raw_text):

    # Step 1
    raw_text = remove_page_markers(raw_text)

    # Step 2
    lines = raw_text.split("\n")

    # Step 3
    lines = remove_footer_noise(lines)

    # Step 4
    lines = normalize_whitespace(lines)

    # Step 5
    lines = merge_broken_lines(lines)

    # Step 6
    text = "\n".join(lines)

    # Step 7
    text = restore_structure(text)

    return text


# ---------------------------------------------------
# TEST
# ---------------------------------------------------

if __name__ == "__main__":

    with open("raw_protocol_text.txt", "r", encoding="utf-8") as f:

        raw = f.read()

    processed = preprocess_protocol_text(raw)

    print(processed[:5000])

    with open("cleaned_protocol_text.txt", "w", encoding="utf-8") as f:

        f.write(processed)