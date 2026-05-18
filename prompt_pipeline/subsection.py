import json
import copy


# =========================================================
# USDM CLASS → JSON PATH
# =========================================================

USDM_CLASS_PATHS = {

    "study":
        ["study"],

    "studyVersion":
        ["study", "versions"],

    "studyTitle":
        ["study", "versions", 0, "titles"],

    "studyIdentifier":
        ["study", "versions", 0, "studyIdentifiers"],

    "indication":
        ["study", "versions", 0, "studyDesigns", 0, "indications"],

    "objective":
        ["study", "versions", 0, "studyDesigns", 0, "objectives"],

    "endpoint":
        ["study", "versions", 0, "studyDesigns", 0, "objectives", 0, "endpoints"],

    "studyDesign":
        ["study", "versions", 0, "studyDesigns"],

    "studyArm":
        ["study", "versions", 0, "studyDesigns", 0, "arms"],

    "studyEpoch":
        ["study", "versions", 0, "studyDesigns", 0, "epochs"],

    "studyCell":
        ["study", "versions", 0, "studyDesigns", 0, "cells"],

    "eligibilityCriterion":
        ["study", "versions", 0, "studyDesigns", 0, "population", "criteria"],

    "studyDesignPopulation":
        ["study", "versions", 0, "studyDesigns", 0, "population"],

    "encounter":
        ["study", "versions", 0, "studyDesigns", 0, "encounters"],

    "activity":
        ["study", "versions", 0, "studyDesigns", 0, "activities"],

    "scheduleTimeline":
        ["study", "versions", 0, "studyDesigns", 0, "scheduleTimelines"],

    "timing":
        ["study", "versions", 0, "studyDesigns", 0, "timings"],

    "studyIntervention":
        ["study", "versions", 0, "studyDesigns", 0, "interventions"],

    "administration":
        ["study", "versions", 0, "studyDesigns", 0, "administrations"],

    "estimand":
        ["study", "versions", 0, "analysis", "estimands"],

    "analysisPopulation":
        ["study", "versions", 0, "analysis", "analysisPopulations"],

    "studyAmendment":
        ["study", "amendments"],

    "organization":
        ["study", "organizations"],

    "studyRole":
        ["study", "roles"]
}


# =========================================================
# LOAD MASTER TEMPLATE
# =========================================================

def load_template(template_path):

    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# CREATE EMPTY CONTAINER
# =========================================================

def create_empty_structure():

    return {}


# =========================================================
# GET VALUE FROM PATH
# =========================================================

def get_nested_value(data, path):

    current = data

    for key in path:

        if isinstance(key, int):

            if isinstance(current, list) and len(current) > key:
                current = current[key]
            else:
                return None

        else:

            if key in current:
                current = current[key]
            else:
                return None

    return current


# =========================================================
# SET VALUE INTO PATH
# =========================================================

def set_nested_value(data, path, value):

    current = data

    for i, key in enumerate(path[:-1]):

        next_key = path[i + 1]

        # Handle list indexes
        if isinstance(key, int):

            while len(current) <= key:
                current.append({})

            current = current[key]

        else:

            if key not in current:

                # Decide dict vs list
                if isinstance(next_key, int):
                    current[key] = []
                else:
                    current[key] = {}

            current = current[key]

    final_key = path[-1]

    if isinstance(final_key, int):

        while len(current) <= final_key:
            current.append(None)

        current[final_key] = value

    else:

        current[final_key] = value


# =========================================================
# EXTRACT SUBSCHEMA
# =========================================================

def get_subschema(usdm_targets,
                  template_path="template/usdm_schema.json"):

    master_schema = load_template(template_path)

    subschema = create_empty_structure()

    for target in usdm_targets:

        if target not in USDM_CLASS_PATHS:
            continue

        path = USDM_CLASS_PATHS[target]

        value = get_nested_value(master_schema, path)

        if value is not None:

            set_nested_value(
                subschema,
                path,
                copy.deepcopy(value)
            )

    return subschema


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    targets = [
        "objective",
        "endpoint"
    ]

    subschema = get_subschema(targets)

    print(json.dumps(subschema, indent=3))