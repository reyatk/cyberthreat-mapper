"""
step02_load_attack.py
Step 2: Load MITRE ATT&CK techniques from the raw STIX file.

Reads data/raw/enterprise-attack.json and keeps, for each technique,
its ATT&CK ID (like T1053.005), name, description, and whether it is
a sub-technique.

Run from the project folder with the virtual environment on:
    python src/step02_load_attack.py
"""

import json
import sys
from pathlib import Path

# Where the downloaded MITRE file lives (relative to the project folder).
RAW_PATH = Path("data/raw/enterprise-attack.json")
PROCESSED_PATH = Path("data/processed/techniques.json")


def load_objects(path: Path) -> list[dict]:
    """Read the STIX file and return its list of objects."""
    with open(path, encoding="utf-8") as f:
        bundle = json.load(f)
    return bundle["objects"]


def get_attack_id(obj: dict) -> str | None:
    """
    Return the ATT&CK ID (like "T1053.005") for one object, or None if it has none.

    The ID lives in obj["external_references"], which is a LIST of dictionaries.
    The right one has "source_name" equal to "mitre-attack", and the ID is
    under its "external_id" key.
    """
    for reference in obj.get("external_references", []):
        if reference["source_name"] == "mitre-attack":
            return reference["external_id"]
    return None

def is_active(obj: dict) -> bool:
    """
    Return True if a technique is still in use, False if it was
    replaced (revoked) or retired (deprecated).
    """
    if obj.get("revoked", False) or obj.get("x_mitre_deprecated", False):
        return False
    return True


def extract_techniques(objects: list[dict]) -> list[dict]:
    """Keep only technique objects, simplified to the four fields this project uses."""
    techniques = []
    for obj in objects:
        # In STIX, ATT&CK techniques have type "attack-pattern".
        if obj["type"] != "attack-pattern":
            continue  # skip everything else (relationships, malware, ...)
        if not is_active(obj):
            continue  # skip techniques that were replaced or retired

        technique = {
            "id": get_attack_id(obj),
            "name": obj["name"],
            "description": obj.get("description", ""),
            "is_subtechnique": obj.get("x_mitre_is_subtechnique", False),
        }
        techniques.append(technique)

    return techniques

def save_techniques(techniques: list[dict], path: Path) -> None:
    """Write the cleaned techniques to a JSON file, creating the folder if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)  # makes data/processed/ if missing
    with open(path, "w", encoding="utf-8") as f:
        json.dump(techniques, f, indent=2)
    pass


def main() -> int:
    """Load the techniques and spot-check one. Returns 0 on success, 1 on failure."""
    if not RAW_PATH.exists():
        print(f"Can't find {RAW_PATH}. Download it first (Phase 2 download task).")
        return 1

    objects = load_objects(RAW_PATH)
    techniques = extract_techniques(objects)
    print(f"Loaded {len(techniques)} techniques.")

    # Spot-check: look for the technique from your Step 1 test.
    matches = [t for t in techniques if t["id"] == "T1053.005"]
    if matches:
        tech = matches[0]
        print(tech["id"], "-", tech["name"], "| sub-technique:", tech["is_subtechnique"])
        print(tech["description"][:200], "...")
    else:
        print("T1053.005 not found. Check TODO 1 and TODO 2.")
    
    save_techniques(techniques, PROCESSED_PATH)
    print(f"Saved {len(techniques)} techniques to {PROCESSED_PATH}")
    return 0


# Runs main() only when you run this file directly.
if __name__ == "__main__":
    sys.exit(main())