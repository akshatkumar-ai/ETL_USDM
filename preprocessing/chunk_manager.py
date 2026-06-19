# import json
# import os
# import copy
# from chunking.section_chunker import section_chunking
# from chunking.semantic_chunker import semantic_chunking
# from chunking.hierarchical_chunker import hierarchical_chunking
# from chunking.llm_dynamic_chunker import llm_dynamic_chunking
# from chunking.recursive_chunker import recursive_chunking
# from chunking.hybrid_chunker import hybrid_chunking
# import config





# CHUNKING_STRATEGY = config.CHUNKING_STRATEGY  # Options: section, semantic, hierarchical, recursive, llm_dynamic, hybrid


# def chunk_document(raw_text,
#                    strategy="section"):

#     if strategy == "section":

#         return section_chunking(raw_text)

#     elif strategy == "semantic":

#         return semantic_chunking(raw_text)

#     elif strategy == "hierarchical":

#         return hierarchical_chunking(raw_text)

#     elif strategy == "recursive":

#         return recursive_chunking(raw_text)

#     elif strategy == "llm_dynamic":

#         return llm_dynamic_chunking(raw_text)

#     elif strategy == "hybrid":

#         return hybrid_chunking(raw_text)

#     else:

#         raise ValueError(
#             f"Unknown chunking strategy: {strategy}"
#         )

# if __name__ == "__main__":

#     with open(
#         "raw_protocol_text.txt",
#         "r",
#         encoding="utf-8"
#     ) as f:

#         raw_text = f.read()

#     chunks = chunk_document(
#         raw_text,
#         strategy=CHUNKING_STRATEGY
#     )

#     print(f"\n Total chunks: {len(chunks)}")

#     os.makedirs("output", exist_ok=True)

#     with open(
#         "output/raw_chunks_recurvsive.json",
#         "w",
#         encoding="utf-8"
#     ) as f:

#         json.dump(
#             chunks,
#             f,
#             indent=2,
#             ensure_ascii=False
#         )

#     print("\n✅ Raw chunks saved")

#     for chunk in chunks:

#         print("=" * 80)

#         print("SECTION:")
#         print(chunk["section"])

#         print("-" * 80)

#         print("SUBSECTION:")
#         print(chunk["subsection"])

#         print("-" * 80)

#         print("TEXT:")
#         print(chunk["text"][:500])


"""
===============================================================================
Hierarchical Document Chunking Pipeline
===============================================================================

Purpose:
--------
This module converts a raw text document into structured, hierarchy-aware chunks.
It is designed for documents with numbered sections (e.g., clinical protocols,
SAPs, CSRs) where preserving the relationship between sections and subsections
is important.

Overall Workflow:
-----------------

1. Text Preprocessing
   - Normalize whitespace and special characters.
   - Remove page numbers and OCR artifacts.
   - Clean potential header lines by removing table-of-content dots and
     trailing page numbers.

2. Header Detection
   - Identify valid document headers such as:
         3.4 Study Population
         3.4.2 Inclusion Criteria
   - Ignore false positives such as:
         2 weeks
         50 cm2
         1 month
   - Detect special sections like:
         Appendix
         Attachment
         References
         Table of Contents

3. Document Tree Construction
   - Convert the document into a tree of DocNode objects.
   - Each node represents a section and stores:
         - Header information
         - Section body text
         - Child subsections
         - Parent relationship

   Example:

       3 Study Design
           |
           +-- 3.1 Objectives
           |
           +-- 3.2 Population
                   |
                   +-- 3.2.1 Inclusion Criteria

4. Hierarchical Chunk Generation
   - Each section becomes an independent chunk.
   - Child section text is not merged into parent sections.
   - Very large sections are split while preserving their metadata.
   - Structural sections with children but no text are retained.

5. Post Processing
   - Remove trivial OCR noise.
   - Preserve meaningful short sections and hierarchy.

Output Format:
--------------
Each chunk contains metadata such as:

{
    "chunk_id": "chunk_0001",
    "section": "3 Study Design",
    "subsection": "3.1 Objectives",
    "level": 2,
    "parent_section": "3 Study Design",
    "text": "Section content..."
}

===============================================================================
"""
import json
import os
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

import config


CHUNKINGSTRATEGY = getattr(config, "CHUNKINGSTRATEGY", "hierarchical")
MAX_CHARS = getattr(config, "CHUNK_MAX_CHARS", 4000)
MIN_CHARS = getattr(config, "CHUNK_MIN_CHARS", 120)


