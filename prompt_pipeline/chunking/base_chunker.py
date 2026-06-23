import re


def is_header_like(line):

    line = line.strip()

    if not line:
        return False

    # ---------------------------------------------------
    # HARD EXCLUSIONS
    # ---------------------------------------------------

    if len(line) > 120:
        return False

    if re.search(r"[.;,:]$", line):
        return False

    # Dosage patterns
    if re.search(r"\b\d+\s?(mg|g|ml|mcg|kg|mmhg|bpm)\b", line, re.IGNORECASE):
        return False

    # Clinical IDs
    if re.search(r"\bNCT\d+\b", line):
        return False

    # Address-like
    if re.search(r"\b(St|Street|Rd|Road|Ave|Avenue|Blvd)\b", line):
        return False

    # Mostly numeric
    alpha_chars = sum(c.isalpha() for c in line)
    digit_chars = sum(c.isdigit() for c in line)

    if digit_chars > alpha_chars:
        return False

    # Table fragments
    if len(line.split()) <= 4 and "(" in line and ")" in line:
        return False

    # Chemical formulas
    if re.search(r"[\[\]\(\)\-]{2,}", line):
        return False

    # ---------------------------------------------------
    # HEADER SCORING
    # ---------------------------------------------------

    score = 0

    # Numbered section headers
    if re.match(r"^\d+(\.\d+)*\s+", line):
        score += 4

    # ALL CAPS short lines
    if line.isupper() and len(line.split()) <= 10:
        score += 3

    # Title Case
    if line == line.title():
        score += 2

    # Short lines
    if len(line.split()) <= 10:
        score += 1

    # No common verbs
    common_verbs = {
        "is", "are", "was", "were",
        "have", "has", "had",
        "will", "would", "should",
        "contains", "administered",
        "provided", "included"
    }

    lower_words = set(line.lower().split())

    if not common_verbs.intersection(lower_words):
        score += 1

    return score >= 4