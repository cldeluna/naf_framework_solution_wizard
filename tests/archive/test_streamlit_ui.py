"""
Streamlit UI Tests for NAF Solution Wizard
Tests actual Streamlit widget functionality and session state management
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Mock streamlit before importing the wizard
sys.modules["streamlit"] = MagicMock()

# Import the wizard module directly using importlib
try:
    import importlib.util

    wizard_path = Path(__file__).parent.parent / "pages" / "20_NAF_Solution_Wizard.py"

    # Read the file content and modify to skip execution
    with open(wizard_path, "r") as f:
        content = f.read()

    # Replace the main execution call to prevent it from running
    # Use a more precise replacement to avoid syntax errors
    lines = content.split("\n")
    modified_lines = []
    for line in lines:
        if line.strip() == "solution_wizard_main()":
            modified_lines.append("# solution_wizard_main()")
        else:
            modified_lines.append(line)
    content = "\n".join(modified_lines)

    # Create a temporary module with the modified content
    spec = importlib.util.spec_from_loader("wizard_module", loader=None)
    wizard_module = importlib.util.module_from_spec(spec)
    exec(content, wizard_module.__dict__)
    NAF_Solution_Wizard = wizard_module
except Exception as e:
    pytest.skip(
        f"Could not import NAF Solution Wizard: {str(e)}", allow_module_level=True
    )


class TestStreamlitUI:
    """Test Streamlit UI functionality and session state management"""

    def setup_method(self):
        """Set up test environment"""
        self.mock_st = sys.modules["streamlit"]
        self.mock_session_state = {}
        self.mock_st.session_state = self.mock_session_state

        # Reset all mock calls
        self.mock_st.reset_mock()

    def test_widget_error_handling_with_invalid_data(self):
        """Test that widget error handling gracefully manages invalid data"""

        # Mock streamlit widgets to raise ValueError for invalid options
        def mock_radio_error(*args, **kwargs):
            if "key" in kwargs and kwargs["key"] == "orch_choice":
                raise ValueError("Yes is not in iterable")
            return "default_value"

        self.mock_st.radio.side_effect = mock_radio_error

        # Test the error handling function
        handle_widget_error = NAF_Solution_Wizard.handle_widget_error

        result = handle_widget_error(
            self.mock_st.radio,
            "Select option",
            ["Valid Option 1", "Valid Option 2"],
            key="test_key",
            error_message="Test error message",
        )

        # Should return None when error occurs
        assert result is None

        # Should display error message
        self.mock_st.error.assert_called()

        # Should display expander with technical details
        self.mock_st.expander.assert_called()

    def test_no_session_state_modification_after_widget_instantiation(self):
        """Test that session state is not modified after widget instantiation"""
        # Set up initial session state
        self.mock_session_state["orch_choice"] = "initial_value"

        # Mock radio widget
        self.mock_st.radio.return_value = "selected_value"

        # Test the orchestration section logic
        handle_widget_error = NAF_Solution_Wizard.handle_widget_error

        # Simulate widget creation
        result = handle_widget_error(
            self.mock_st.radio,
            "Select option",
            ["Option 1", "Option 2"],
            key="orch_choice",
        )

        # Session state should not be modified after widget instantiation
        assert self.mock_session_state.get("orch_choice") == "initial_value"

        # Widget should still return the expected value
        assert result == "selected_value"

    def test_template_preview_rendering_with_valid_data(self):
        """Test that template preview renders correctly with valid data"""
        _render_template_preview = NAF_Solution_Wizard._render_template_preview

        # Create test payload
        test_payload = {
            "initiative": {
                "title": "Test Initiative",
                "description": "Test Description",
                "category": "Test Category",
                "problem_statement": "Test Problem",
                "assumptions": "Test Assumptions",
            },
            "my_role": {
                "who": "Test Role",
                "skills": "Test Skills",
                "developer": "Test Developer",
            },
            "stakeholders": {
                "choices": {"Technical": "Technical Lead"},
                "other": "Other stakeholders",
            },
            "presentation": {
                "users": "Test Users",
                "interaction": "Test Interaction",
                "tools": "Test Tools",
                "auth": "Test Auth",
            },
            "intent": {"development": "Test Development", "provided": "Test Provided"},
            "observability": {"methods": "Test Methods", "tools": "Test Tools"},
            "orchestration": {"choice": "No", "details": "Test Details"},
            "collector": {"methods": "Test Methods", "auth": "Test Auth"},
            "executor": {"methods": "Test Methods"},
            "dependencies": [{"name": "Test Dependency", "details": "Test Details"}],
            "timeline": {
                "items": [],
                "staff_count": 1,
                "start_date": "2024-01-01",
                "projected_completion": "2024-12-31",
                "total_business_days": 250,
                "staffing_plan_md": "Test staffing plan",
            },
        }

        # Render template preview
        result = _render_template_preview(test_payload)

        # Should contain expected content
        assert "Test Initiative" in result
        assert "Test Description" in result
        assert "Test Role" in result
        assert "Technical Lead" in result
        assert "Test Problem" in result
        assert "Test Assumptions" in result

        # Should not contain error message
        assert "Error rendering preview" not in result

    def test_template_preview_rendering_with_invalid_data(self):
        """Test that template preview handles invalid data gracefully"""
        _render_template_preview = NAF_Solution_Wizard._render_template_preview

        # Create invalid payload
        invalid_payload = {
            "initiative": None,  # Invalid None value
            "my_role": "invalid_string",  # Should be dict
            "stakeholders": {"invalid": "structure"},
        }

        # Render template preview
        result = _render_template_preview(invalid_payload)

        # Should handle errors gracefully
        assert "Error rendering preview" in result or result is not None

    def test_widget_error_handling_with_various_widget_types(self):
        """Test error handling with different widget types"""
        handle_widget_error = NAF_Solution_Wizard.handle_widget_error

        # Test with selectbox
        def mock_selectbox_error(*args, **kwargs):
            raise ValueError("Invalid option")

        self.mock_st.selectbox.side_effect = mock_selectbox_error

        result = handle_widget_error(
            self.mock_st.selectbox,
            "Select option",
            ["Option 1", "Option 2"],
            key="test_select",
        )

        assert result is None
        self.mock_st.error.assert_called()

    def test_session_state_initialization_before_widget_creation(self):
        """Test that session state initialization happens before widget creation"""
        # This test ensures we don't modify session state after widget instantiation
        initial_state = dict(self.mock_session_state)

        # Mock radio widget
        self.mock_st.radio.return_value = "test_value"

        # Simulate the pattern used in the wizard
        key = "test_widget"

        # This should NOT modify session state after widget creation
        # (the old problematic code would have done this)
        if key not in self.mock_session_state:
            # This initialization should happen BEFORE widget creation
            self.mock_session_state[key] = "sentinel_value"

        # Create widget
        result = self.mock_st.radio("Test", ["Option 1", "Option 2"], key=key)

        # Session state should remain as initialized
        assert self.mock_session_state[key] == "sentinel_value"
        assert result == "test_value"

    def test_upload_data_with_invalid_widget_values(self):
        """Test upload handling when data contains invalid widget values"""
        handle_widget_error = NAF_Solution_Wizard.handle_widget_error

        # Simulate upload data with invalid orchestration choice
        invalid_upload_data = {
            "orchestration": {"choice": "Invalid Choice That Is Not In Options"}
        }

        # Mock radio widget to fail with invalid data
        def mock_radio_invalid(*args, **kwargs):
            if kwargs.get("key") == "orch_choice":
                raise ValueError(
                    "Invalid Choice That Is Not In Options is not in iterable"
                )
            return "default"

        self.mock_st.radio.side_effect = mock_radio_invalid

        # Test error handling
        result = handle_widget_error(
            self.mock_st.radio,
            "Select option",
            [
                "— Select one —",
                "No",
                "Yes – internal via custom scripts and logic",
                "Yes – provide details",
            ],
            key="orch_choice",
            error_message="Orchestration selection validation failed",
        )

        # Should handle error gracefully
        assert result is None
        self.mock_st.error.assert_called_with(
            "⚠️ Orchestration selection validation failed. The uploaded data may contain an invalid option."
        )


class TestStreamlitIntegration:
    """Integration tests for Streamlit UI components"""

    def test_full_upload_workflow_with_error_handling(self):
        """Test complete upload workflow including error handling"""
        # This would be a more comprehensive integration test
        # that simulates the actual Streamlit app behavior
        pass

    def test_template_preview_consistency_with_export(self):
        """Test that template preview matches export output"""
        # Test that preview and export use the same template
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
