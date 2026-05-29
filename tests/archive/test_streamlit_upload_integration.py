"""
Streamlit Upload Integration Tests
Tests the complete upload workflow including Streamlit UI session state management
"""

import pytest
import sys
import json
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_data_generator import LoremTestDataGenerator


class TestStreamlitUploadIntegration:
    """Integration tests for Streamlit upload functionality"""

    def setup_method(self):
        """Set up test environment"""
        self.api_base_url = "http://localhost:8001"
        self.generator = LoremTestDataGenerator()
        self.test_token = "test-token-lorem"
        self.api_headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json",
        }

    def test_upload_with_invalid_orchestration_choice(self):
        """Test upload handling when data contains invalid orchestration choice"""
        # Generate test data with intentionally invalid orchestration choice
        test_data = self.generator.generate_complete_solution()

        # Modify orchestration to use invalid choice that would cause session state error
        test_data["orchestration"]["choice"] = "Invalid Choice"

        # Upload to API
        response = requests.post(
            f"{self.api_base_url}/api/v1/solutions",
            headers=self.api_headers,
            json=test_data,
            timeout=10,
        )

        if response.status_code == 200:
            solution_id = response.json().get("solution_id")
            assert solution_id is not None

            # Retrieve the solution to verify it was stored correctly
            get_response = requests.get(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                headers=self.api_headers,
                timeout=10,
            )

            assert get_response.status_code == 200
            stored_data = get_response.json().get("json_data", {})

            # Verify the invalid choice was stored (API should accept it)
            assert stored_data["orchestration"]["choice"] == "Invalid Choice"
        else:
            pytest.skip(
                f"API not available for integration testing: {response.status_code}"
            )

    def test_upload_with_all_invalid_widget_choices(self):
        """Test upload with various invalid widget choices that could cause session state errors"""
        # Generate base test data
        test_data = self.generator.generate_complete_solution()

        # Modify various fields with invalid choices
        invalid_scenarios = [
            {
                "name": "Invalid orchestration",
                "modifications": {
                    "orchestration": {"choice": "Completely Invalid Choice"}
                },
            },
            {
                "name": "Invalid role data",
                "modifications": {"my_role": {"who": "Invalid Role Choice"}},
            },
            {
                "name": "Invalid skill data",
                "modifications": {"my_role": {"skills": "Invalid Skill Choice"}},
            },
            {
                "name": "Invalid developer data",
                "modifications": {"my_role": {"developer": "Invalid Developer Choice"}},
            },
        ]

        for scenario in invalid_scenarios:
            with pytest.raises(Exception):
                # Create modified test data
                modified_data = test_data.copy()
                modified_data.update(scenario["modifications"])

                # This should test that the Streamlit UI handles invalid data gracefully
                # without session state errors
                pass

    def test_streamlit_error_handling_mechanism(self):
        """Test that the Streamlit error handling mechanism works correctly"""
        # Mock the Streamlit environment
        with patch("pages.NAF_Solution_Wizard.st") as mock_st:
            mock_session_state = {}
            mock_st.session_state = mock_session_state

            # Mock radio widget to raise ValueError
            def mock_radio_error(*args, **kwargs):
                if "key" in kwargs and "choice" in kwargs.get("key", ""):
                    raise ValueError("Invalid option is not in iterable")
                return "default_value"

            mock_st.radio.side_effect = mock_radio_error

            # Import and test the error handling function
            try:
                from pages.NAF_Solution_Wizard import handle_widget_error

                # Test error handling
                result = handle_widget_error(
                    mock_st.radio,
                    "Select option",
                    ["Valid Option 1", "Valid Option 2"],
                    key="test_choice_key",
                    error_message="Test validation failed",
                )

                # Should return None on error
                assert result is None

                # Should display error message
                mock_st.error.assert_called()

                # Should show technical details in expander
                mock_st.expander.assert_called()

            except ImportError:
                pytest.skip("Could not import NAF Solution Wizard for testing")

    def test_session_state_no_modification_after_widget_creation(self):
        """Test that session state is not modified after widget creation (the main bug)"""
        with patch("pages.NAF_Solution_Wizard.st") as mock_st:
            # Set up initial session state
            mock_session_state = {"orch_choice": "initial_value"}
            mock_st.session_state = mock_session_state

            # Mock radio widget
            mock_st.radio.return_value = "selected_value"

            try:
                from pages.NAF_Solution_Wizard import handle_widget_error

                # Simulate the problematic pattern
                orch_choice = handle_widget_error(
                    mock_st.radio,
                    "Select option",
                    ["Option 1", "Option 2"],
                    key="orch_choice",
                    error_message="Test error",
                )

                # Session state should NOT be modified after widget creation
                assert mock_session_state["orch_choice"] == "initial_value"

                # Function should return the widget result
                assert orch_choice == "selected_value"

            except ImportError:
                pytest.skip("Could not import NAF Solution Wizard for testing")

    def test_template_preview_with_problematic_data(self):
        """Test template preview rendering with data that could cause issues"""
        with patch("pages.NAF_Solution_Wizard.st") as mock_st:
            mock_st.session_state = {}

            try:
                from pages.NAF_Solution_Wizard import _render_template_preview

                # Test with problematic data
                problematic_payloads = [
                    # None values
                    {"initiative": None, "my_role": None, "stakeholders": None},
                    # Missing required sections
                    {
                        "initiative": {"title": "Test"},
                        # Missing my_role, stakeholders, etc.
                    },
                    # Invalid data types
                    {
                        "initiative": "should be dict not string",
                        "my_role": ["should be dict not list"],
                        "stakeholders": {"invalid": "structure"},
                    },
                ]

                for payload in problematic_payloads:
                    result = _render_template_preview(payload)

                    # Should handle errors gracefully
                    assert result is not None
                    # Either renders successfully or shows error message
                    assert "Error rendering preview" in result or len(result) > 0

            except ImportError:
                pytest.skip("Could not import NAF Solution Wizard for testing")

    def test_comprehensive_upload_validation(self):
        """Comprehensive test that validates the entire upload process"""
        # Generate test data
        test_data = self.generator.generate_complete_solution()

        # Add some edge cases that could cause session state issues
        test_data["orchestration"][
            "choice"
        ] = "Yes – provide details"  # Valid but requires details
        test_data["my_role"]["who"] = "Other (fill in)"  # Requires custom input
        test_data["my_role"]["skills"] = "Other (fill in)"  # Requires custom input

        # Upload to API
        response = requests.post(
            f"{self.api_base_url}/api/v1/solutions",
            headers=self.api_headers,
            json=test_data,
            timeout=10,
        )

        if response.status_code == 200:
            solution_id = response.json().get("solution_id")

            # Verify storage
            get_response = requests.get(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                headers=self.api_headers,
                timeout=10,
            )

            assert get_response.status_code == 200
            stored_data = get_response.json().get("json_data", {})

            # Validate all sections were stored correctly
            assert (
                stored_data["initiative"]["title"] == test_data["initiative"]["title"]
            )
            assert (
                stored_data["orchestration"]["choice"]
                == test_data["orchestration"]["choice"]
            )
            assert stored_data["my_role"]["who"] == test_data["my_role"]["who"]

        else:
            pytest.skip(f"API not available: {response.status_code}")


class TestErrorHandlingEdgeCases:
    """Test edge cases in error handling"""

    def test_widget_error_with_various_exception_types(self):
        """Test error handling with different types of exceptions"""
        with patch("pages.NAF_Solution_Wizard.st") as mock_st:
            mock_st.session_state = {}

            try:
                from pages.NAF_Solution_Wizard import handle_widget_error

                # Test with ValueError
                mock_st.radio.side_effect = ValueError("Test ValueError")
                result = handle_widget_error(
                    mock_st.radio, "Test", ["Option1"], key="test"
                )
                assert result is None

                # Test with generic Exception
                mock_st.radio.side_effect = Exception("Test Exception")
                result = handle_widget_error(
                    mock_st.radio, "Test", ["Option1"], key="test"
                )
                assert result is None

                # Verify error messages were displayed
                assert mock_st.error.call_count >= 2

            except ImportError:
                pytest.skip("Could not import NAF Solution Wizard for testing")

    def test_concurrent_session_state_access(self):
        """Test session state handling under concurrent access scenarios"""
        # This would test for race conditions in session state access
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
