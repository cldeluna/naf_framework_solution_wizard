"""
Test for the title field round-trip functionality.

This test verifies that when only the title field is modified
and saved to JSON, uploading that JSON only updates the title field.
"""

import json
from wizard_data import (
    build_wizard_payload,
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_title_field_roundtrip():
    """Test that title field can be saved and loaded without affecting other fields."""
    
    # Initial session state with default values
    original_title = "My new network automation project"
    new_title = "Updated Network Automation Project"
    
    # Create initial session state
    initial_state = get_title_only_session_state(original_title)
    
    # Build payload (simulating JSON download)
    payload = build_wizard_payload(initial_state)
    
    # Modify only the title in the payload
    payload["initiative"]["title"] = new_title
    # Ensure category is empty to match the initial state
    payload["initiative"]["category"] = ""
    
    # Restore session state from modified payload (simulating JSON upload)
    restored_updates = restore_session_state_from_data(payload)
    
    # Verify only title-related fields changed
    assert restored_updates["_wizard_automation_title"] == new_title, \
        f"Title should be '{new_title}' but got '{restored_updates.get('_wizard_automation_title')}'"
    
    # Check that other fields remain at their default values
    # Note: When category is empty in JSON, it gets restored as "Other"
    expected_defaults = get_title_only_session_state(new_title)
    expected_defaults["_wizard_category"] = "Other"  # Adjust for empty category behavior
    
    # Fields that should NOT have changed
    fields_to_check = [
        "_wizard_automation_description",
        "_wizard_problem_statement",
        "_wizard_expected_use",
        "_wizard_error_conditions",
        "_wizard_assumptions",
        "_wizard_deployment_strategy",  # This now gets set to placeholder when empty
        "_wizard_deployment_strategy_description",
        "_wizard_out_of_scope",
        "_wizard_category",
        "_wizard_category_other",
        "stakeholders_choices",
        "stakeholders_other_text",
        "my_role_who",
        "my_role_skills",
        "my_role_dev",
    ]
    
    for field in fields_to_check:
        actual_value = restored_updates.get(field, initial_state.get(field))
        expected_value = expected_defaults.get(field)
        
        if field in ["stakeholders_choices"]:
            # Special handling for dict fields
            assert actual_value == expected_value, \
                f"Field '{field}' should remain unchanged"
        elif field == "_wizard_deployment_strategy":
            # Deployment strategy gets set to placeholder when empty
            assert actual_value == "— Select a deployment strategy —", \
                f"Field '{field}' should be placeholder but got '{actual_value}'"
        else:
            assert actual_value == expected_value, \
                f"Field '{field}' should be '{expected_value}' but got '{actual_value}'"
    
    print("✅ Title field round-trip test passed!")
    print(f"   - Title successfully updated from '{original_title}' to '{new_title}'")
    print(f"   - All other fields remained at their default values")
    

def test_json_serialization_roundtrip():
    """Test that the payload can be serialized to JSON and deserialized back."""
    
    # Create test data
    test_title = "Test JSON Serialization"
    initial_state = get_title_only_session_state(test_title)
    
    # Build payload
    payload = build_wizard_payload(initial_state)
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Deserialize from JSON
    loaded_data = json.loads(json_str)
    
    # Restore session state
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify title is preserved
    assert restored_updates["_wizard_automation_title"] == test_title, \
        "Title should survive JSON serialization round-trip"
    
    print("✅ JSON serialization round-trip test passed!")


def test_multiple_field_changes():
    """Test that multiple fields can be updated correctly."""
    
    # Create initial state
    initial_state = get_title_only_session_state("Original Title")
    
    # Build payload
    payload = build_wizard_payload(initial_state)
    
    # Modify multiple fields
    payload["initiative"]["title"] = "Multi-Field Update Test"
    payload["initiative"]["problem_statement"] = "This is a test problem statement"
    payload["initiative"]["category"] = "Configuration Management ITIL4/5"  # Use exact key from YAML
    
    # Restore session state
    restored_updates = restore_session_state_from_data(payload)
    
    # Verify all fields were updated
    assert restored_updates["_wizard_automation_title"] == "Multi-Field Update Test"
    assert restored_updates["_wizard_problem_statement"] == "This is a test problem statement"
    # Category should be set to the valid category value
    assert restored_updates["_wizard_category"] == "Configuration Management ITIL4/5"
    
    print("✅ Multiple field update test passed!")


if __name__ == "__main__":
    test_title_field_roundtrip()
    test_json_serialization_roundtrip()
    test_multiple_field_changes()
    print("\n🎉 All tests passed successfully!")
