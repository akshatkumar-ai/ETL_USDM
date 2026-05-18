import copy


# =========================================================
# CHECK NULL/EMPTY
# =========================================================

def is_empty(value):

    return value in [
        None,
        "",
        [],
        {}
    ]


# =========================================================
# MERGE LISTS
# =========================================================

def merge_lists(base, new):

    if not isinstance(base, list):
        base = []

    if not isinstance(new, list):
        return base

    merged = copy.deepcopy(base)

    for item in new:

        # Avoid duplicate exact objects
        if item not in merged:
            merged.append(item)

    return merged


# =========================================================
# RECURSIVE MERGE
# =========================================================

def merge_usdm(base, new):
    """
    Recursively merge USDM structures.

    Rules:
    - null never overwrites non-null
    - arrays append
    - dicts merge recursively
    - non-null overwrites null
    """

    # -----------------------------------------------------
    # CASE 1: BOTH DICTS
    # -----------------------------------------------------

    if isinstance(base, dict) and isinstance(new, dict):

        merged = copy.deepcopy(base)

        for key, value in new.items():

            if key not in merged:

                merged[key] = copy.deepcopy(value)

            else:

                merged[key] = merge_usdm(
                    merged[key],
                    value
                )

        return merged


    # -----------------------------------------------------
    # CASE 2: BOTH LISTS
    # -----------------------------------------------------

    if isinstance(base, list) and isinstance(new, list):

        return merge_lists(base, new)


    # -----------------------------------------------------
    # CASE 3: BASE EMPTY → TAKE NEW
    # -----------------------------------------------------

    if is_empty(base) and not is_empty(new):

        return copy.deepcopy(new)


    # -----------------------------------------------------
    # CASE 4: KEEP EXISTING
    # -----------------------------------------------------

    return copy.deepcopy(base)


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    base = {

        "study": {

            "versions": [

                {
                    "studyDesigns": [

                        {
                            "objectives": [
                                {
                                    "name": "Primary Objective"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

    new = {

        "study": {

            "versions": [

                {
                    "studyDesigns": [

                        {
                            "arms": [
                                {
                                    "name": "Placebo Arm"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }

    merged = merge_usdm(base, new)

    import json

    print(json.dumps(merged, indent=2))
    