from doctest import master
import json
import copy

from typing import Any, Dict, List, Optional, Union

# =========================================================
# USDM CLASS → JSON PATH
# =========================================================

USDM_CLASS_PATHS: Dict[str, List[Union[str, int]]] = {

    # Top-level study
    "study":
        ["study"],

    "studyVersion":
        ["study", "versions"],

    "studyTitle":
        ["study", "versions", 0, "titles"],

    "studyIdentifier":
        ["study", "versions", 0, "studyIdentifiers"],

    "referenceIdentifier":
        ["study", "versions", 0, "referenceIdentifiers"],

    # Study design — common
    "studyDesign":
        ["study", "versions", 0, "studyDesigns"],

    "interventionalStudyDesign":
        ["study", "versions", 0, "studyDesigns"],

    "observationalStudyDesign":
        ["study", "versions", 0, "studyDesigns"],

    # Within studyDesign[0]
    "indication":
        ["study", "versions", 0, "studyDesigns", 0, "indications"],

    "objective":
        ["study", "versions", 0, "studyDesigns", 0, "objectives"],

    "endpoint":
        ["study", "versions", 0, "studyDesigns", 0, "objectives", 0, "endpoints"],

    "estimand":
        ["study", "versions", 0, "studyDesigns", 0, "estimands"],

    "intercurrentEvent":
        ["study", "versions", 0, "studyDesigns", 0, "estimands", 0, "intercurrentEvents"],

    "studyArm":
        ["study", "versions", 0, "studyDesigns", 0, "arms"],

    "studyEpoch":
        ["study", "versions", 0, "studyDesigns", 0, "epochs"],

    "studyCell":
        ["study", "versions", 0, "studyDesigns", 0, "studyCells"],

    "studyElement":
        ["study", "versions", 0, "studyDesigns", 0, "elements"],

    "eligibilityCriterion":
        ["eligibilityCriteria"],                               # top-level in schema

    "studyDesignPopulation":
        ["study", "versions", 0, "studyDesigns", 0, "population"],

    "populationDefinition":
        ["study", "versions", 0, "studyDesigns", 0, "population"],

    "encounter":
        ["study", "versions", 0, "studyDesigns", 0, "encounters"],

    "activity":
        ["study", "versions", 0, "studyDesigns", 0, "activities"],

    "scheduleTimeline":
        ["scheduleTimelines"],                                  # top-level in schema

    "timing":
        ["study", "versions", 0, "studyDesigns", 0, "timings"],

    "scheduleTimelineExit":
        ["study", "versions", 0, "studyDesigns", 0, "scheduleTimelineExits"],

    "studyIntervention":
        ["studyInterventions"],                                 # top-level in schema

    "administrableProduct":
        ["administrableProducts"],                              # top-level in schema

    "administration":
        ["study", "versions", 0, "studyDesigns", 0, "administrations"],

    "strength":
        ["study", "versions", 0, "studyDesigns", 0, "strengths"],

    "substance":
        ["study", "versions", 0, "studyDesigns", 0, "substances"],

    "BiomedicalConcept":
        ["biomedicalConcepts"],                                 # top-level in schema

    "BiomedicalConceptCategory":
        ["bcCategories"],

    "Procedure":
        ["study", "versions", 0, "studyDesigns", 0, "procedures"],

    "BiospecimenRetention":
        ["study", "versions", 0, "studyDesigns", 0, "biospecimenRetentions"],

    "analysisPopulation":
        ["analysisPopulations"],                                # top-level in schema

    "studyAmendment":
        ["study", "versions", 0, "amendments"],

    "studyChange":
        ["study", "versions", 0, "studyChanges"],

    "Organization":
        ["organizations"],                                      # top-level in schema

    "address":
        ["organizations", 0, "legalAddress"],

    "studyRole":
        ["study", "versions", 0, "studyRoles"],

    "studySite":
        ["study", "versions", 0, "studySites"],

    "GeographicScope":
        ["study", "versions", 0, "geographicScopes"],

    "GovernanceDate":
        ["study", "versions", 0, "dateValues"],

    "narrativeContent":
        ["documentedBy"],

    "DocumentContentReference":
        ["documentedBy", 0, "documentContentReferences"],

    "syntaxTemplate":
        ["study", "versions", 0, "studyDesigns", 0, "syntaxTemplates"],

    "dictionaries":
        ["dictionaries"],

    "conditions":
        ["conditions"],

    "notes":
        ["notes"],
}



# ── Template loading ───────────────────────────────────────────────────────────

def load_template(template_path: str) -> Dict:
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Path helpers ───────────────────────────────────────────────────────────────

def get_nested_value(data: Any, path: List[Union[str, int]]) -> Optional[Any]:
    current = data
    for key in path:
        if isinstance(key, int):
            if isinstance(current, list) and len(current) > key:
                current = current[key]
            else:
                return None
        else:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
    return current


def set_nested_value(
    data: Any,
    path: List[Union[str, int]],
    value: Any,
) -> None:
    current = data
    for i, key in enumerate(path[:-1]):
        next_key = path[i + 1]
        if isinstance(key, int):
            while len(current) <= key:
                current.append({})
            current = current[key]
        else:
            if key not in current:
                current[key] = [] if isinstance(next_key, int) else {}
            current = current[key]

    final_key = path[-1]
    if isinstance(final_key, int):
        while len(current) <= final_key:
            current.append(None)
        current[final_key] = value
    else:
        current[final_key] = value


# ── Public API ─────────────────────────────────────────────────────────────────

def get_subschema(
    usdm_class: str,
    template_path: str = "template/usdm_schema.json",
) -> Dict:
    """
    Return a minimal JSON sub-schema for one USDM class.

    For base classes: slice the field out of the master template.
    For custom extension classes: return the inline schema defined above.

    The returned dict is what the LLM receives; it must return the same
    structure with values filled in.
    """

    # ── Custom extension class ────────────────────────────────────────────────
    # if usdm_class in CUSTOM_CLASS_SCHEMAS:
    #     return {usdm_class: copy.deepcopy(CUSTOM_CLASS_SCHEMAS[usdm_class])}

    # ── Base USDM class ───────────────────────────────────────────────────────
    if usdm_class not in USDM_CLASS_PATHS:
        # Unknown class — return empty shell so the caller can still proceed
        return {usdm_class: None}

    master = load_template(template_path)
    print(master.keys())
    # print(master["study"].keys())
    path   = USDM_CLASS_PATHS[usdm_class]
    value  = get_nested_value(master, path)

    if usdm_class not in master:
        return {usdm_class: None}

    return {
        usdm_class: copy.deepcopy(master[usdm_class])
    }

    # if value is None:
    #     return {usdm_class: None}

    # subschema: Dict = {}
    # set_nested_value(subschema, path, copy.deepcopy(value))
    # return subschema


# ── Self-test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    for cls_name in ["objective", "eligibilityCriterion", "statisticalAnalysis",
                     "cellTherapyManufacturing", "randomization"]:
        schema = get_subschema(cls_name)
        print(f"\n{'='*60}")
        print(f"Sub-schema for: {cls_name}")
        print(json.dumps(schema, indent=3)[:800])