"""
Test for the deployment strategy "Other" functionality.

This test verifies that custom deployment strategies are handled correctly
when saved and loaded via JSON.
"""

import json
from wizard_data import (
    build_wizard_payload,
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_deployment_strategy_other_roundtrip():
    """Test that custom deployment strategy is preserved through JSON round-trip."""
    
    # Create test session state with custom deployment strategy
    test_session = get_title_only_session_state("Test Project")
    test_session["_wizard_deployment_strategy"] = "Other"
    test_session["_wizard_deployment_strategy_other"] = "Custom XYZ Strategy"
    test_session["_wizard_deployment_strategy_description"] = "Custom pilot approach"
    
    # Build payload
    payload = build_wizard_payload(test_session)
    
    # Verify the custom strategy is in the payload
    assert payload["initiative"]["deployment_strategy"] == "Custom XYZ Strategy", \
        f"Expected 'Custom XYZ Strategy' but got '{payload['initiative']['deployment_strategy']}'"
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Deserialize from JSON
    loaded_data = json.loads(json_str)
    
    # Restore session state
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify the custom strategy is restored correctly
    assert restored_updates["_wizard_deployment_strategy"] == "Other", \
        f"Expected 'Other' but got '{restored_updates.get('_wizard_deployment_strategy')}'"
    assert restored_updates["_wizard_deployment_strategy_other"] == "Custom XYZ Strategy", \
        f"Expected 'Custom XYZ Strategy' but got '{restored_updates.get('_wizard_deployment_strategy_other')}'"
    
    print("✅ Deployment strategy 'Other' round-trip test passed!")
    print(f"   - Custom strategy 'Custom XYZ Strategy' preserved through JSON save/load")


def test_standard_deployment_strategy():
    """Test that standard deployment strategies work correctly."""
    
    # Create test session state with standard deployment strategy
    test_session = get_title_only_session_state("Test Project")
    test_session["_wizard_deployment_strategy"] = "Canary"
    test_session["_wizard_deployment_strategy_other"] = ""  # Should be empty for standard
    
    # Build payload
    payload = build_wizard_payload(test_session)
    
    # Verify the standard strategy is in the payload
    assert payload["initiative"]["deployment_strategy"] == "Canary", \
        f"Expected 'Canary' but got '{payload['initiative']['deployment_strategy']}'"
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Deserialize from JSON
    loaded_data = json.loads(json_str)
    
    # Restore session state
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify the standard strategy is restored correctly
    assert restored_updates["_wizard_deployment_strategy"] == "Canary", \
        f"Expected 'Canary' but got '{restored_updates.get('_wizard_deployment_strategy')}'"
    assert restored_updates["_wizard_deployment_strategy_other"] == "", \
        f"Expected empty string but got '{restored_updates.get('_wizard_deployment_strategy_other')}'"
    
    print("✅ Standard deployment strategy test passed!")
    print(f"   - Standard strategy 'Canary' preserved through JSON save/load")


def test_unknown_deployment_strategy():
    """Test that unknown deployment strategies are moved to 'Other'."""
    
    # Create JSON with unknown deployment strategy
    test_json = {
        "initiative": {
            "title": "Test Project",
            "deployment_strategy": "Unknown Strategy"
        }
    }
    
    # Restore session state
    restored_updates = restore_session_state_from_data(test_json)
    
    # Verify unknown strategy is moved to 'Other'
    assert restored_updates["_wizard_deployment_strategy"] == "Other", \
        f"Expected 'Other' but got '{restored_updates.get('_wizard_deployment_strategy')}'"
    assert restored_updates["_wizard_deployment_strategy_other"] == "Unknown Strategy", \
        f"Expected 'Unknown Strategy' but got '{restored_updates.get('_wizard_deployment_strategy_other')}'"
    
    print("✅ Unknown deployment strategy test passed!")
    print(f"   - Unknown strategy moved to 'Other' field")


if __name__ == "__main__":
    test_deployment_strategy_other_roundtrip()
    test_standard_deployment_strategy()
    test_unknown_deployment_strategy()
    print("\n🎉 All deployment strategy tests passed!")
