#from utils.file_manager import load_json, save_json
import json 

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

    with open(path, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

