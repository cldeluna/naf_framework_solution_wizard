#!/usr/bin/env python3
"""
Main Test Script for NAF Solution Wizard
Generates lorem test data and tests the API endpoints
"""

import sys
import json
import requests
from typing import Any as TypingAny
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from tests.test_data_generator import LoremTestDataGenerator


class SolutionWizardTester:
    """Test framework for NAF Solution Wizard API"""

    def __init__(self, api_base_url: str = "http://localhost:8001"):
        self.api_base_url = api_base_url
        self.generator = LoremTestDataGenerator()
        self.test_token = "test-token-lorem"
        self.headers = {
            "Authorization": f"Bearer {self.test_token}",
            "Content-Type": "application/json",
        }
        self.results = {
            "test_run": f"LOREM_TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "api_url": api_base_url,
            "tests": [],
        }

    def log_test(
        self, test_name: str, success: bool, message: str = "", data: TypingAny = None
    ):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }
        if data is not None:
            result["data"] = data
        self.results["tests"].append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def test_api_health(self) -> bool:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_test(
                    "API Health Check", True, f"Status: {response.json()['status']}"
                )
                return True
            else:
                self.log_test(
                    "API Health Check", False, f"Status code: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test("API Health Check", False, f"Exception: {str(e)}")
            return False

    def test_create_solution(self) -> str:
        """Test creating a solution with lorem data"""
        try:
            # Generate test data
            test_data = self.generator.generate_complete_test_data()

            # Create solution via API
            response = requests.post(
                f"{self.api_base_url}/api/v1/solutions",
                json=test_data,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                solution_id = result.get("solution_id")

                self.log_test(
                    "Create Solution",
                    True,
                    f"Solution ID: {solution_id}",
                    {"title": test_data["initiative"]["title"]},
                )

                # Save the generated test data
                self.save_test_data(test_data, solution_id)

                return solution_id
            else:
                self.log_test(
                    "Create Solution",
                    False,
                    f"Status code: {response.status_code}, Response: {response.text}",
                )
                return None

        except Exception as e:
            self.log_test("Create Solution", False, f"Exception: {str(e)}")
            return None

    def test_get_solution(self, solution_id: str) -> bool:
        """Test retrieving a solution"""
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                title = (
                    result.get("json_data", {})
                    .get("initiative", {})
                    .get("title", "Unknown")
                )

                self.log_test(
                    "Get Solution",
                    True,
                    f"Retrieved: {title}",
                    {"solution_id": solution_id},
                )
                return True
            else:
                self.log_test(
                    "Get Solution", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("Get Solution", False, f"Exception: {str(e)}")
            return False

    def test_update_solution(self, solution_id: str) -> bool:
        """Test updating a solution"""
        try:
            # Generate updated test data
            updated_data = self.generator.generate_complete_test_data()
            updated_data["initiative"]["title"] = f"{self.generator.title} - UPDATED"

            response = requests.put(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                json=updated_data,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                self.log_test(
                    "Update Solution", True, f"Updated solution: {solution_id}"
                )
                return True
            else:
                self.log_test(
                    "Update Solution", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("Update Solution", False, f"Exception: {str(e)}")
            return False

    def test_export_solution(self, solution_id: str) -> bool:
        """Test exporting a solution"""
        try:
            # Test JSON export
            response = requests.post(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}/export",
                params={"format": "json"},
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                self.save_export_data(result, solution_id, "json")

                self.log_test("Export Solution (JSON)", True, "Exported as JSON")

                # Test Markdown export
                response_md = requests.post(
                    f"{self.api_base_url}/api/v1/solutions/{solution_id}/export",
                    params={"format": "markdown"},
                    headers=self.headers,
                    timeout=10,
                )

                if response_md.status_code == 200:
                    result_md = response_md.json()
                    self.save_export_data(result_md, solution_id, "markdown")

                    self.log_test(
                        "Export Solution (Markdown)", True, "Exported as Markdown"
                    )
                    return True
                else:
                    self.log_test(
                        "Export Solution (Markdown)",
                        False,
                        f"Status code: {response_md.status_code}",
                    )
                    return False
            else:
                self.log_test(
                    "Export Solution (JSON)",
                    False,
                    f"Status code: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("Export Solution", False, f"Exception: {str(e)}")
            return False

    def test_list_solutions(self) -> bool:
        """Test listing all solutions"""
        try:
            response = requests.get(
                f"{self.api_base_url}/api/v1/solutions",
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                count = result.get("count", 0)

                self.log_test("List Solutions", True, f"Found {count} solutions")
                return True
            else:
                self.log_test(
                    "List Solutions", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("List Solutions", False, f"Exception: {str(e)}")
            return False

    def test_upload_validation(self) -> bool:
        """Test upload validation functionality"""
        try:
            from tests.upload_validator import WizardUploadValidator

            validator = WizardUploadValidator(self.api_base_url)

            # Generate test file
            json_file_path = validator.generate_test_file()
            if not json_file_path:
                self.log_test(
                    "Upload Validation - Generate",
                    False,
                    "Failed to generate test file",
                )
                return False

            # Upload and validate
            solution_id = validator.validate_api_upload(json_file_path)
            if not solution_id:
                self.log_test(
                    "Upload Validation - API", False, "Failed to upload or validate"
                )
                return False

            # Test export
            if not validator.validate_export_functionality(solution_id):
                self.log_test(
                    "Upload Validation - Export", False, "Export validation failed"
                )
                return False

            self.log_test("Upload Validation", True, "All upload validations passed")
            return True

        except Exception as e:
            self.log_test("Upload Validation", False, f"Exception: {str(e)}")
            return False

    def test_delete_solution(self, solution_id: str) -> bool:
        """Test deleting a solution"""
        try:
            response = requests.delete(
                f"{self.api_base_url}/api/v1/solutions/{solution_id}",
                headers=self.headers,
                timeout=10,
            )

            if response.status_code == 200:
                self.log_test(
                    "Delete Solution", True, f"Deleted solution: {solution_id}"
                )
                return True
            else:
                self.log_test(
                    "Delete Solution", False, f"Status code: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("Delete Solution", False, f"Exception: {str(e)}")
            return False

    def save_test_data(self, data: dict, solution_id: str):
        """Save generated test data using wizard naming convention"""
        filename = self.generator.get_wizard_filename()
        output_path = Path("tests") / "generated" / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Test data saved to: {output_path}")
        print("📁 This file can be manually uploaded to the Solution Wizard")

    def save_export_data(self, data: dict, solution_id: str, format_type: str):
        """Save exported data"""
        filename = f"lorem_export_{solution_id}.{format_type}"
        output_path = Path("tests") / "exports" / filename
        output_path.parent.mkdir(exist_ok=True)

        if format_type == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data["data"], f, indent=2, ensure_ascii=False)
        else:  # markdown
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(data["data"])

        print(f"💾 Export saved to: {output_path}")

    def save_test_results(self):
        """Save test results summary"""
        filename = f"test_results_{self.results['test_run']}.json"
        output_path = Path("tests") / "results" / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        return str(output_path)

    def run_full_test_suite(self) -> bool:
        """Run the complete test suite"""
        print("🚀 Starting NAF Solution Wizard Test Suite")
        print(f"📝 Test Run: {self.results['test_run']}")
        print(f"🌐 API URL: {self.api_base_url}")
        print("=" * 60)

        # Test API health first
        if not self.test_api_health():
            print("❌ API health check failed. Aborting tests.")
            return False

        # Run CRUD tests
        solution_id = self.test_create_solution()
        if not solution_id:
            print("❌ Failed to create solution. Aborting tests.")
            return False

        # Continue with other tests
        self.test_get_solution(solution_id)
        self.test_update_solution(solution_id)
        self.test_export_solution(solution_id)
        self.test_list_solutions()

        # Run upload validation test
        self.test_upload_validation()

        # Clean up
        self.test_delete_solution(solution_id)

        # Save results
        results_file = self.save_test_results()

        # Summary
        passed = sum(1 for test in self.results["tests"] if test["success"])
        total = len(self.results["tests"])

        print("=" * 60)
        print(f"📊 Test Results: {passed}/{total} passed")
        print(f"💾 Results saved to: {results_file}")

        if passed == total:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed.")
            return False


def main():
    """Main test runner"""
    import argparse

    parser = argparse.ArgumentParser(description="NAF Solution Wizard Test Framework")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8001",
        help="API base URL (default: http://localhost:8001)",
    )
    parser.add_argument(
        "--test",
        choices=["health", "create", "full"],
        default="full",
        help="Test to run (default: full)",
    )

    args = parser.parse_args()

    tester = SolutionWizardTester(args.api_url)

    if args.test == "health":
        tester.test_api_health()
    elif args.test == "create":
        tester.test_create_solution()
    else:
        tester.run_full_test_suite()


if __name__ == "__main__":
    main()
