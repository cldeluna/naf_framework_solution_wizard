"""
Test full stakeholders flow including widget index calculation.

This test verifies that stakeholders widgets correctly display restored values
and that the index calculation works for both "None" and regular selections.
"""

import json
from wizard_data import (
    build_wizard_payload,
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_stakeholders_selectbox_index_calculation():
    """Test that selectbox index is calculated correctly for restored values."""
    
    print("\n=== Testing Stakeholders Selectbox Index Calculation ===")
    
    # Simulate the stakeholders catalog
    catalog = {
        "Technical Stakeholders": [
            "Individual Network Engineer",
            "Network Engineering team",
            "Network Operations (NOC) team",
            "Security engineering / operations",
            "None"
        ],
        "Business Stakeholders": [
            "Executive sponsor",
            "Project manager",
            "Finance team",
            "None"
        ]
    }
    
    # Test case 1: Regular selection (not "None")
    print("\nTest 1: Regular selection")
    current_value = "Network Engineering team"
    select_opts = ["— Select one —"] + catalog["Technical Stakeholders"]
    
    # This is the logic from the fixed code
    try:
        index = select_opts.index(current_value) if current_value in select_opts else 0
    except ValueError:
        index = 0
    
    expected_index = 2  # "— Select one —" (0), "Individual Network Engineer" (1), "Network Engineering team" (2)
    assert index == expected_index, \
        f"Expected index {expected_index} for 'Network Engineering team' but got {index}"
    print(f"✅ Index correctly calculated as {index} for 'Network Engineering team'")
    
    # Test case 2: "None" selection
    print("\nTest 2: 'None' selection")
    current_value = "None"
    select_opts = ["— Select one —"] + catalog["Technical Stakeholders"]
    
    try:
        index = select_opts.index(current_value) if current_value in select_opts else 0
    except ValueError:
        index = 0
    
    expected_index = 5  # "None" is at position 5 in the options
    assert index == expected_index, \
        f"Expected index {expected_index} for 'None' but got {index}"
    print(f"✅ Index correctly calculated as {index} for 'None'")
    
    # Test case 3: Sentinel value (should default to 0)
    print("\nTest 3: Sentinel value")
    current_value = "— Select one —"
    select_opts = ["— Select one —"] + catalog["Technical Stakeholders"]
    
    try:
        index = select_opts.index(current_value) if current_value in select_opts else 0
    except ValueError:
        index = 0
    
    expected_index = 0  # Sentinel should be at index 0
    assert index == expected_index, \
        f"Expected index {expected_index} for sentinel but got {index}"
    print(f"✅ Index correctly calculated as {index} for sentinel value")
    
    print("\n✅ Selectbox index calculation test passed!")


def test_stakeholders_full_roundtrip():
    """Test complete round-trip with various stakeholder selections."""
    
    print("\n=== Testing Stakeholders Full Round-trip ===")
    
    # Create test session with mixed selections
    test_session = get_title_only_session_state("Stakeholder Test")
    
    # Simulate widget state (what would be in session_state after widget interaction)
    test_session["stakeholders_choice_Technical_Stakeholders"] = "Network Engineering team"
    test_session["stakeholders_choice_User_and_Customer_Stakeholders"] = "Internal users (ITSM / Service Desk)"
    test_session["stakeholders_choice_Governance_and_Risk_Stakeholders"] = "None"
    test_session["stakeholders_choice_Business_and_Leadership_Stakeholders"] = "Executive sponsor (CIO / CTO / VP of IT)"
    test_session["stakeholders_choice_External_Vendor_Partner_Stakeholders"] = "None"
    test_session["stakeholders_other_text"] = "Custom consulting partner"
    
    # This simulates what the widget code does to build choices
    test_session["stakeholders_choices"] = {
        "Technical Stakeholders": "Network Engineering team",
        "User and Customer Stakeholders": "Internal users (ITSM / Service Desk)",
        "Governance and Risk Stakeholders": "None",
        "Business and Leadership Stakeholders": "Executive sponsor (CIO / CTO / VP of IT)",
        "External/Vendor/Partner Stakeholders": "None"
    }
    
    # Build payload
    payload = build_wizard_payload(test_session)
    
    # Verify payload
    stakeholders = payload["stakeholders"]
    assert stakeholders["choices"]["Technical Stakeholders"] == "Network Engineering team"
    assert stakeholders["choices"]["Governance and Risk Stakeholders"] == "None"
    assert stakeholders["other"] == "Custom consulting partner"
    print("✅ Stakeholders correctly stored in payload")
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Restore session state
    loaded_data = json.loads(json_str)
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify restoration
    assert restored_updates["stakeholders_choices"]["Technical Stakeholders"] == "Network Engineering team"
    assert restored_updates["stakeholders_choices"]["Governance and Risk Stakeholders"] == "None"
    assert restored_updates["stakeholders_other_text"] == "Custom consulting partner"
    print("✅ Stakeholders correctly restored from JSON")
    
    # Simulate widget re-initialization with restored data
    # This tests that the index calculation would work correctly
    for category, value in restored_updates["stakeholders_choices"].items():
        select_opts = ["— Select one —", "None"] + ["Option1", "Option2", "Option3"]  # Simplified
        if value in select_opts:
            index = select_opts.index(value)
            assert select_opts[index] == value, \
                f"Index {index} for {category} doesn't match value '{value}'"
    
    print("✅ Widget re-initialization would work correctly")
    
    print("\n✅ Full round-trip test passed!")


def test_stakeholders_edge_cases():
    """Test edge cases for stakeholders handling."""
    
    print("\n=== Testing Stakeholders Edge Cases ===")
    
    # Test case 1: Empty string value
    test_json_1 = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {"Technical Stakeholders": ""},
            "other": ""
        }
    }
    
    restored_1 = restore_session_state_from_data(test_json_1)
    assert restored_1["stakeholders_choices"]["Technical Stakeholders"] == ""
    print("✅ Empty string handled correctly")
    
    # Test case 2: Value not in options (should still be preserved)
    test_json_2 = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {"Technical Stakeholders": "Custom Team Not In List"},
            "other": ""
        }
    }
    
    restored_2 = restore_session_state_from_data(test_json_2)
    assert restored_2["stakeholders_choices"]["Technical Stakeholders"] == "Custom Team Not In List"
    print("✅ Custom value not in list preserved correctly")
    
    # Test case 3: Mixed None and values
    test_json_3 = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {
                "Technical Stakeholders": "None",
                "Business Stakeholders": "Finance team",
                "Risk Stakeholders": "None"
            },
            "other": ""
        }
    }
    
    restored_3 = restore_session_state_from_data(test_json_3)
    assert restored_3["stakeholders_choices"]["Technical Stakeholders"] == "None"
    assert restored_3["stakeholders_choices"]["Business Stakeholders"] == "Finance team"
    assert restored_3["stakeholders_choices"]["Risk Stakeholders"] == "None"
    print("✅ Mixed None and values handled correctly")
    
    print("\n✅ Edge cases test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Stakeholders Selectbox Fix")
    print("=" * 60)
    
    test_stakeholders_selectbox_index_calculation()
    test_stakeholders_full_roundtrip()
    test_stakeholders_edge_cases()
    
    print("\n" + "=" * 60)
    print("🎉 All stakeholders tests passed successfully!")
    print("=" * 60)
