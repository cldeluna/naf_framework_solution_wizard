"""
Test stakeholder category mapping for backward compatibility.

This test verifies that old category names in JSON are correctly mapped
to current category names when uploading.
"""

import json
from wizard_data import (
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_stakeholders_category_mapping():
    """Test that stakeholder categories are preserved correctly (no mapping)."""
    
    print("\n=== Testing Stakeholders Category Preservation ===")
    
    # Test JSON with old category names
    test_json = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {
                "Technical Stakeholders": "Individual Network Engineer",
                "Business Stakeholders": "IT Director",  # This will be preserved as-is
                "User Stakeholders": "Customers",  # This will be preserved as-is
                "User and Customer Stakeholders": "Internal users (ITSM / Service Desk)",
                "Governance and Risk Stakeholders": "None",
                "Business and Leadership Stakeholders": "None",
                "External/Vendor/Partner Stakeholders": "None"
            },
            "other": ""
        }
    }
    
    # Restore session state from JSON
    restored_updates = restore_session_state_from_data(test_json)
    
    # Verify categories are preserved as-is
    choices = restored_updates["stakeholders_choices"]
    
    # All categories should be preserved exactly as they were
    assert "Business Stakeholders" in choices, \
        "'Business Stakeholders' should be preserved"
    assert choices["Business Stakeholders"] == "IT Director", \
        f"Expected 'IT Director' but got '{choices['Business Stakeholders']}'"
    
    assert "User Stakeholders" in choices, \
        "'User Stakeholders' should be preserved"
    assert choices["User Stakeholders"] == "Customers", \
        f"Expected 'Customers' but got '{choices['User Stakeholders']}'"
    
    # Should preserve all categories
    assert choices["Technical Stakeholders"] == "Individual Network Engineer"
    assert choices["Governance and Risk Stakeholders"] == "None"
    assert choices["Business and Leadership Stakeholders"] == "None"
    assert choices["External/Vendor/Partner Stakeholders"] == "None"
    
    print("✅ All stakeholder categories preserved exactly as provided")
    
    print("\n✅ Category mapping test passed!")


def test_stakeholders_mapping_with_actual_values():
    """Test preservation with the actual values from the user's JSON."""
    
    print("\n=== Testing with User's Actual JSON Values ===")
    
    # Use the exact JSON structure from the user
    user_json = {
        "initiative": {
            "title": "User Project"
        },
        "stakeholders": {
            "choices": {
                "Technical Stakeholders": "Individual Network Engineer",
                "Business Stakeholders": "IT Director",
                "User Stakeholders": "Customers",
                "User and Customer Stakeholders": "None",
                "Governance and Risk Stakeholders": "None",
                "Business and Leadership Stakeholders": "None",
                "External/Vendor/Partner Stakeholders": "None"
            }
        }
    }
    
    # Restore session state
    restored_updates = restore_session_state_from_data(user_json)
    
    # Verify all categories are preserved exactly
    choices = restored_updates["stakeholders_choices"]
    
    # All values should be preserved exactly as provided
    assert choices["Technical Stakeholders"] == "Individual Network Engineer"
    assert choices["Business Stakeholders"] == "IT Director"
    assert choices["User Stakeholders"] == "Customers"
    assert choices["User and Customer Stakeholders"] == "None"
    assert choices["Governance and Risk Stakeholders"] == "None"
    assert choices["Business and Leadership Stakeholders"] == "None"
    assert choices["External/Vendor/Partner Stakeholders"] == "None"
    
    print("✅ User's JSON values preserved exactly")
    print(f"  - All categories preserved with their original values")
    
    # Simulate widget initialization to verify they would display
    for category, value in choices.items():
        if value not in ["None", ""]:
            print(f"  - Widget '{category}' would display: {value}")
    
    print("\n✅ User JSON preservation test passed!")


def test_stakeholders_mapping_edge_cases():
    """Test edge cases for category mapping."""
    
    print("\n=== Testing Category Mapping Edge Cases ===")
    
    # Test with unknown category (should remain unchanged)
    test_json_1 = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {
                "Unknown Category": "Some value",
                "Technical Stakeholders": "Network team"
            }
        }
    }
    
    restored_1 = restore_session_state_from_data(test_json_1)
    choices_1 = restored_1["stakeholders_choices"]
    
    # Unknown category should remain as-is
    assert "Unknown Category" in choices_1, \
        "Unknown category should be preserved"
    assert choices_1["Unknown Category"] == "Some value", \
        "Unknown category value should be preserved"
    
    print("✅ Unknown categories preserved correctly")
    
    # Test with empty choices
    test_json_2 = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {}
        }
    }
    
    restored_2 = restore_session_state_from_data(test_json_2)
    assert restored_2["stakeholders_choices"] == {}, \
        "Empty choices should remain empty"
    
    print("✅ Empty choices handled correctly")
    
    # Test with all old categories (they should be preserved as-is)
    test_json_3 = {
        "initiative": {"title": "Test"},
        "stakeholders": {
            "choices": {
                "Business Stakeholders": "CEO",
                "User Stakeholders": "End Users"
            }
        }
    }
    
    restored_3 = restore_session_state_from_data(test_json_3)
    choices_3 = restored_3["stakeholders_choices"]
    
    assert len(choices_3) == 2, \
        f"Expected 2 categories but got {len(choices_3)}"
    assert "Business Stakeholders" in choices_3
    assert "User Stakeholders" in choices_3
    assert choices_3["Business Stakeholders"] == "CEO"
    assert choices_3["User Stakeholders"] == "End Users"
    
    print("✅ All categories preserved exactly as provided")
    
    print("\n✅ Edge cases test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Stakeholders Category Mapping")
    print("=" * 60)
    
    test_stakeholders_category_mapping()
    test_stakeholders_mapping_with_actual_values()
    test_stakeholders_mapping_edge_cases()
    
    print("\n" + "=" * 60)
    print("🎉 All category mapping tests passed successfully!")
    print("=" * 60)
