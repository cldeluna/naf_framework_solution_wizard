#!/usr/bin/env python3
"""Test JSON upload with author field."""

import json
import sys
from pathlib import Path

# Add parent directory to path to import wizard_data
sys.path.insert(0, str(Path(__file__).parent.parent))
from wizard_data import restore_session_state_from_data

def test_author_upload():
    """Test that author field is properly restored from JSON."""
    
    print("Testing author field restoration from JSON upload...")
    
    # Create test JSON with author
    test_json = {
        "initiative": {
            "author": "John Doe",
            "title": "Test Upload Project",
            "description": "Testing JSON upload with author"
        }
    }
    
    # Restore session state from JSON
    restored = restore_session_state_from_data(test_json)
    
    # Verify author is restored
    assert "_wizard_author" in restored, "Author field missing from restored session state"
    assert restored["_wizard_author"] == "John Doe", f"Expected 'John Doe', got '{restored['_wizard_author']}'"
    
    print("✓ Author field correctly restored from JSON upload")
    
    # Test with empty author
    test_json_empty = {
        "initiative": {
            "author": "",
            "title": "Empty Author Test"
        }
    }
    
    restored_empty = restore_session_state_from_data(test_json_empty)
    assert restored_empty["_wizard_author"] == "", "Empty author should be preserved"
    
    print("✓ Empty author field handled correctly")
    
    # Test with missing author
    test_json_missing = {
        "initiative": {
            "title": "Missing Author Test"
        }
    }
    
    restored_missing = restore_session_state_from_data(test_json_missing)
    # Author should not be in updates if not in original data
    assert "_wizard_author" not in restored_missing, "Missing author should not be in updates"
    
    print("✓ Missing author field handled correctly")
    
    print("\n✅ All JSON upload tests passed!")
    
    # Save test JSON for manual upload testing
    test_file = Path(__file__).parent / "exports" / "test_author_upload.json"
    with open(test_file, "w") as f:
        json.dump(test_json, f, indent=2)
    print(f"\nTest JSON saved to '{test_file}' for manual upload testing")

if __name__ == "__main__":
    test_author_upload()
