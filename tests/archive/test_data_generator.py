"""
Test Data Generator for NAF Solution Wizard
Generates lorem ipsum test data for all wizard fields
"""

from lorem_text import lorem
import random
import json
from typing import Dict, Any, List
from pathlib import Path


class LoremTestDataGenerator:
    """Generates lorem ipsum test data for Solution Wizard fields"""

    def __init__(self):
        self.title = "LOREM TEST"

        # Standard pulldown options that should be preserved
        self.standard_options = {
            "deployment_strategies": [
                "Phased Rollout",
                "Big Bang",
                "Pilot Program",
                "Canary Release",
                "Blue-Green Deployment",
                "Feature Flag",
                "Other",
            ],
            "categories": [
                "Network Automation",
                "Security Automation",
                "Cloud Automation",
                "Infrastructure as Code",
                "Monitoring & Observability",
                "Compliance & Governance",
                "Other",
            ],
            "users": [
                "Network Engineers",
                "System Administrators",
                "Security Analysts",
                "Developers",
            ],
            "interactions": ["Web Dashboard", "CLI Tools", "API Access", "Mobile App"],
            "tools": ["Streamlit", "FastAPI", "React", "Vue.js"],
            "auth": ["LDAP/Active Directory", "OAuth2", "SAML", "API Keys"],
            "development_formats": ["YAML", "JSON", "XML", "TOML"],
            "provided_formats": ["REST API", "GraphQL", "gRPC", "Message Queue"],
            "methods": ["Syslog", "SNMP Traps", "API Callbacks", "File Monitoring"],
            "tools_observability": ["ELK Stack", "Grafana", "Prometheus", "Datadog"],
            "collection_methods": ["SSH", "NETCONF", "REST APIs", "SNMP"],
            "auth_mechanisms": [
                "SSH Keys",
                "API Tokens",
                "Certificates",
                "Username/Password",
            ],
            "traffic_handling": [
                "Concurrent Execution",
                "Sequential Processing",
                "Batch Processing",
            ],
            "normalization": [
                "JSON Schema",
                "XML Schema",
                "Custom Parser",
                "No Normalization",
            ],
            "execution_methods": ["SSH", "NETCONF", "RESTCONF", "Custom Protocol"],
        }

    def get_lorem_sentence(self) -> str:
        """Generate a single lorem sentence"""
        return lorem.sentence()

    def get_lorem_paragraph(self, sentences: int = 3) -> str:
        """Generate a lorem paragraph with specified number of sentences"""
        return " ".join(lorem.sentence() for _ in range(sentences))

    def get_lorem_words(self, words: int = 5) -> str:
        """Generate lorem text with specified number of words"""
        return lorem.words(words)

    def get_random_choice(self, options: List[str]) -> str:
        """Get random choice from standard options"""
        return random.choice(options)

    def get_random_choices(self, options: List[str], count: int = 2) -> List[str]:
        """Get random choices from standard options"""
        return random.sample(options, min(count, len(options)))

    def generate_initiative_data(self) -> Dict[str, Any]:
        """Generate initiative section data"""
        return {
            "title": self.title,
            "description": self.get_lorem_paragraph(5),
            "category": self.get_random_choice(self.standard_options["categories"]),
            "problem_statement": self.get_lorem_paragraph(3),
            "out_of_scope": self.get_lorem_paragraph(2),
            "expected_use": self.get_lorem_paragraph(3),
            "error_conditions": self.get_lorem_paragraph(2),
            "assumptions": self.get_lorem_paragraph(2),
            "deployment_strategy": self.get_random_choice(
                self.standard_options["deployment_strategies"]
            ),
            "deployment_strategy_description": self.get_lorem_paragraph(3),
            "no_move_forward_reasons": [self.get_lorem_sentence() for _ in range(2)],
            "no_move_forward": self.get_lorem_paragraph(2),
        }

    def generate_my_role_data(self) -> Dict[str, Any]:
        """Generate my role section data"""
        return {
            "who": f"Lorem {self.get_lorem_words(2)} Engineer",
            "skills": self.get_lorem_paragraph(2),
            "developer": self.get_random_choice(
                ["In-house team", "External vendor", "Hybrid approach"]
            ),
        }

    def generate_stakeholders_data(self) -> Dict[str, Any]:
        """Generate stakeholders section data"""
        stakeholder_categories = {
            "Technical Stakeholders": self.get_random_choice(
                ["Network Engineering Team", "DevOps Team", "Security Team"]
            ),
            "Business Stakeholders": self.get_random_choice(
                ["IT Director", "Operations Manager", "Product Owner"]
            ),
            "User Stakeholders": self.get_random_choice(
                ["End Users", "Support Team", "Customers"]
            ),
        }

        return {
            "choices": stakeholder_categories,
            "other": f"Lorem {self.get_lorem_words(3)} stakeholders",
        }

    def generate_presentation_data(self) -> Dict[str, Any]:
        """Generate presentation section data"""
        return {
            "users": self.get_lorem_paragraph(2),
            "interaction": self.get_lorem_paragraph(2),
            "tools": self.get_lorem_paragraph(2),
            "auth": self.get_lorem_paragraph(2),
            "selections": {
                "users": self.get_random_choices(self.standard_options["users"], 3),
                "interactions": self.get_random_choices(
                    self.standard_options["interactions"], 2
                ),
                "tools": self.get_random_choices(self.standard_options["tools"], 2),
                "auth": self.get_random_choices(self.standard_options["auth"], 2),
            },
        }

    def generate_intent_data(self) -> Dict[str, Any]:
        """Generate intent section data"""
        return {
            "development": self.get_lorem_paragraph(2),
            "provided": self.get_lorem_paragraph(2),
            "selections": {
                "development": self.get_random_choices(
                    self.standard_options["development_formats"], 2
                ),
                "provided": self.get_random_choices(
                    self.standard_options["provided_formats"], 2
                ),
            },
        }

    def generate_observability_data(self) -> Dict[str, Any]:
        """Generate observability section data"""
        return {
            "methods": self.get_lorem_paragraph(2),
            "go_no_go": self.get_lorem_paragraph(2),
            "additional_logic": self.get_lorem_paragraph(2),
            "tools": self.get_lorem_paragraph(2),
            "selections": {
                "methods": self.get_random_choices(self.standard_options["methods"], 3),
                "go_no_go_text": self.get_lorem_sentence(),
                "additional_logic_enabled": random.choice([True, False]),
                "additional_logic_text": (
                    self.get_lorem_sentence() if random.choice([True, False]) else ""
                ),
                "tools": self.get_random_choices(
                    self.standard_options["tools_observability"], 2
                ),
            },
        }

    def generate_orchestration_data(self) -> Dict[str, Any]:
        """Generate orchestration section data"""
        return {
            "summary": self.get_lorem_paragraph(3),
            "selections": {
                "choice": self.get_random_choice(
                    [
                        "— Select one —",
                        "No",
                        "Yes – internal via custom scripts and logic",
                        "Yes – provide details",
                    ]
                ),
                "details": (
                    self.get_lorem_paragraph(2) if random.choice([True, False]) else ""
                ),
            },
        }

    def generate_collector_data(self) -> Dict[str, Any]:
        """Generate collector section data"""
        return {
            "methods": self.get_lorem_paragraph(2),
            "auth": self.get_lorem_paragraph(2),
            "handling": self.get_lorem_paragraph(2),
            "scale": self.get_lorem_paragraph(2),
            "tools": self.get_lorem_paragraph(2),
            "selections": {
                "methods": self.get_random_choices(
                    self.standard_options["collection_methods"], 3
                ),
                "auth": self.get_random_choices(
                    self.standard_options["auth_mechanisms"], 2
                ),
                "handling": self.get_random_choices(
                    self.standard_options["traffic_handling"], 2
                ),
                "normalization": self.get_random_choices(
                    self.standard_options["normalization"], 2
                ),
                "devices": f"{random.randint(10, 1000)} {self.get_lorem_words(2)} devices",
                "metrics_per_sec": f"{random.randint(100, 10000)} metrics/sec",
                "cadence": f"Every {random.randint(1, 60)} {self.get_random_choice(['minutes', 'seconds', 'hours'])}",
                "tools": self.get_random_choices(self.standard_options["tools"], 2),
            },
        }

    def generate_executor_data(self) -> Dict[str, Any]:
        """Generate executor section data"""
        return {
            "methods": self.get_lorem_paragraph(2),
            "selections": {
                "methods": self.get_random_choices(
                    self.standard_options["execution_methods"], 2
                )
            },
        }

    def generate_dependencies_data(self) -> List[Dict[str, Any]]:
        """Generate dependencies section data"""
        dependencies = []
        for i in range(random.randint(2, 5)):
            dependencies.append(
                {
                    "name": f"Lorem {self.get_lorem_words(2)} {i+1}",
                    "details": (
                        self.get_lorem_paragraph(1)
                        if random.choice([True, False])
                        else ""
                    ),
                }
            )
        return dependencies

    def generate_timeline_data(self) -> Dict[str, Any]:
        """Generate timeline section data"""
        items: list[Dict[str, Any]] = []
        start_date = "2024-01-15"

        timeline_items: list[tuple[str, int, str]] = [
            ("Requirements gathering", 5, "Lorem ipsum requirements"),
            ("Design and architecture", 7, "Lorem ipsum design"),
            ("Development phase", 14, "Lorem ipsum development"),
            ("Testing and validation", 5, "Lorem ipsum testing"),
            ("Deployment and rollout", 3, "Lorem ipsum deployment"),
        ]

        current_date = start_date
        for name, duration, notes in timeline_items:
            items.append(
                {
                    "name": name,
                    "start": current_date,
                    "end": f"2024-01-{15 + duration + len(items) * 5:02d}",
                    "duration_bd": duration,
                    "notes": notes,
                }
            )

        return {
            "staff_count": random.randint(2, 8),
            "start_date": start_date,
            "total_business_days": sum(item["duration_bd"] for item in items),
            "projected_completion": items[-1]["end"],
            "items": items,
            "staffing_plan_md": self.get_lorem_paragraph(4),
        }

    def generate_complete_test_data(self) -> Dict[str, Any]:
        """Generate complete test data for the entire solution wizard"""
        return {
            "initiative": self.generate_initiative_data(),
            "my_role": self.generate_my_role_data(),
            "stakeholders": self.generate_stakeholders_data(),
            "presentation": self.generate_presentation_data(),
            "intent": self.generate_intent_data(),
            "observability": self.generate_observability_data(),
            "orchestration": self.generate_orchestration_data(),
            "collector": self.generate_collector_data(),
            "executor": self.generate_executor_data(),
            "dependencies": self.generate_dependencies_data(),
            "timeline": self.generate_timeline_data(),
        }

    def get_wizard_filename(self) -> str:
        """Generate filename using wizard naming convention"""
        from datetime import datetime
        import re

        # Sanitize title for filename (same as wizard does)
        title_for_zip = (
            self.title.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace("*", "_")
            .replace("?", "_")
            .replace('"', "_")
            .replace("<", "_")
            .replace(">", "_")
            .replace("|", "_")
        )
        # Remove multiple underscores and trailing underscores
        title_for_zip = re.sub(r"_+", "_", title_for_zip).strip("_")

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        return f"naf_report_{title_for_zip}_{timestamp}.json"

    def save_test_data(self, data: Dict[str, Any], filename: str | None = None) -> str:
        """Save test data to JSON file using wizard naming convention"""
        if filename is None:
            filename = self.get_wizard_filename()

        output_path = Path("tests") / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return str(output_path)


if __name__ == "__main__":
    # Generate and save test data
    generator = LoremTestDataGenerator()
    test_data = generator.generate_complete_test_data()

    # Save to file
    output_file = generator.save_test_data(test_data)
    print(f"✅ Test data saved to: {output_file}")
    print(f"📝 Generated test data for: {generator.title}")
    print(f"📊 Total sections: {len(test_data)}")
