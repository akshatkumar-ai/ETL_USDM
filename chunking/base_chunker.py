import re


# =========================================================
# COMMON HEADER PATTERNS
# =========================================================

HEADER_PATTERNS = [

    # 1 OBJECTIVES
    r"^\s*\d+\s+[A-Z][A-Z\s\-]{3,}$",

    # 5.1 STUDY DESIGN
    r"^\s*\d+(\.\d+)*\s+[A-Z][A-Z\s\-]{3,}$",

    # OBJECTIVES
    r"^[A-Z][A-Z\s\-]{3,}$",
]


# =========================================================
# HEADER DETECTION
# =========================================================

def is_header(line):

    line = line.strip()

    if not line:
        return False

    for pattern in HEADER_PATTERNS:

        if re.match(pattern, line):

            return True

    return False


# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()