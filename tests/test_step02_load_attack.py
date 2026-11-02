"""
Tests for step02_load_attack.py.

These use small fake objects instead of the real 53 MB file,
so they run instantly and test only our own logic.

Run from the project folder with:  python -m pytest
"""

import step02_load_attack as loader


def make_technique(attack_id="T1053.005", name="Scheduled Task", **extra):
    """Build a fake STIX technique object. `extra` adds or overrides keys."""
    obj = {
        "type": "attack-pattern",
        "name": name,
        "description": "Example description.",
        "x_mitre_is_subtechnique": True,
        "external_references": [
            {"source_name": "mitre-attack", "external_id": attack_id},
        ],
    }
    obj.update(extra)
    return obj


def test_get_attack_id_finds_mitre_id():
    obj = make_technique(attack_id="T1003")
    assert loader.get_attack_id(obj) == "T1003"


def test_get_attack_id_skips_other_sources():
    # The MITRE reference is second in the list, so the loop has to keep looking.
    obj = make_technique()
    obj["external_references"].insert(0, {"source_name": "capec", "external_id": "CAPEC-1"})
    assert loader.get_attack_id(obj) == "T1053.005"


def test_get_attack_id_returns_none_when_missing():
    obj = make_technique()
    obj["external_references"] = []
    assert loader.get_attack_id(obj) is None


def test_is_active_false_when_revoked():
    assert loader.is_active(make_technique(revoked=True)) is False


def test_is_active_true_for_normal_technique():
    assert loader.is_active(make_technique()) is True


def test_extract_skips_non_techniques_and_inactive():
    objects = [
        make_technique(attack_id="T1053.005"),
        make_technique(attack_id="T9999", revoked=True),
        {"type": "relationship"},  # not a technique, should be skipped
    ]
    result = loader.extract_techniques(objects)
    assert [t["id"] for t in result] == ["T1053.005"]
    assert set(result[0].keys()) == {"id", "name", "description", "is_subtechnique"}


def test_is_active_false_when_deprecated():
    assert loader.is_active(make_technique(x_mitre_deprecated=True)) is False