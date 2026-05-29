"""
Test for stakeholders field with "None" selections.

This test verifies that the stakeholders field can handle "None" selections
without failing during JSON upload/restore operations.
"""

import json
from wizard_data import (
    build_wizard_payload,
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_stakeholders_with_none_selections():
    """Test that stakeholders with 'None' selections are handled correctly."""
    
    print("\n=== Testing Stakeholders with 'None' Selections ===")
    
    # Create test session state with stakeholders including "None"
    test_session = get_title_only_session_state("Test Project")
    test_session["stakeholders_choices"] = {
        "Technical Stakeholders": "None",
        "User and Customer Stakeholders": "Network Engineering team",
        "Governance and Risk Stakeholders": "None",
        "Business and Leadership Stakeholders": "Executive sponsor (CIO / CTO / VP of IT)",
        "External/Vendor/Partner Stakeholders": "None"
    }
    test_session["stakeholders_other_text"] = ""
    
    # Build payload
    payload = build_wizard_payload(test_session)
    
    # Verify the stakeholders are in the payload
    assert "stakeholders" in payload, "Stakeholders not found in payload"
    assert payload["stakeholders"]["choices"]["Technical Stakeholders"] == "None", \
        f"Expected 'None' but got '{payload['stakeholders']['choices']['Technical Stakeholders']}'"
    print("✅ Stakeholders with 'None' selections correctly stored in payload")
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Verify JSON contains the correct stakeholders
    json_data = json.loads(json_str)
    assert json_data["stakeholders"]["choices"]["Technical Stakeholders"] == "None", \
        f"JSON expected 'None' but got '{json_data['stakeholders']['choices']['Technical Stakeholders']}'"
    print("✅ Stakeholders with 'None' selections correctly serialized to JSON")
    
    # Deserialize from JSON
    loaded_data = json.loads(json_str)
    
    # Restore session state
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify the stakeholders are restored correctly
    assert "stakeholders_choices" in restored_updates, \
        "stakeholders_choices not found in restored updates"
    assert restored_updates["stakeholders_choices"]["Technical Stakeholders"] == "None", \
        f"Expected 'None' but got '{restored_updates['stakeholders_choices']['Technical Stakeholders']}'"
    assert restored_updates["stakeholders_choices"]["User and Customer Stakeholders"] == "Network Engineering team", \
        f"Expected 'Network Engineering team' but got '{restored_updates['stakeholders_choices']['User and Customer Stakeholders']}'"
    print("✅ Stakeholders with 'None' selections correctly restored from JSON")
    
    print("\n✅ Stakeholders 'None' selection test passed!")


def test_stakeholders_empty_and_none():
    """Test that empty and None stakeholder data is handled gracefully."""
    
    print("\n=== Testing Empty and None Stakeholder Data ===")
    
    # Test case 1: stakeholders is None
    test_json_1 = {
        "initiative": {"title": "Test"},
        "stakeholders": None
    }
    
    restored_updates_1 = restore_session_state_from_data(test_json_1)
    assert restored_updates_1.get("stakeholders_choices") == {}, \
        f"Expected empty dict but got '{restored_updates_1.get('stakeholders_choices')}'"
    print("✅ None stakeholders handled correctly")
    
    # Test case 2: stakeholders is empty dict
    test_json_2 = {
        "initiative": {"title": "Test"},
        "stakeholders": {}
    }
    
    restored_updates_2 = restore_session_state_from_data(test_json_2)
    assert restored_updates_2.get("stakeholders_choices") == {}, \
        f"Expected empty dict but got '{restored_updates_2.get('stakeholders_choices')}'"
    print("✅ Empty stakeholders dict handled correctly")
    
    # Test case 3: stakeholders has no choices key
    test_json_3 = {
        "initiative": {"title": "Test"},
        "stakeholders": {"other": "Custom stakeholder"}
    }
    
    restored_updates_3 = restore_session_state_from_data(test_json_3)
    assert restored_updates_3.get("stakeholders_choices") == {}, \
        f"Expected empty dict but got '{restored_updates_3.get('stakeholders_choices')}'"
    assert restored_updates_3.get("stakeholders_other_text") == "Custom stakeholder", \
        f"Expected 'Custom stakeholder' but got '{restored_updates_3.get('stakeholders_other_text')}'"
    print("✅ Stakeholders without choices handled correctly")
    
    print("\n✅ Empty and None stakeholder data test passed!")


def test_stakeholders_all_none():
    """Test that all stakeholders set to 'None' works correctly."""
    
    print("\n=== Testing All Stakeholders Set to 'None' ===")
    
    # Create test session with all stakeholders as "None"
    test_session = get_title_only_session_state("All None Test")
    test_session["stakeholders_choices"] = {
        "Technical Stakeholders": "None",
        "User and Customer Stakeholders": "None",
        "Governance and Risk Stakeholders": "None",
        "Business and Leadership Stakeholders": "None",
        "External/Vendor/Partner Stakeholders": "None"
    }
    test_session["stakeholders_other_text"] = ""
    
    # Build payload and test round-trip
    payload = build_wizard_payload(test_session)
    json_str = json.dumps(payload, indent=2)
    loaded_data = json.loads(json_str)
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify all stakeholders are "None"
    for category, value in restored_updates["stakeholders_choices"].items():
        assert value == "None", \
            f"Expected 'None' for {category} but got '{value}'"
    
    print("✅ All stakeholders correctly set to 'None'")
    print("\n✅ All 'None' stakeholders test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Stakeholders Field with 'None' Selections")
    print("=" * 60)
    
    test_stakeholders_with_none_selections()
    test_stakeholders_empty_and_none()
    test_stakeholders_all_none()
    
    print("\n" + "=" * 60)
    print("🎉 All stakeholders 'None' tests passed successfully!")
    print("=" * 60)