PAGE_NOISE_RE = re.compile(
    r"^\s*(PAGE\s+\d+|Document Page\s+\d+|Page\s+\d+)\s*$",
    re.IGNORECASE,
)
TOC_DOTS_RE = re.compile(r"\.{2,}\s*\d+\s*$")
TRAILING_PAGE_RE = re.compile(r"\s+\d+\s*$")
PURE_PAGE_LINE_RE = re.compile(r"^\s*(PAGE\s+\d+|Document Page\s+\d+|Page\s+\d+)\s*$", re.I)

# Require hierarchical numbering, not plain quantities.
# Good: 3.4 Study Population / 3.4.2.2 Exclusion Criteria
# Bad: 2 weeks / 50 cm2 / 1 month
STRICT_HEADER_RE = re.compile(
    r"""
    ^
    (?P<number>\d+\.\d+(?:\.\d+)*\.?)      # require at least one dot: 3.4 or deeper
    \s+
    (?P<title>[A-Za-z].*?)                 # title must start with a letter
    $
    """,
    re.VERBOSE,
)

APPENDIX_HEADER_RE = re.compile(
    r"""
    ^
    (?:
        Attachment\s+[A-Z0-9.\-]+ |
        Appendix\s+[A-Z0-9.\-]+   |
        Schedule\s+of\s+Events    |
        Table\s+of\s+Contents(?:\s+\w+)?   |
        References
    )
    .*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

UNIT_LIKE_TITLE_RE = re.compile(
    r"""
    ^
    (?:
        days? | weeks? | months? | years? |
        mg | g | kg | ml | l | cm2 | cm | mm |
        bpm | sec | seconds? | hours?
    )
    $
    """,
    re.IGNORECASE | re.VERBOSE,
)

@dataclass
class DocNode:
    header: str
    level: int
    number: str = ""
    title: str = ""
    body_lines: List[str] = field(default_factory=list)
    children: List["DocNode"] = field(default_factory=list)
    parent: Optional["DocNode"] = None

    def body_text(self) -> str:
        return "\n".join(x for x in self.body_lines if x.strip()).strip()


def normalize_line(line: str) -> str:
    line = line.replace("\u00a0", " ")
    line = re.sub(r"\s+", " ", line).strip()
    return line


def clean_candidate_header(line: str) -> str:
    line = normalize_line(line)
    line = TOC_DOTS_RE.sub("", line)          # remove TOC leaders like ......13
    line = TRAILING_PAGE_RE.sub("", line)     # remove trailing page number if left behind
    return line.strip()

def is_noise(line: str) -> bool:
    if not line:
        return True
    if PURE_PAGE_LINE_RE.match(line):
        return True
    return False

def parse_header(line: str):
    line = clean_candidate_header(line)
    if not line or is_noise(line):
        return None

    if APPENDIX_HEADER_RE.match(line):
        return {
            "header": line,
            "number": "",
            "title": line,
            "level": 1,
        }

    m = STRICT_HEADER_RE.match(line)
    if not m:
        return None

    number = m.group("number").rstrip(".")
    title = m.group("title").strip()

    # Reject fake headers like "2 weeks", "50 cm2", "1 month"
    title_first_token = title.split()[0].strip(",;:").lower() if title else ""
    if UNIT_LIKE_TITLE_RE.match(title_first_token):
        return None

    # Reject extremely short/unit-like "titles"
    if len(title) < 4:
        return None

    level = number.count(".") + 1

    return {
        "header": f"{number}. {title}",
        "number": number,
        "title": title,
        "level": level,
    }


def build_document_tree(rawtext: str) -> DocNode:
    """
    Build a hierarchy from numbered headers.
    Root is synthetic and never emitted as a final chunk.
    """
    root = DocNode(header="DOCUMENT_ROOT", level=0)
    stack: List[DocNode] = [root]

    for raw in rawtext.splitlines():
        line = normalize_line(raw)
        if is_noise(line):
            continue

        header_info = parse_header(line)

        if header_info:
            node = DocNode(
                header=header_info["header"],
                number=header_info["number"],
                title=header_info["title"],
                level=header_info["level"],
            )

            while stack and stack[-1].level >= node.level:
                stack.pop()

            parent = stack[-1] if stack else root
            node.parent = parent
            parent.children.append(node)
            stack.append(node)
        else:
            stack[-1].body_lines.append(line)

    return root


def split_long_text(text: str, max_chars: int = MAX_CHARS) -> List[str]:
    """
    Generic size-based splitter used only after hierarchy is preserved.
    Split by paragraphs first, then by lines, then by hard cap.
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

    chunks: List[str] = []
    current = ""

    for para in paragraphs:
        proposal = f"{current}\n{para}".strip() if current else para
        if len(proposal) <= max_chars:
            current = proposal
        else:
            if current:
                chunks.append(current.strip())
            if len(para) <= max_chars:
                current = para
            else:
                for i in range(0, len(para), max_chars):
                    piece = para[i:i + max_chars].strip()
                    if piece:
                        chunks.append(piece)
                current = ""

    if current:
        chunks.append(current.strip())

    return chunks


def get_ancestry(node: DocNode) -> List[DocNode]:
    path = []
    cur = node.parent
    while cur and cur.level > 0:
        path.append(cur)
        cur = cur.parent
    return list(reversed(path))



def walk_and_emit(node: DocNode, out: List[Dict[str, Any]], chunk_id_start: int = 1) -> int:
    """
    Emission policy:
    1. Each node becomes one chunk using only its own body text.
    2. If a node body is too large, split that body after hierarchy is preserved.
    3. Recurse into children.
    """
    chunk_id = chunk_id_start

    if node.level > 0:
        body = node.body_text()

        if body:
            parts = split_long_text(body, MAX_CHARS)
            if len(parts) == 1:
                out.append(
                    {
                        "chunk_id": f"chunk_{chunk_id:04d}",
                        "section": get_ancestry(node)[0].header if get_ancestry(node) else node.header,
                        "subsection": node.header,
                        "level": node.level,
                        "parent_section": node.parent.header if node.parent else "",
                        "text": parts[0],
                    }
                )
                chunk_id += 1
            else:
                for idx, part in enumerate(parts, start=1):
                    out.append(
                        {
                            "chunk_id": f"chunk_{chunk_id:04d}",
                            "section": get_ancestry(node)[0].header if get_ancestry(node) else node.header,
                            "subsection": f"{node.header} [{idx}/{len(parts)}]",
                            "level": node.level,
                            "parent_section": node.parent.header if node.parent else "",
                            "text": part,
                        }
                    )
                    chunk_id += 1

        # If the node has little or no body but has children, emit a structural chunk too.
        elif node.children:
            out.append(
                {
                    "chunk_id": f"chunk_{chunk_id:04d}",
                    "section": get_ancestry(node)[0].header if get_ancestry(node) else node.header,
                    "subsection": node.header,
                    "level": node.level,
                    "parent_section": node.parent.header if node.parent else "",
                    "text": "",
                }
            )
            chunk_id += 1

    for child in node.children:
        chunk_id = walk_and_emit(child, out, chunk_id)

    return chunk_id


def postprocess_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Keep hierarchy, remove only trivial noise.
    Do NOT hard-code domain phrases.
    """
    cleaned: List[Dict[str, Any]] = []

    for ch in chunks:
        text = (ch.get("text") or "").strip()

        # Keep structural nodes if they have real headers and children may depend on them.
        if not text:
            cleaned.append(ch)
            continue

        # Remove very tiny pure-noise chunks, but do not drop meaningful short headers.
        if len(text) < MIN_CHARS:
            if re.fullmatch(r"[A-Za-z0-9.\- ]{1,20}", text):
                # usually OCR debris like isolated page artifacts
                continue

        cleaned.append(ch)

    return cleaned


def chunk_document(rawtext: str, strategy: str = "hierarchical") -> List[Dict[str, Any]]:
    """
    Header-driven hierarchical chunking.
    strategy is retained for compatibility, but hierarchical is the default and preferred path.
    """
    tree = build_document_tree(rawtext)
    chunks: List[Dict[str, Any]] = []
    walk_and_emit(tree, chunks, chunk_id_start=1)
    chunks = postprocess_chunks(chunks)
    return chunks


if __name__ == "__main__":
    with open("rawprotocoltext.txt", "r", encoding="utf-8") as f:
        rawtext = f.read()

    chunks = chunk_document(rawtext, strategy=CHUNKINGSTRATEGY)

    print(f"Total chunks: {len(chunks)}")
    os.makedirs("output", exist_ok=True)

    with open("output/raw_chunks_hierarchical.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print("Raw chunks saved to output/raw_chunks_hierarchical.json")

    for chunk in chunks[:20]:
        print("=" * 80)
        print("SECTION")
        print(chunk["section"])
        print("-" * 80)
        print("SUBSECTION")
        print(chunk["subsection"])
        print("-" * 80)
        print("TEXT")
        print(chunk["text"][:500])