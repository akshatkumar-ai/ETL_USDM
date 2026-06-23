import re


# =========================================================
# SECTION → USDM CLASS MAPPING
# =========================================================

SECTION_TO_USDM = {

    "synopsis": [
        "study",
        "studyVersion",
        "studyTitle",
        "studyIdentifier"
    ],

    "background": [
        "indication",
        "studyVersion.rationale"
    ],

    "objectives": [
        "objective",
        "endpoint"
    ],

    "study_design": [
        "studyDesign",
        "studyArm",
        "studyEpoch",
        "studyCell"
    ],

    "eligibility": [
        "eligibilityCriterion",
        "studyDesignPopulation"
    ],

    "schedule": [
        "encounter",
        "activity",
        "scheduleTimeline",
        "timing"
    ],

    "interventions": [
        "studyIntervention",
        "administration"
    ],

    "statistics": [
        "estimand",
        "analysisPopulation"
    ],

    "amendments": [
        "studyAmendment"
    ],

    "organizations": [
        "organization",
        "studyRole"
    ]
}


# =========================================================
# SECTION HEADER PATTERNS
# =========================================================

SECTION_PATTERNS = {

    "synopsis":
        r"(SYNOPSIS|STUDY SYNOPSIS|PROTOCOL SYNOPSIS)",

    "background":
        r"(BACKGROUND|RATIONALE|INTRODUCTION)",

    "objectives":
        r"(OBJECTIVES?|ENDPOINTS?)",

    "study_design":
        r"(STUDY DESIGN|TRIAL DESIGN|OVERALL DESIGN)",

    "eligibility":
        r"(ELIGIBILITY CRITERIA|INCLUSION CRITERIA|EXCLUSION CRITERIA)",

    "schedule":
        r"(SCHEDULE OF ACTIVITIES|VISIT SCHEDULE|STUDY PROCEDURES)",

    "interventions":
        r"(INTERVENTIONS?|TREATMENTS?|DOSING)",

    "statistics":
        r"(STATISTICAL METHODS|STATISTICS|ANALYSIS PLAN)",

    "amendments":
        r"(AMENDMENTS?|PROTOCOL AMENDMENTS?)",

    "organizations":
        r"(SPONSOR|ORGANIZATION|GOVERNANCE)"
}


# =========================================================
# FIND ALL SECTION HEADERS
# =========================================================

def find_sections(raw_text):

    matches = []

    for section_name, pattern in SECTION_PATTERNS.items():

        for match in re.finditer(pattern, raw_text, re.IGNORECASE):

            matches.append({
                "section": section_name,
                "start": match.start()
            })

    # Sort by position in document
    matches = sorted(matches, key=lambda x: x["start"])

    return matches


# =========================================================
# CREATE SEMANTIC CHUNKS
# =========================================================

def chunk_document(raw_text):

    sections = find_sections(raw_text)

    chunks = []

    for i in range(len(sections)):

        current = sections[i]

        start = current["start"]

        # End = next section OR end of document
        if i + 1 < len(sections):
            end = sections[i + 1]["start"]
        else:
            end = len(raw_text)

        chunk_text = raw_text[start:end].strip()

        chunks.append({

            "section": current["section"],

            "text": chunk_text,

            "usdm_targets":
                SECTION_TO_USDM[current["section"]]
        })

    return chunks


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    with open("raw_protocol_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    chunks = chunk_document(raw_text)

    print(f"\n✅ Total Chunks: {len(chunks)}\n")

    for chunk in chunks:

        print("=" * 80)
        print("SECTION:", chunk["section"])
        print("USDM TARGETS:", chunk["usdm_targets"])
        print("-" * 80)

        print(chunk["text"][:1500])

        print("\n")