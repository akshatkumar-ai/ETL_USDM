# =========================================================
# REQUIRED USDM PATHS
# =========================================================

REQUIRED_FIELDS = {

    "study_identifiers":
        ["study", "versions", 0, "studyIdentifiers"],

    "objectives":
        ["study", "versions", 0, "studyDesigns", 0, "objectives"],

    "study_arms":
        ["study", "versions", 0, "studyDesigns", 0, "arms"],

    "eligibility":
        ["study", "versions", 0, "studyDesigns", 0, "population"],

    "schedule":
        ["study", "versions", 0, "studyDesigns", 0, "encounters"],

    "interventions":
        ["study", "versions", 0, "studyDesigns", 0, "interventions"],

    "estimands":
        ["study", "versions", 0, "analysis", "estimands"]
}


# =========================================================
# GET VALUE FROM PATH
# =========================================================

def get_nested_value(data, path):

    current = data

    for key in path:

        try:

            if isinstance(key, int):

                current = current[key]

            else:

                current = current[key]

        except Exception:

            return None

    return current


# =========================================================
# CHECK EMPTY
# =========================================================

def is_missing(value):

    return value in [
        None,
        "",
        [],
        {}
    ]


# =========================================================
# VALIDATE USDM
# =========================================================

def validate_usdm(usdm_json):
    """
    Validate critical USDM sections.
    """

    validation_results = {

        "valid": True,

        "missing_sections": [],

        "present_sections": []
    }

    for section_name, path in REQUIRED_FIELDS.items():

        value = get_nested_value(usdm_json, path)

        if is_missing(value):

            validation_results["missing_sections"].append(
                section_name
            )

            validation_results["valid"] = False

        else:

            validation_results["present_sections"].append(
                section_name
            )

    return validation_results


# =========================================================
# COMPLETENESS SCORE
# =========================================================

def calculate_completeness(validation_results):

    total = len(REQUIRED_FIELDS)

    present = len(
        validation_results["present_sections"]
    )

    score = round((present / total) * 100, 2)

    return score


# =========================================================
# PRINT REPORT
# =========================================================

def print_validation_report(validation_results):

    print("\n" + "=" * 60)
    print("USDM VALIDATION REPORT")
    print("=" * 60)

    print("\n✅ PRESENT SECTIONS:\n")

    for item in validation_results["present_sections"]:

        print(f"  ✔ {item}")

    print("\n❌ MISSING SECTIONS:\n")

    for item in validation_results["missing_sections"]:

        print(f"  ✘ {item}")

    completeness = calculate_completeness(
        validation_results
    )

    print(f"\n📊 COMPLETENESS: {completeness}%\n")


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    sample_usdm = {

        "study": {

            "versions": [

                {

                    "studyIdentifiers": [
                        {
                            "id": "ABC123"
                        }
                    ],

                    "studyDesigns": [

                        {

                            "objectives": [
                                {
                                    "name": "Primary Objective"
                                }
                            ],

                            "arms": [
                                {
                                    "name": "Placebo"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

    results = validate_usdm(sample_usdm)

    print_validation_report(results)