#!/usr/bin/env python3
"""
Test complete wizard_data.py functionality.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import wizard_data
sys.path.insert(0, str(Path(__file__).parent.parent))
from wizard_data import build_wizard_payload, restore_session_state_from_data, get_title_only_session_state

def test_complete_payload():
    """Test that all sections are included in the payload."""
    
    # Create a sample session state with values from all sections
    session_state = {
        # Initiative section
        "_wizard_automation_title": "Test Automation Project",
        "_wizard_automation_description": "A test project for automation",
        "_wizard_category": "Network Monitoring",
        "_wizard_problem_statement": "Need to monitor network devices",
        "_wizard_expected_use": "Daily monitoring of network health",
        "_wizard_error_conditions": "Device unreachable",
        "_wizard_assumptions": "Devices are accessible",
        "_wizard_deployment_strategy": "Centralized",
        "_wizard_deployment_strategy_description": "Deployed at central location",
        "_wizard_out_of_scope": "Wireless networks",
        "no_move_forward": "None",
        "no_move_forward_reasons": ["Technical complexity"],
        
        # My Role section
        "my_role_who": "I'm a network engineer.",
        "my_role_skills": "I have some scripting skills",
        "my_role_dev": "I'll do it myself.",
        
        # Stakeholders section
        "stakeholders_choices": {"Network Operations": "Primary", "Security Team": "Secondary"},
        "stakeholders_other_text": "Custom stakeholder",
        
        # Presentation section
        "pres_user_Network Engineers": True,
        "pres_user_Security Analysts": True,
        "pres_interact_Web Dashboard": True,
        "pres_interact_API": True,
        "pres_tool_Grafana": True,
        "pres_auth_SSO": True,
        
        # Intent section
        "intent_dev_Python Scripts": True,
        "intent_dev_Ansible Playbooks": True,
        "intent_prov_SNMP": True,
        "intent_prov_REST APIs": True,
        
        # Observability section
        "obs_state_Prometheus": True,
        "obs_state_InfluxDB": True,
        "obs_tool_Grafana": True,
        "obs_go_no_go": "Device must be reachable",
        "obs_add_logic_choice": "Yes",
        "obs_add_logic_text": "Check device status before alerting",
        
        # Orchestration section
        "orch_choice": "Ansible",
        "orch_details_text": "Using Ansible for configuration management",
        
        # Collector section
        "collector_method_SNMP": True,
        "collector_method_NETCONF": True,
        "collector_auth_SSH Keys": True,
        "collector_handle_Retry Logic": True,
        "collector_norm_YANG Models": True,
        "collection_tool_NAPALM": True,
        "collector_devices": "Cisco, Juniper switches",
        "collector_metrics": "Interface stats, CPU, memory",
        "collector_cadence": "5 minutes",
        
        # Executor section
        "exec_0": True,  # Ansible
        "exec_1": True,  # NETCONF
        
        # Dependencies section
        "dep_network_infra": True,
        "dep_revision_control": True,
        "dep_revision_control_details": "GitHub",
        "dep_monitoring_system": True,
        "dep_monitoring_system_details": "Prometheus",
        
        # Timeline section
        "timeline_build_buy": "Build In-House",
        "timeline_staff_count": 2,
        "timeline_external_staff_count": 0,
        "timeline_staffing_plan": "2 network engineers will work on this project",
        "timeline_holiday_region": "US",
        "timeline_start_date": "2024-01-01",
        "timeline_milestones": [
            {"name": "Planning", "duration_bd": 5, "notes": "Initial planning phase"},
            {"name": "Development", "duration_bd": 10, "notes": "Develop the solution"},
        ],
    }
    
    # Build the payload
    payload = build_wizard_payload(session_state)
    
    # Verify all sections are present
    expected_sections = [
        "initiative", "my_role", "stakeholders", "presentation",
        "intent", "observability", "orchestration", "collector",
        "executor", "dependencies", "timeline"
    ]
    
    for section in expected_sections:
        assert section in payload, f"Missing section: {section}"
        print(f"✓ Section '{section}' is present")
    
    # Verify some specific values
    assert payload["initiative"]["title"] == "Test Automation Project"
    assert payload["presentation"]["users"] == "This solution targets Network Engineers and Security Analysts."
    assert payload["orchestration"]["selections"]["choice"] == "Ansible"
    print(f"Dependencies found: {payload['dependencies']}")
    assert len(payload["dependencies"]) >= 3  # At least the default ones
    assert payload["timeline"]["staff_count"] == 2
    
    print("\n✓ All payload values are correct")
    
    # Test restoration
    print("\nTesting session state restoration...")
    restored = restore_session_state_from_data(payload)
    
    # Verify some restored values
    assert restored["_wizard_automation_title"] == "Test Automation Project"
    assert restored["pres_user_Network Engineers"] is True
    assert restored["orch_choice"] == "Ansible"
    assert restored["dep_network_infra"] is True
    assert restored["timeline_staff_count"] == 2
    
    print("✓ All values restored correctly")
    
    # Test round-trip
    print("\nTesting round-trip (payload -> restore -> payload)...")
    payload2 = build_wizard_payload(restored)
    
    # Compare key sections
    assert payload2["initiative"]["title"] == payload["initiative"]["title"]
    assert payload2["presentation"]["users"] == payload["presentation"]["users"]
    assert payload2["orchestration"]["selections"]["choice"] == payload["orchestration"]["selections"]["choice"]
    assert len(payload2["dependencies"]) == len(payload["dependencies"])
    
    print("✓ Round-trip test passed")
    
    print("\n🎉 All tests passed! The wizard_data.py file handles all sections correctly.")
    
    # Optional: Save sample payload for inspection
    from pathlib import Path
    sample_file = Path(__file__).parent / "exports" / "sample_complete_payload.json"
    with open(sample_file, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\nSample payload saved to '{sample_file}'")


if __name__ == "__main__":
    test_complete_payload()
