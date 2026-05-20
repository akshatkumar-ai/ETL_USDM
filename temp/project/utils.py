import os
import json
import re


# =========================================================
# LOAD TEXT
# =========================================================

def load_text_file(path):

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# =========================================================
# LOAD JSON
# =========================================================

def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================================
# SAVE JSON
# =========================================================

def save_json(data, path):

    os.makedirs(
        os.path.dirname(path),
        exist_ok=True
    )

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )


# =========================================================
# CLEAN LLM JSON RESPONSE
# =========================================================

def clean_json_response(text):

    text = text.strip()

    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)

    text = re.sub(r"```$", "", text)

    return text.strip()


# =========================================================
# DEEP MERGE
# =========================================================

def deep_merge(target, source):

    for key, value in source.items():

        # -------------------------------------------------
        # DICT
        # -------------------------------------------------

        if (
            key in target
            and isinstance(target[key], dict)
            and isinstance(value, dict)
        ):

            deep_merge(
                target[key],
                value
            )

        # -------------------------------------------------
        # LIST
        # -------------------------------------------------

        elif (
            key in target
            and isinstance(target[key], list)
            and isinstance(value, list)
        ):

            target[key].extend(value)

        # -------------------------------------------------
        # SCALAR
        # -------------------------------------------------

        else:

            target[key] = value