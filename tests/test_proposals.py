import json

import pytest

from edge_catch.proposals import parse_proposal


def valid_proposal() -> dict[str, object]:
    return {
        "hypothesis": "An empty value may follow a separate branch.",
        "assumptions": ["Empty strings are accepted inputs."],
        "expected_behavior": "The function returns an empty string.",
        "rationale": "Existing tests only use non-empty values.",
        "test_name": "test_empty_value",
        "test_code": "def test_empty_value():\n    assert format_value('') == ''\n",
    }


def test_parses_complete_proposal_and_preserves_raw_response() -> None:
    raw_response = json.dumps(valid_proposal())

    proposal = parse_proposal(raw_response)

    assert proposal.hypothesis == "An empty value may follow a separate branch."
    assert proposal.assumptions == ("Empty strings are accepted inputs.",)
    assert proposal.test_name == "test_empty_value"
    assert proposal.raw_response == raw_response


def test_rejects_malformed_json() -> None:
    with pytest.raises(ValueError, match="proposal is not valid JSON"):
        parse_proposal("not JSON")


def test_rejects_missing_field() -> None:
    data = valid_proposal()
    del data["rationale"]

    with pytest.raises(ValueError, match="missing fields: rationale"):
        parse_proposal(json.dumps(data))


def test_rejects_unexpected_field() -> None:
    data = valid_proposal()
    data["confidence"] = 0.99

    with pytest.raises(ValueError, match="unexpected fields: confidence"):
        parse_proposal(json.dumps(data))


def test_rejects_invalid_assumptions() -> None:
    data = valid_proposal()
    data["assumptions"] = "Empty strings are accepted inputs."

    with pytest.raises(ValueError, match="assumptions must be an array"):
        parse_proposal(json.dumps(data))


def test_rejects_blank_string_field() -> None:
    data = valid_proposal()
    data["hypothesis"] = "   "

    with pytest.raises(ValueError, match="hypothesis must be a non-empty string"):
        parse_proposal(json.dumps(data))
