import json
import os

from utils.llm_call import llm_call


# =========================================================
# LOAD CHUNKS
# =========================================================

def load_chunks(path):

    with open(path, "r", encoding="utf-8") as f:

        return json.load(f)


# =========================================================
# BUILD PROMPT
# =========================================================

def build_memory_prompt(chunks):

    chunk_text = ""

    for chunk in chunks:

        chunk_text += f"""

CHUNK_ID: {chunk['chunk_id']}

SECTION: {chunk['section']}

TEXT:
{chunk['text']}

"""

    prompt = f"""
You are analyzing chunks extracted from a clinical trial protocol.

Your task is to build a semantic memory representation of the protocol.

The final downstream goal is population of a USDM-style
clinical study model.

USDM concepts typically include:
- Study
- StudyDesign
- Objectives
- Endpoints
- EligibilityCriteria
- StudyPopulation
- StudyIntervention
- StudyArm
- StudyEpoch
- Encounter
- Activity
- Assessment
- Schedule
- Timing
- AnalysisPopulation
- SafetyAssessments
- StatisticalAnalysis
- Organizations
- StudyRoles

You are NOT generating USDM objects yet.

Instead:

1. Organize chunks into high-level semantic groups
2. Group related protocol concepts together
3. Preserve clinical meaning
4. Associate chunk_ids with groups
5. Generate concise summaries

The groups may include:
- study_overview
- study_design
- objectives
- endpoints
- eligibility
- interventions
- safety
- assessments
- schedule
- statistics
- organizations
- efficacy
- analysis_sets
- visits
- procedures

Return ONLY valid JSON.

Each group should contain:
- summary
- chunk_ids

INPUT CHUNKS:

{chunk_text}
"""

    return prompt


# =========================================================
# BUILD MEMORY
# =========================================================

def build_semantic_memory(chunks):

    prompt = build_memory_prompt(chunks)

    response = llm_call(prompt)

    return response


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    chunks = load_chunks(
        "output/raw_chunks.json"
    )

    semantic_memory = build_semantic_memory(
        chunks
    )

    os.makedirs("output", exist_ok=True)

    with open(
        "output/semantic_memory.json",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(semantic_memory)

    print("\n✅ semantic_memory.json generated")