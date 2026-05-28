from __future__ import annotations

import json


DEDUP_KEYS = {

    "eligibilityCriterion":
        ["criterion", "text", "description"],

    "studyEpoch":
        ["name"],

    "studyArm":
        ["name"],

    "objective":
        ["name", "description"],

    "endpoint":
        ["name", "description"],

    "activity":
        ["name"],

    "encounter":
        ["name"],

    "analysisPopulation":
        ["name"],

    "studyCell":
        ["name"],
}


def _normalize(v):

    if v is None:
        return ""

    return str(v).strip().lower()


def _dedup_list(items, keys):

    seen = set()

    deduped = []

    for item in items:

        if not isinstance(item, dict):

            deduped.append(item)

            continue

        signature = tuple(
            _normalize(item.get(k))
            for k in keys
        )

        if signature in seen:
            continue

        seen.add(signature)

        deduped.append(item)

    return deduped


def deduplicate_usdm(obj):

    if isinstance(obj, dict):

        result = {}

        for k, v in obj.items():

            result[k] = deduplicate_usdm(v)

            if (
                isinstance(result[k], list)
                and k in DEDUP_KEYS
            ):
                result[k] = _dedup_list(
                    result[k],
                    DEDUP_KEYS[k]
                )

        return result

    elif isinstance(obj, list):

        return [
            deduplicate_usdm(x)
            for x in obj
        ]

    return obj