#!/usr/bin/env python3
"""Test the author field implementation."""

import json
import sys
from pathlib import Path

# Add parent directory to path to import wizard_data
sys.path.insert(0, str(Path(__file__).parent.parent))
from wizard_data import build_wizard_payload, restore_session_state_from_data


def test_author_field():
    """Test that author field is properly handled in payload and restoration."""
    
    print("Testing author field implementation...")
    
    # Test 1: Build payload with author
    print("\n1. Testing payload building with author...")
    session_state = {
        "_wizard_author": "John Doe",
        "_wizard_automation_title": "Test Project",
        "_wizard_automation_description": "Test description",
        "_wizard_category": "Configuration Management",
    }
    
    payload = build_wizard_payload(session_state)
    
    # Verify author is in payload
    assert "author" in payload["initiative"], "Author field missing from payload"
    assert payload["initiative"]["author"] == "John Doe", f"Expected 'John Doe', got '{payload['initiative']['author']}'"
    print("✓ Author field correctly included in payload")
    
    # Test 2: Restore session state with author
    print("\n2. Testing session state restoration with author...")
    test_data = {
        "initiative": {
            "author": "Jane Smith",
            "title": "Restored Project",
            "description": "Restored description",
        }
    }
    
    restored = restore_session_state_from_data(test_data)
    
    # Verify author is restored
    assert "_wizard_author" in restored, "Author field missing from restored session state"
    assert restored["_wizard_author"] == "Jane Smith", f"Expected 'Jane Smith', got '{restored['_wizard_author']}'"
    print("✓ Author field correctly restored from JSON")
    
    # Test 3: Round-trip test
    print("\n3. Testing round-trip (payload -> restore -> payload)...")
    original_author = "Alice Johnson"
    session_state = {
        "_wizard_author": original_author,
        "_wizard_automation_title": "Round Trip Test",
        "_wizard_automation_description": "Testing round trip",
    }
    
    # Build payload
    payload1 = build_wizard_payload(session_state)
    
    # Restore from payload
    restored = restore_session_state_from_data(payload1)
    
    # Build payload again
    payload2 = build_wizard_payload(restored)
    
    # Verify author survived round-trip
    assert payload2["initiative"]["author"] == original_author, f"Round-trip failed: expected '{original_author}', got '{payload2['initiative']['author']}'"
    print("✓ Author field survived round-trip successfully")
    
    # Test 4: Empty author handling
    print("\n4. Testing empty author handling...")
    session_state_empty = {
        "_wizard_author": "",
        "_wizard_automation_title": "Empty Author Test",
    }
    
    payload_empty = build_wizard_payload(session_state_empty)
    assert payload_empty["initiative"]["author"] == "", "Empty author should be preserved"
    print("✓ Empty author field handled correctly")
    
    # Test 5: None author handling
    print("\n5. Testing None author handling...")
    test_data_none = {
        "initiative": {
            "title": "Test",
            "author": None,
        }
    }
    
    restored_none = restore_session_state_from_data(test_data_none)
    assert restored_none["_wizard_author"] == "", "None author should be converted to empty string"
    print("✓ None author field handled correctly")
    
    print("\n✅ All author field tests passed!")
    
    # Save sample JSON for inspection
    sample_file = Path(__file__).parent / "exports" / "sample_author_payload.json"
    with open(sample_file, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\nSample payload saved to '{sample_file}'")


if __name__ == "__main__":
    test_author_field()
