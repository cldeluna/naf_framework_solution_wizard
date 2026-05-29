"""
Test that stakeholders widgets are properly initialized from uploaded JSON.

This test simulates the widget initialization process to ensure uploaded
stakeholder values are correctly displayed in the UI.
"""

import json
from wizard_data import (
    restore_session_state_from_data,
    get_title_only_session_state
)


def test_stakeholders_widget_initialization():
    """Test that stakeholders widget keys are properly set from uploaded data."""
    
    print("\n=== Testing Stakeholders Widget Initialization ===")
    
    # Create test JSON with stakeholders data
    test_json = {
        "initiative": {
            "title": "Test Project",
            "description": "Test description"
        },
        "stakeholders": {
            "choices": {
                "Technical Stakeholders": "Network Engineering team",
                "User and Customer Stakeholders": "None",
                "Governance and Risk Stakeholders": "Security officer / CISO staff",
                "Business and Leadership Stakeholders": "Executive sponsor (CIO / CTO / VP of IT)",
                "External/Vendor/Partner Stakeholders": "None"
            },
            "other": "Custom vendor partner"
        }
    }
    
    # Restore session state from JSON
    restored_updates = restore_session_state_from_data(test_json)
    
    # Verify stakeholders_choices is restored
    assert "stakeholders_choices" in restored_updates, \
        "stakeholders_choices not found in restored updates"
    
    choices = restored_updates["stakeholders_choices"]
    assert choices["Technical Stakeholders"] == "Network Engineering team", \
        f"Expected 'Network Engineering team' but got '{choices['Technical Stakeholders']}'"
    assert choices["User and Customer Stakeholders"] == "None", \
        f"Expected 'None' but got '{choices['User and Customer Stakeholders']}'"
    assert choices["Governance and Risk Stakeholders"] == "Security officer / CISO staff", \
        f"Expected 'Security officer / CISO staff' but got '{choices['Governance and Risk Stakeholders']}'"
    
    # Verify other text is restored
    assert restored_updates["stakeholders_other_text"] == "Custom vendor partner", \
        f"Expected 'Custom vendor partner' but got '{restored_updates['stakeholders_other_text']}'"
    
    print("✅ Stakeholders data correctly restored to session state")
    
    # Simulate widget initialization (what happens in pages/20_NAF_Solution_Wizard.py)
    # The widgets use keys like "stakeholders_choice_Technical_Stakeholders"
    
    # Test that the widget initialization logic would work
    widget_initializations = {}
    for category, value in choices.items():
        # Simulate the sanitization that happens in _sanitize_title()
        sanitized = category.replace(" ", "_").replace("/", "_").replace("&", "_")
        widget_key = f"stakeholders_choice_{sanitized}"
        
        # This is what the widget initialization code does:
        # If the widget key doesn't exist, it sets it from the restored choices
        widget_initializations[widget_key] = value if value else "— Select one —"
    
    # Verify widget initializations
    assert widget_initializations["stakeholders_choice_Technical_Stakeholders"] == "Network Engineering team"
    assert widget_initializations["stakeholders_choice_User_and_Customer_Stakeholders"] == "None"
    assert widget_initializations["stakeholders_choice_Governance_and_Risk_Stakeholders"] == "Security officer / CISO staff"
    
    print("✅ Widget keys would be correctly initialized from uploaded values")
    
    print("\n✅ Stakeholders widget initialization test passed!")


def test_stakeholders_widget_with_empty_data():
    """Test widget initialization when stakeholders data is empty."""
    
    print("\n=== Testing Widget Initialization with Empty Data ===")
    
    # Test with empty stakeholders
    test_json = {
        "initiative": {"title": "Test"},
        "stakeholders": {}
    }
    
    restored_updates = restore_session_state_from_data(test_json)
    
    # Should have empty choices
    assert restored_updates["stakeholders_choices"] == {}
    assert restored_updates["stakeholders_other_text"] == ""
    
    print("✅ Empty stakeholders data handled correctly")
    
    # Test with None stakeholders
    test_json_2 = {
        "initiative": {"title": "Test"},
        "stakeholders": None
    }
    
    restored_updates_2 = restore_session_state_from_data(test_json_2)
    
    # Should have empty choices
    assert restored_updates_2["stakeholders_choices"] == {}
    assert restored_updates_2["stakeholders_other_text"] == ""
    
    print("✅ None stakeholders data handled correctly")
    
    print("\n✅ Empty data widget initialization test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Stakeholders Widget Initialization")
    print("=" * 60)
    
    test_stakeholders_widget_initialization()
    test_stakeholders_widget_with_empty_data()
    
    print("\n" + "=" * 60)
    print("🎉 All widget initialization tests passed!")
    print("=" * 60)
