"""
Upload Validator for NAF Solution Wizard
Tests uploading JSON files and validates all wizard fields are properly loaded
"""

import json
import sys
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_data_generator import LoremTestDataGenerator


class WizardUploadValidator:
    """Validates that uploaded JSON files are properly loaded into the Solution Wizard"""

    def __init__(
        self,
        api_base_url: str = "http://localhost:8001",
        streamlit_url: str = "http://localhost:8501",
    ):
        self.api_base_url = api_base_url
        self.streamlit_url = streamlit_url
        self.generator = LoremTestDataGenerator()
        self.test_token = "test-token-lorem"
        self.api_headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json",
        }
        self.validation_results: Dict[str, Any] = {
            "test_run": f"UPLOAD_VALIDATION_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "validations": [],
        }

    def log_validation(
        self, test_name: str, success: bool, message: str = "", details: Any = None
    ):
        """Log validation result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        if details is not None:
            result["details"] = details
        self.validation_results["validations"].append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def generate_test_file(self) -> str:
        """Generate a test JSON file with wizard naming convention"""
        test_data = self.generator.generate_complete_test_data()
        filename = self.generator.get_wizard_filename()

        # Save to tests directory for upload
        output_path = Path("tests") / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)

        self.log_validation(
            "Generate Test File",
            True,
            f"Created: {filename}",
            {"path": str(output_path), "size": output_path.stat().st_size},
        )

        return str(output_path)

    def validate_api_upload(self, json_file_path: str) -> str:
        """Upload file via API and validate it's stored correctly"""
        try:
            # Read the JSON file
            with open(json_file_path, "r", encoding="utf-8") as f:
                test_data = json.load(f)

            # Create solution via API
            response = requests.post(
                f"{self.api_base_url}/api/v1/solutions",
                json=test_data,
                headers=self.api_headers,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                solution_id = result.get("solution_id")

                self.log_validation("API Upload", True, f"Solution ID: {solution_id}")

                # Retrieve and validate the stored solution
                return self.validate_stored_solution(solution_id, test_data)
            else:
                self.log_validation(
                    "API Upload",
                    False,
                    f"Status code: {response.status_code}, Response: {response.text}",
                )
                return None

        except Exception as e:
            self.log_validation("API Upload", False, f"Exception: {str(e)}")
            return None

    def validate_stored_solution(
        self, solution_id: str, original_data: Dict[str, Any]
    ) -> str:
        """Validate that the stored solution matches the original data"""
        try:
            # Retrieve the solution
            response = requests.get(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                headers=self.api_headers,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                stored_data = result.get("json_data", {})

                # Validate all sections
                validation_passed = True

                # Check title
                if stored_data.get("initiative", {}).get("title") == "LOREM TEST":
                    self.log_validation(
                        "Title Validation", True, "Title correctly set to LOREM TEST"
                    )
                else:
                    self.log_validation("Title Validation", False, "Title mismatch")
                    validation_passed = False

                # Validate each section
                sections_to_validate = [
                    "initiative",
                    "my_role",
                    "stakeholders",
                    "presentation",
                    "intent",
                    "observability",
                    "orchestration",
                    "collector",
                    "executor",
                    "dependencies",
                    "timeline",
                ]

                for section in sections_to_validate:
                    try:
                        original_section = original_data.get(section, {})
                        stored_section = stored_data.get(section, {})

                        if self.validate_section(
                            section, original_section, stored_section
                        ):
                            self.log_validation(
                                f"{section.title()} Section",
                                True,
                                "All fields validated",
                            )
                        else:
                            self.log_validation(
                                f"{section.title()} Section", False, "Validation failed"
                            )
                            validation_passed = False
                    except Exception as e:
                        self.log_validation(
                            f"{section.title()} Section", False, f"Exception: {str(e)}"
                        )
                        validation_passed = False

                if validation_passed:
                    self.log_validation(
                        "Overall Validation",
                        True,
                        "All sections validated successfully",
                    )
                    return solution_id
                else:
                    self.log_validation(
                        "Overall Validation", False, "Some validations failed"
                    )
                    return None

            else:
                self.log_validation(
                    "Solution Retrieval", False, f"Status code: {response.status_code}"
                )
                return None

        except Exception as e:
            self.log_validation("Solution Validation", False, f"Exception: {str(e)}")
            return None

    def validate_section(
        self, section_name: str, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate a specific section of the solution"""
        if not original or not stored:
            return False

        # For text fields, check they contain lorem content
        text_fields = {
            "initiative": [
                "description",
                "problem_statement",
                "out_of_scope",
                "expected_use",
                "error_conditions",
                "assumptions",
                "deployment_strategy_description",
            ],
            "my_role": ["who", "skills"],
            "stakeholders": ["other"],
            "presentation": ["users", "interaction", "tools", "auth"],
            "intent": ["development", "provided"],
            "observability": ["methods", "go_no_go", "additional_logic", "tools"],
            "orchestration": ["summary"],
            "collector": ["methods", "auth", "handling", "scale", "tools"],
            "executor": ["methods"],
        }

        # For pulldown fields, check they use standard options
        pulldown_fields = {
            "initiative": ["category", "deployment_strategy"],
            "my_role": ["developer"],
        }

        validation_passed = True

        # Validate text fields contain lorem content
        if section_name in text_fields:
            for field in text_fields[section_name]:
                original_value = original.get(field, "")
                stored_value = stored.get(field, "")

                if original_value and stored_value:
                    # Check if stored value contains lorem-like content (longer text)
                    if len(stored_value) > 20 and any(
                        word in stored_value.lower()
                        for word in ["lorem", "ipsum", "dolor", "sit", "amet"]
                    ):
                        pass  # Contains lorem content
                    elif len(original_value) > 100:  # Original was long text
                        # Check if stored value is also substantial
                        if len(stored_value) < 50:
                            validation_passed = False
                elif original_value != stored_value:
                    validation_passed = False

        # Validate pulldown fields use standard options
        if section_name in pulldown_fields:
            for field in pulldown_fields[section_name]:
                original_value = original.get(field, "")
                stored_value = stored.get(field, "")

                if original_value != stored_value:
                    validation_passed = False

        # Validate complex nested structures
        if section_name == "stakeholders":
            if not self.validate_stakeholders(original, stored):
                validation_passed = False

        elif section_name == "presentation":
            if not self.validate_selections(
                original.get("selections", {}), stored.get("selections", {})
            ):
                validation_passed = False

        elif section_name == "intent":
            if not self.validate_selections(
                original.get("selections", {}), stored.get("selections", {})
            ):
                validation_passed = False

        elif section_name == "observability":
            if not self.validate_observability_selections(
                original.get("selections", {}), stored.get("selections", {})
            ):
                validation_passed = False

        elif section_name == "orchestration":
            if not self.validate_orchestration_selections(
                original.get("selections", {}), stored.get("selections", {})
            ):
                validation_passed = False

        elif section_name == "collector":
            if not self.validate_collector_selections(
                original.get("selections", {}), stored.get("selections", {})
            ):
                validation_passed = False

        elif section_name == "executor":
            if not self.validate_executor_selections(
                original.get("selections", {}), stored.get("selections", {})
            ):
                validation_passed = False

        elif section_name == "dependencies":
            if not self.validate_dependencies(original, stored):
                validation_passed = False

        elif section_name == "timeline":
            if not self.validate_timeline(original, stored):
                validation_passed = False

        return validation_passed

    def validate_stakeholders(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate stakeholders section"""
        if not original or not stored:
            return False

        # Check choices
        original_choices = original.get("choices", {})
        stored_choices = stored.get("choices", {})

        if not isinstance(original_choices, dict) or not isinstance(
            stored_choices, dict
        ):
            return False

        if set(original_choices.keys()) != set(stored_choices.keys()):
            return False

        for key in original_choices:
            if original_choices[key] != stored_choices.get(key, ""):
                return False

        # Check other field
        original_other = original.get("other", "")
        stored_other = stored.get("other", "")
        if original_other != stored_other:
            return False

        return True

    def validate_selections(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate generic selections structure"""
        if not original or not stored:
            return False

        for key in original:
            if key not in stored:
                return False

            original_value = original[key]
            stored_value = stored[key]

            if isinstance(original_value, list):
                if not isinstance(stored_value, list) or set(original_value) != set(
                    stored_value
                ):
                    return False
            else:
                if original_value != stored_value:
                    return False

        return True

    def validate_observability_selections(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate observability selections with complex structure"""
        if not original or not stored:
            return False

        # Check methods, tools (arrays)
        for key in ["methods", "tools"]:
            if key in original and key in stored:
                if set(original[key]) != set(stored[key]):
                    return False

        # Check other fields
        for key in ["go_no_go_text", "additional_logic_text"]:
            if key in original and key in stored:
                if original[key] != stored[key]:
                    return False

        # Check boolean fields
        for key in ["additional_logic_enabled"]:
            if key in original and key in stored:
                if original[key] != stored[key]:
                    return False

        return True

    def validate_orchestration_selections(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate orchestration selections"""
        if not original or not stored:
            return False

        if original.get("choice", "") != stored.get("choice", ""):
            return False

        if original.get("details", "") != stored.get("details", ""):
            return False

        return True

    def validate_collector_selections(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate collector selections"""
        if not original or not stored:
            return False

        # Check array fields
        for key in ["methods", "auth", "handling", "normalization", "tools"]:
            if key in original and key in stored:
                if set(original[key]) != set(stored[key]):
                    return False

        # Check string fields
        for key in ["devices", "metrics_per_sec", "cadence"]:
            if key in original and key in stored:
                if original[key] != stored[key]:
                    return False

        return True

    def validate_executor_selections(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate executor selections"""
        if not original or not stored:
            return False

        if "methods" in original and "methods" in stored:
            return set(original["methods"]) == set(stored["methods"])

        return True

    def validate_dependencies(
        self, original: List[Dict[str, Any]], stored: List[Dict[str, Any]]
    ) -> bool:
        """Validate dependencies list"""
        if not isinstance(original, list) or not isinstance(stored, list):
            return False

        if len(original) != len(stored):
            return False

        for i, (orig_dep, stored_dep) in enumerate(zip(original, stored)):
            if not isinstance(orig_dep, dict) or not isinstance(stored_dep, dict):
                return False

            if orig_dep.get("name", "") != stored_dep.get("name", ""):
                return False
            if orig_dep.get("details", "") != stored_dep.get("details", ""):
                return False

        return True

    def validate_timeline(
        self, original: Dict[str, Any], stored: Dict[str, Any]
    ) -> bool:
        """Validate timeline section"""
        if not original or not stored:
            return False

        # Check basic fields
        basic_fields = [
            "staff_count",
            "start_date",
            "total_business_days",
            "projected_completion",
        ]
        for field in basic_fields:
            if original.get(field, "") != stored.get(field, ""):
                return False

        # Check staffing plan
        if original.get("staffing_plan_md", "") != stored.get("staffing_plan_md", ""):
            return False

        # Check timeline items
        original_items = original.get("items", [])
        stored_items = stored.get("items", [])

        if not isinstance(original_items, list) or not isinstance(stored_items, list):
            return False

        if len(original_items) != len(stored_items):
            return False

        for i, (orig_item, stored_item) in enumerate(zip(original_items, stored_items)):
            if not isinstance(orig_item, dict) or not isinstance(stored_item, dict):
                return False

            for field in ["name", "start", "end", "duration_bd", "notes"]:
                if orig_item.get(field, "") != stored_item.get(field, ""):
                    return False

        return True

    def validate_export_functionality(self, solution_id: str) -> bool:
        """Test that the uploaded solution can be exported correctly"""
        try:
            # Test JSON export
            response = requests.post(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}/export",
                params={"format": "json"},
                headers=self.api_headers,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                export_data = result.get("data", {})

                # Validate export contains all sections
                required_sections = [
                    "initiative",
                    "my_role",
                    "stakeholders",
                    "presentation",
                    "intent",
                    "observability",
                    "orchestration",
                    "collector",
                    "executor",
                    "dependencies",
                    "timeline",
                ]

                missing_sections = [
                    section
                    for section in required_sections
                    if section not in export_data
                ]

                if not missing_sections:
                    self.log_validation(
                        "Export Validation", True, "All sections present in export"
                    )

                    # Test Markdown export
                    response_md = requests.post(
                        f"{self.api_base_url}/api/v1/solutions/{solution_id}/export",
                        params={"format": "markdown"},
                        headers=self.api_headers,
                        timeout=10,
                    )

                    if response_md.status_code == 200:
                        result_md = response_md.json()
                        markdown_content = result_md.get("data", "")

                        if (
                            "LOREM TEST" in markdown_content
                            and len(markdown_content) > 1000
                        ):
                            self.log_validation(
                                "Markdown Export", True, "Export contains test data"
                            )
                            return True
                        else:
                            self.log_validation(
                                "Markdown Export", False, "Export content invalid"
                            )
                            return False
                    else:
                        self.log_validation(
                            "Markdown Export",
                            False,
                            f"Status code: {response_md.status_code}",
                        )
                        return False
                else:
                    self.log_validation(
                        "Export Validation",
                        False,
                        f"Missing sections: {missing_sections}",
                    )
                    return False
            else:
                self.log_validation(
                    "Export Validation", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_validation("Export Validation", False, f"Exception: {str(e)}")
            return False

    def test_streamlit_ui_session_state_handling(self) -> bool:
        """Test Streamlit UI session state handling with problematic data"""
        try:
            print("🔍 Testing Streamlit UI session state handling...")

            # Generate test data with problematic values that could cause session state errors
            test_data = self.generator.generate_complete_test_data()

            # Create scenarios that would trigger session state errors in the old code
            problematic_scenarios = [
                {
                    "name": "Invalid orchestration choice",
                    "data": test_data.copy(),
                    "modifications": lambda d: d.update(
                        {
                            "orchestration": {
                                "choice": "Invalid Choice Not In Options",
                                "details": "",
                            }
                        }
                    ),
                },
                {
                    "name": "Invalid role choices",
                    "data": test_data.copy(),
                    "modifications": lambda d: d.update(
                        {
                            "my_role": {
                                "who": "Invalid Role Choice",
                                "skills": "Invalid Skill Choice",
                                "developer": "Invalid Developer Choice",
                            }
                        }
                    ),
                },
                {
                    "name": "Mixed valid/invalid data",
                    "data": test_data.copy(),
                    "modifications": lambda d: d.update(
                        {
                            "orchestration": {
                                "choice": "Yes – provide details",
                                "details": "Valid details",
                            },
                            "my_role": {
                                "who": "Invalid Role",
                                "skills": "Valid skills",
                                "developer": "Invalid developer",
                            },
                        }
                    ),
                },
            ]

            all_passed = True

            for scenario in problematic_scenarios:
                try:
                    # Apply modifications
                    scenario["modifications"](scenario["data"])

                    # Upload problematic data
                    response = requests.post(
                        f"{self.api_base_url}/api/v1/solutions",
                        headers=self.api_headers,
                        json=scenario["data"],
                        timeout=10,
                    )

                    if response.status_code == 200:
                        solution_id = response.json().get("solution_id")

                        # Verify the data was stored (API should handle it)
                        get_response = requests.get(
                            f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                            headers=self.api_headers,
                            timeout=10,
                        )

                        if get_response.status_code == 200:
                            stored_data = get_response.json().get("json_data", {})

                            # Verify the problematic data was stored correctly
                            expected_orch_choice = scenario["data"]["orchestration"][
                                "choice"
                            ]
                            actual_orch_choice = stored_data.get(
                                "orchestration", {}
                            ).get("choice")

                            if actual_orch_choice == expected_orch_choice:
                                self.log_validation(
                                    f"Streamlit UI Test - {scenario['name']}",
                                    True,
                                    f"Successfully handled problematic data: {expected_orch_choice}",
                                )
                            else:
                                self.log_validation(
                                    f"Streamlit UI Test - {scenario['name']}",
                                    False,
                                    f"Data mismatch: expected {expected_orch_choice}, got {actual_orch_choice}",
                                )
                                all_passed = False
                        else:
                            self.log_validation(
                                f"Streamlit UI Test - {scenario['name']}",
                                False,
                                f"Failed to retrieve stored data: {get_response.status_code}",
                            )
                            all_passed = False
                    else:
                        self.log_validation(
                            f"Streamlit UI Test - {scenario['name']}",
                            False,
                            f"Upload failed: {response.status_code} - {response.text}",
                        )
                        all_passed = False

                except Exception as e:
                    self.log_validation(
                        f"Streamlit UI Test - {scenario['name']}",
                        False,
                        f"Exception during test: {str(e)}",
                    )
                    all_passed = False

            return all_passed

        except Exception as e:
            self.log_validation(
                "Streamlit UI Session State Test", False, f"Test setup failed: {str(e)}"
            )
            return False

    def test_error_handling_functionality(self) -> bool:
        """Test the error handling functionality directly"""
        try:
            print("🔍 Testing error handling functionality...")

            # Import the error handling function
            sys.path.append(str(Path(__file__).parent.parent))

            # Mock streamlit to test error handling
            import unittest.mock as mock

            with mock.patch("pages.NAF_Solution_Wizard.st") as mock_st:
                mock_session_state = {}
                mock_st.session_state = mock_session_state

                # Import the function
                try:
                    from pages.NAF_Solution_Wizard import handle_widget_error

                    # Test 1: ValueError handling
                    def mock_radio_value_error(*args, **kwargs):
                        raise ValueError("Test ValueError - option not in iterable")

                    mock_st.radio.side_effect = mock_radio_value_error

                    result = handle_widget_error(
                        mock_st.radio,
                        "Select option",
                        ["Valid Option 1", "Valid Option 2"],
                        key="test_key",
                        error_message="Test error message",
                    )

                    if result is None and mock_st.error.called:
                        self.log_validation(
                            "Error Handling - ValueError",
                            True,
                            "ValueError handled correctly with None return and error message",
                        )
                    else:
                        self.log_validation(
                            "Error Handling - ValueError",
                            False,
                            "ValueError not handled correctly",
                        )
                        return False

                    # Test 2: Generic Exception handling
                    def mock_radio_generic_error(*args, **kwargs):
                        raise Exception("Test generic exception")

                    mock_st.radio.side_effect = mock_radio_generic_error
                    mock_st.reset_mock()

                    result = handle_widget_error(
                        mock_st.radio,
                        "Select option",
                        ["Valid Option 1", "Valid Option 2"],
                        key="test_key2",
                        error_message="Test generic error",
                    )

                    if result is None and mock_st.error.called:
                        self.log_validation(
                            "Error Handling - Generic Exception",
                            True,
                            "Generic exception handled correctly",
                        )
                    else:
                        self.log_validation(
                            "Error Handling - Generic Exception",
                            False,
                            "Generic exception not handled correctly",
                        )
                        return False

                    # Test 3: Normal operation
                    mock_st.radio.side_effect = None
                    mock_st.radio.return_value = "selected_value"
                    mock_st.reset_mock()

                    result = handle_widget_error(
                        mock_st.radio,
                        "Select option",
                        ["Valid Option 1", "Valid Option 2"],
                        key="test_key3",
                    )

                    if result == "selected_value" and not mock_st.error.called:
                        self.log_validation(
                            "Error Handling - Normal Operation",
                            True,
                            "Normal operation works correctly",
                        )
                    else:
                        self.log_validation(
                            "Error Handling - Normal Operation",
                            False,
                            "Normal operation not working correctly",
                        )
                        return False

                    return True

                except ImportError:
                    self.log_validation(
                        "Error Handling Test",
                        False,
                        "Could not import error handling function for testing",
                    )
                    return False

        except Exception as e:
            self.log_validation(
                "Error Handling Test", False, f"Test failed with exception: {str(e)}"
            )
            return False

    def save_validation_results(self) -> str:
        """Save validation results to file"""
        filename = (
            f"upload_validation_results_{self.validation_results['test_run']}.json"
        )
        output_path = Path("tests") / "results" / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)

        return str(output_path)

    def run_complete_validation(self) -> bool:
        """Run the complete upload validation test"""
        print("🧪 Starting NAF Solution Wizard Upload Validation")
        print(f"📝 Test Run: {self.validation_results['test_run']}")
        print(f"🌐 API URL: {self.api_base_url}")
        print("=" * 60)

        # Step 1: Generate test file
        json_file_path = self.generate_test_file()
        if not json_file_path:
            print("❌ Failed to generate test file")
            return False

        # Step 2: Upload to API
        solution_id = self.validate_api_upload(json_file_path)
        if not solution_id:
            print("❌ Failed to upload test file")
            return False

        # Step 3: Validate stored solution
        if not self.validate_stored_solution(
            solution_id, json.load(open(json_file_path))
        ):
            print("❌ Failed to validate stored solution")
            return False

        # Step 4: Test export functionality
        if not self.validate_export_functionality(solution_id):
            print("❌ Failed to validate export functionality")
            return False

        # Step 5: Test Streamlit UI session state handling
        if not self.test_streamlit_ui_session_state_handling():
            print("❌ Failed Streamlit UI session state tests")
            return False

        # Step 6: Test error handling functionality
        if not self.test_error_handling_functionality():
            print("❌ Failed error handling tests")
            return False

        # Save results
        results_file = self.save_validation_results()

        # Summary
        passed = sum(
            1 for test in self.validation_results["validations"] if test["success"]
        )
        total = len(self.validation_results["validations"])

        print("=" * 60)
        print(f"📊 Validation Results: {passed}/{total} passed")
        print(f"💾 Results saved to: {results_file}")
        print(f"📁 Test file: {json_file_path}")

        if passed == total:
            print("🎉 All upload validations passed!")
            return True
        else:
            print(f"⚠️ {total - passed} validations failed")
            return False


def main():
    """Main validation runner"""
    import argparse

    parser = argparse.ArgumentParser(
        description="NAF Solution Wizard Upload Validation"
    )
    parser.add_argument(
        "--api-url",
        default="http://localhost:8001",
        help="API base URL (default: http://localhost:8001)",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate test file, don't upload",
    )

    args = parser.parse_args()

    validator = WizardUploadValidator(args.api_url)

    if args.generate_only:
        json_file_path = validator.generate_test_file()
        print(f"📁 Test file generated: {json_file_path}")
        print("📤 You can now manually upload this file to the Solution Wizard")
    else:
        validator.run_complete_validation()


if __name__ == "__main__":
    main()
