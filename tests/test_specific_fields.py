"""
Tests for specific field scenarios as requested by the user.

1. Category field set to "Device Onboarding" - verify JSON save/load
2. Deployment Strategy set to "Other" with "My own Strategy" - verify JSON save/load
"""

import json
from wizard_data import (
    build_wizard_payload,
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_category_device_onboarding():
    """Test that Category 'Device Onboarding' is saved to JSON and uploaded successfully."""
    
    print("\n=== Testing Category: Device Onboarding ===")
    
    # Create test session state with Device Onboarding category
    test_session = get_title_only_session_state("Network Automation Project")
    test_session["_wizard_category"] = "Device Onboarding"
    test_session["_wizard_category_other"] = ""  # Empty for standard category
    
    # Build payload
    payload = build_wizard_payload(test_session)
    
    # Verify the category is in the payload
    assert payload["initiative"]["category"] == "Device Onboarding", \
        f"Expected 'Device Onboarding' but got '{payload['initiative']['category']}'"
    print("✅ Category 'Device Onboarding' correctly stored in payload")
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Verify JSON contains the correct category
    json_data = json.loads(json_str)
    assert json_data["initiative"]["category"] == "Device Onboarding", \
        f"JSON expected 'Device Onboarding' but got '{json_data['initiative']['category']}'"
    print("✅ Category 'Device Onboarding' correctly serialized to JSON")
    
    # Deserialize from JSON
    loaded_data = json.loads(json_str)
    
    # Restore session state
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify the category is restored correctly
    assert restored_updates["_wizard_category"] == "Device Onboarding", \
        f"Expected 'Device Onboarding' but got '{restored_updates.get('_wizard_category')}'"
    assert restored_updates["_wizard_category_other"] == "", \
        f"Expected empty string but got '{restored_updates.get('_wizard_category_other')}'"
    print("✅ Category 'Device Onboarding' correctly restored from JSON")
    
    print("\n✅ Category 'Device Onboarding' test passed!")


def test_deployment_strategy_other_my_own():
    """Test that Deployment Strategy 'Other' with 'My own Strategy' is handled correctly."""
    
    print("\n=== Testing Deployment Strategy: Other with 'My own Strategy' ===")
    
    # Create test session state with custom deployment strategy
    test_session = get_title_only_session_state("Custom Strategy Project")
    test_session["_wizard_deployment_strategy"] = "Other"
    test_session["_wizard_deployment_strategy_other"] = "My own Strategy"
    test_session["_wizard_deployment_strategy_description"] = "A custom deployment approach"
    
    # Build payload
    payload = build_wizard_payload(test_session)
    
    # Verify the custom strategy is in the payload
    assert payload["initiative"]["deployment_strategy"] == "My own Strategy", \
        f"Expected 'My own Strategy' but got '{payload['initiative']['deployment_strategy']}'"
    print("✅ Custom deployment strategy 'My own Strategy' correctly stored in payload")
    
    # Serialize to JSON
    json_str = json.dumps(payload, indent=2)
    
    # Verify JSON contains the correct deployment strategy
    json_data = json.loads(json_str)
    assert json_data["initiative"]["deployment_strategy"] == "My own Strategy", \
        f"JSON expected 'My own Strategy' but got '{json_data['initiative']['deployment_strategy']}'"
    print("✅ Custom deployment strategy 'My own Strategy' correctly serialized to JSON")
    
    # Deserialize from JSON
    loaded_data = json.loads(json_str)
    
    # Restore session state
    restored_updates = restore_session_state_from_data(loaded_data)
    
    # Verify the custom strategy is restored correctly
    assert restored_updates["_wizard_deployment_strategy"] == "Other", \
        f"Expected 'Other' but got '{restored_updates.get('_wizard_deployment_strategy')}'"
    assert restored_updates["_wizard_deployment_strategy_other"] == "My own Strategy", \
        f"Expected 'My own Strategy' but got '{restored_updates.get('_wizard_deployment_strategy_other')}'"
    print("✅ Custom deployment strategy correctly restored to 'Other' field")
    
    print("\n✅ Deployment Strategy 'Other' with 'My own Strategy' test passed!")


def test_json_roundtrip_combined():
    """Test both fields together in a single JSON round-trip."""
    
    print("\n=== Testing Combined Fields Round-trip ===")
    
    # Create test session state with both fields
    test_session = get_title_only_session_state("Combined Test Project")
    test_session["_wizard_category"] = "Device Onboarding"
    test_session["_wizard_category_other"] = ""
    test_session["_wizard_deployment_strategy"] = "Other"
    test_session["_wizard_deployment_strategy_other"] = "My own Strategy"
    test_session["_wizard_deployment_strategy_description"] = "Combined test deployment"
    
    # Build payload and serialize to JSON
    payload = build_wizard_payload(test_session)
    json_str = json.dumps(payload, indent=2)
    
    print("📄 Generated JSON snippet:")
    # Show relevant parts of the JSON
    json_data = json.loads(json_str)
    print(json.dumps({
        "title": json_data["initiative"]["title"],
        "category": json_data["initiative"]["category"],
        "deployment_strategy": json_data["initiative"]["deployment_strategy"]
    }, indent=2))
    
    # Restore session state
    restored_updates = restore_session_state_from_data(json_data)
    
    # Verify both fields are correct
    assert restored_updates["_wizard_category"] == "Device Onboarding"
    assert restored_updates["_wizard_deployment_strategy"] == "Other"
    assert restored_updates["_wizard_deployment_strategy_other"] == "My own Strategy"
    
    print("\n✅ Combined fields round-trip test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Specific Field Scenarios")
    print("=" * 60)
    
    test_category_device_onboarding()
    test_deployment_strategy_other_my_own()
    test_json_roundtrip_combined()
    
    print("\n" + "=" * 60)
    print("🎉 All specific field tests passed successfully!")
    print("=" * 60)
