"""
Testable functions for the NAF Solution Wizard data handling.

This module extracts the core logic for:
1. Building the JSON payload from session state
2. Restoring session state from uploaded JSON data

These functions are pure (no Streamlit dependencies) and can be tested directly.

USAGE:
------
wizard_data.py serves multiple purposes:
- Testing: The pure functions can be unit tested without Streamlit dependencies
- Code Organization: Separates data transformation logic from UI code
- Reusability: Provides clean interfaces for data serialization/deserialization
- Maintainability: Centralizes payload building and session state restoration logic

FEATURES:
---------
The build_wizard_payload function now handles ALL wizard sections:
- Initiative: Title, description, category, problem statement, deployment strategy, etc.
- My Role: Who is filling out the wizard and their skills/role
- Stakeholders: Selected stakeholder categories and custom entries
- Presentation: Users, interaction modes, tools, and authentication
- Intent: Development approaches and provided formats
- Observability: State methods, tools, go/no-go criteria, and additional logic
- Orchestration: Choice and details for workflow automation
- Collector: Methods, authentication, handling, normalization, scale, and tools
- Executor: Methods for executing automation changes
- Dependencies: External systems and interfaces the solution relies on
- Timeline: Staffing, milestones, and schedule calculations

The restore_session_state_from_data function restores all session state keys
from uploaded JSON data, enabling complete wizard state recovery.

Helper functions:
- _collect_checkbox_values(): Extracts checked values for a given prefix
- _build_sentence_from_list(): Creates human-readable sentences from lists
- _get_custom_value(): Gets custom values when enable toggles are active
- Section-specific builders for each wizard section

WIZARD FIELD MAPPINGS
=====================

The following fields are used in the NAF Solution Wizard:

INITIATIVE SECTION:
-------------------
_wizard_automation_title (str): Title of the automation initiative
_wizard_automation_description (str): Short description/scope of the initiative
_wizard_category (str): Category selected from predefined list or "Other"
_wizard_category_other (str): Custom category when "Other" is selected
_wizard_problem_statement (str): Problem statement description
_wizard_expected_use (str): Expected use cases (Markdown supported)
_wizard_error_conditions (str): Error conditions description
_wizard_assumptions (str): Assumptions for the automation
_wizard_deployment_strategy (str): Selected deployment strategy
_wizard_deployment_strategy_other (str): Custom deployment strategy
_wizard_deployment_strategy_description (str): Description of deployment strategy
_wizard_out_of_scope (str): Out of scope items (optional)
no_move_forward (str): Additional risks in not moving forward
no_move_forward_reasons (list[str]): Standard reasons for not moving forward

MY ROLE SECTION:
----------------
my_role_who (str): Who's filling out the wizard (radio selection)
my_role_who_other (str): Custom description when "Other" is selected
my_role_skills (str): Technical skills description (radio selection)
my_role_skills_other (str): Custom skills description when "Other" is selected
my_role_dev (str): Who will develop the automation (radio selection)
my_role_dev_other (str): Custom developer description when "Other" is selected

STAKEHOLDERS SECTION:
---------------------
stakeholders_choices (dict): Selected stakeholder categories and their values
stakeholders_other_text (str): Custom stakeholder description
stakeholders_other_enable (bool): Toggle for custom stakeholder input

PRESENTATION SECTION:
---------------------
pres_user_{option} (bool): Checkboxes for intended users
pres_user_custom_enable (bool): Toggle for custom users
pres_user_custom (str): Custom user description
pres_interact_{option} (bool): Checkboxes for interaction methods
pres_interact_custom_enable (bool): Toggle for custom interaction
pres_interact_custom (str): Custom interaction description
pres_tool_{option} (bool): Checkboxes for presentation tools
pres_tool_custom_enable (bool): Toggle for custom tools
pres_tool_custom (str): Custom tool description
pres_auth_{option} (bool): Checkboxes for authentication methods
pres_auth_other_enable (bool): Toggle for other authentication
pres_auth_other_text (str): Other authentication details

INTENT SECTION:
---------------
intent_dev_{option} (bool): Checkboxes for development approaches
intent_dev_custom_enable (bool): Toggle for custom development intent
intent_dev_custom (str): Custom development intent
intent_prov_{option} (bool): Checkboxes for provision approaches
intent_prov_custom_enable (bool): Toggle for custom provision
intent_prov_custom (str): Custom provision description

OBSERVABILITY SECTION:
----------------------
obs_state_{option} (bool): Checkboxes for state representation methods
obs_tool_{option} (bool): Checkboxes for observability tools
obs_tool_other_enable (bool): Toggle for other tools
obs_tool_other_text (str): Other tool details
obs_go_no_go (str): Go/No-Go criteria
obs_add_logic_choice (str): Additional gating logic choice (radio)
obs_add_logic_text (str): Additional gating logic description

ORCHESTRATION SECTION:
----------------------
orch_choice (str): Orchestration platform choice (radio)
orch_details_text (str): Orchestration details description

COLLECTOR SECTION:
------------------
collector_method_{option} (bool): Checkboxes for collection methods
collector_methods_other_enable (bool): Toggle for custom methods
collector_methods_other (str): Custom method description
collector_auth_{option} (bool): Checkboxes for authentication
collector_auth_other_enable (bool): Toggle for other authentication
collector_auth_other (str): Other authentication details
collector_handle_{option} (bool): Checkboxes for data handling
collector_handling_other_enable (bool): Toggle for custom handling
collector_handling_other (str): Custom handling description
collector_norm_{option} (bool): Checkboxes for normalization
collector_norm_other_enable (bool): Toggle for custom normalization
collector_norm_other (str): Custom normalization description
collection_tool_{option} (bool): Checkboxes for collection tools
collection_tools_other_enable (bool): Toggle for custom tools
collection_tools_other (str): Custom tool description
collector_devices (str): Devices/scope text area
collector_metrics (str): Metrics/data text area
collector_cadence (str): Cadence text input

EXECUTOR SECTION:
-----------------
exec_{index} (bool): Checkboxes for execution methods
exec_custom_enable (bool): Toggle for custom execution methods
exec_custom_text (str): Custom execution methods

DEPENDENCIES SECTION:
---------------------
dep_{key} (bool): Checkboxes for dependencies
dep_{key}_details (str): Details for each dependency

TIMELINE SECTION:
-----------------
timeline_build_buy (str): Build or buy choice (radio)
timeline_staff_count (int): Direct staff count
timeline_external_staff_count (int): Professional services staff count
timeline_staffing_plan (str): Staffing plan (Markdown)
timeline_holiday_region (str): Holiday calendar region
timeline_start_date (date): Project start date
timeline_milestones (list[dict]): List of milestone dictionaries
_tl_name_{N} (str): Milestone name for row N
_tl_duration_{N} (int): Milestone duration in business days for row N
_tl_notes_{N} (str): Milestone notes for row N

LEGACY KEYS (for backward compatibility):
----------------------------------------
_wizard_data (dict): Legacy storage for scalar field values
_wizard_checkboxes (dict): Legacy storage for checkbox states
_json_loaded (bool): Flag indicating JSON was loaded
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import datetime


def _collect_checkbox_values(session_state: Dict[str, Any], prefix: str) -> List[str]:
    """
    Collect all checked values for a given checkbox prefix.
    
    Args:
        session_state: Streamlit session state dictionary
        prefix: Prefix of checkbox keys (e.g., 'pres_user_')
        
    Returns:
        List of checked values
    """
    return [key.replace(prefix, "") for key, value in session_state.items() 
            if key.startswith(prefix) and value is True]


def _build_sentence_from_list(items: List[str], prefix: str = "", suffix: str = "") -> str:
    """
    Build a human-readable sentence from a list of items.
    
    Args:
        items: List of items to join
        prefix: Text to prepend
        suffix: Text to append
        
    Returns:
        Formatted sentence or empty string if no items
    """
    if not items:
        return ""
    
    if len(items) == 1:
        return f"{prefix}{items[0]}{suffix}"
    elif len(items) == 2:
        return f"{prefix}{items[0]} and {items[1]}{suffix}"
    else:
        return f"{prefix}{', '.join(items[:-1])}, and {items[-1]}{suffix}"


def _get_custom_value(session_state: Dict[str, Any], key: str, enable_key: str) -> str:
    """
    Get custom value if its enable toggle is active.
    
    Args:
        session_state: Streamlit session state dictionary
        key: Key for the custom value
        enable_key: Key for the enable toggle
        
    Returns:
        Custom value or empty string
    """
    return session_state.get(key, "") if session_state.get(enable_key, False) else ""


def build_wizard_payload(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a comprehensive wizard payload from session state.
    
    Args:
        session_state: Streamlit session state dictionary
        
    Returns:
        Complete payload dictionary with all wizard data
    """
    # Get the actual deployment strategy value
    deployment_strategy = session_state.get("_wizard_deployment_strategy", "")
    if deployment_strategy == "Other":
        deployment_strategy = session_state.get("_wizard_deployment_strategy_other", "")
    
    # Get the actual category value
    category = session_state.get("_wizard_category", "")
    category_other = session_state.get("_wizard_category_other", "")
    
    payload = {
        "initiative": {
            "author": session_state.get("_wizard_author", ""),
            "title": session_state.get("_wizard_automation_title", ""),
            "description": session_state.get("_wizard_automation_description", ""),
            "category": category,
            "category_other": category_other,
            "problem_statement": session_state.get("_wizard_problem_statement", ""),
            "expected_use": session_state.get("_wizard_expected_use", ""),
            "error_conditions": session_state.get("_wizard_error_conditions", ""),
            "assumptions": session_state.get("_wizard_assumptions", ""),
            "deployment_strategy": deployment_strategy,
            "deployment_strategy_other": session_state.get("_wizard_deployment_strategy_other", ""),
            "deployment_strategy_description": session_state.get("_wizard_deployment_strategy_description", ""),
            "out_of_scope": session_state.get("_wizard_out_of_scope", ""),
            "no_move_forward": session_state.get("no_move_forward", ""),
            "no_move_forward_reasons": session_state.get("no_move_forward_reasons", []),
        },
        "my_role": {
            "who": session_state.get("my_role_who", ""),
            "skills": session_state.get("my_role_skills", ""),
            "developer": session_state.get("my_role_dev", ""),
        },
        "stakeholders": {
            "choices": session_state.get("stakeholders_choices", {}),
            "other": (session_state.get("stakeholders_other_text") or "").strip(),
        },
        "presentation": _build_presentation_data(session_state),
        "intent": _build_intent_data(session_state),
        "observability": _build_observability_data(session_state),
        "orchestration": _build_orchestration_data(session_state),
        "collector": _build_collector_data(session_state),
        "executor": _build_executor_data(session_state),
        "dependencies": _build_dependencies_data(session_state),
        "timeline": _build_timeline_data(session_state),
    }
    
    return payload


def _build_presentation_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build presentation section data from session state."""
    selected_users = _collect_checkbox_values(session_state, "pres_user_")
    selected_interactions = _collect_checkbox_values(session_state, "pres_interact_")
    selected_tools = _collect_checkbox_values(session_state, "pres_tool_")
    selected_auth_pres = _collect_checkbox_values(session_state, "pres_auth_")
    
    # Add custom values if enabled
    custom_users = _get_custom_value(session_state, "pres_user_custom", "pres_user_custom_enable")
    custom_interact = _get_custom_value(session_state, "pres_interact_custom", "pres_interact_custom_enable")
    custom_tool = _get_custom_value(session_state, "pres_tool_custom", "pres_tool_custom_enable")
    custom_auth = _get_custom_value(session_state, "pres_auth_other_text", "pres_auth_other_enable")
    
    if custom_users:
        selected_users.append(custom_users)
    if custom_interact:
        selected_interactions.append(custom_interact)
    if custom_tool:
        selected_tools.append(custom_tool)
    if custom_auth:
        selected_auth_pres.append(custom_auth)
    
    users_sentence = _build_sentence_from_list(selected_users, "This solution targets ", ".")
    interaction_sentence = _build_sentence_from_list(selected_interactions, "Users will interact with the solution via ", ".")
    tools_sentence = _build_sentence_from_list(selected_tools, "The presentation layer will be built using ", ".")
    auth_sentence = _build_sentence_from_list(selected_auth_pres, "Presentation authentication will use ", ".")
    
    return {
        "users": users_sentence,
        "interaction": interaction_sentence,
        "tools": tools_sentence,
        "auth": auth_sentence,
        "selections": {
            "users": selected_users,
            "interactions": selected_interactions,
            "tools": selected_tools,
            "auth": selected_auth_pres,
        },
    }


def _build_intent_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build intent section data from session state."""
    selected_intent_devs = _collect_checkbox_values(session_state, "intent_dev_")
    selected_intent_prov = _collect_checkbox_values(session_state, "intent_prov_")
    
    # Add custom values if enabled
    custom_dev = _get_custom_value(session_state, "intent_dev_custom", "intent_dev_custom_enable")
    custom_prov = _get_custom_value(session_state, "intent_prov_custom", "intent_prov_custom_enable")
    
    if custom_dev:
        selected_intent_devs.extend([v.strip() for v in custom_dev.split(",")])
    if custom_prov:
        selected_intent_prov.extend([v.strip() for v in custom_prov.split(",")])
    
    dev_sentence = _build_sentence_from_list(selected_intent_devs, "We will develop ", ".")
    prov_sentence = _build_sentence_from_list(selected_intent_prov, "We will use existing ", ".")
    
    return {
        "development": dev_sentence,
        "provided": prov_sentence,
        "selections": {
            "development": selected_intent_devs,
            "provided": selected_intent_prov,
        },
    }


def _build_observability_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build observability section data from session state."""
    selected_methods = _collect_checkbox_values(session_state, "obs_state_")
    selected_tools_obs = _collect_checkbox_values(session_state, "obs_tool_")
    
    # Add custom tools if enabled
    custom_tools = _get_custom_value(session_state, "obs_tool_other_text", "obs_tool_other_enable")
    if custom_tools:
        selected_tools_obs.append(custom_tools)
    
    methods_sentence = _build_sentence_from_list(selected_methods, "State will be represented using ", ".")
    tools_sentence = _build_sentence_from_list(selected_tools_obs, "Observability tools include ", ".")
    
    go_no_go_text = session_state.get("obs_go_no_go", "")
    add_logic_choice = session_state.get("obs_add_logic_choice", "")
    add_logic_text = session_state.get("obs_add_logic_text", "")
    
    add_logic_sentence = ""
    if add_logic_choice == "Yes" and add_logic_text:
        add_logic_sentence = f"Additional gating logic: {add_logic_text}"
    
    return {
        "methods": methods_sentence,
        "go_no_go": go_no_go_text,
        "additional_logic": add_logic_sentence,
        "tools": tools_sentence,
        "selections": {
            "methods": selected_methods,
            "go_no_go_text": go_no_go_text,
            "additional_logic_enabled": add_logic_choice == "Yes",
            "additional_logic_text": add_logic_text,
            "tools": selected_tools_obs,
        },
    }


def _build_orchestration_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build orchestration section data from session state."""
    orch_choice = session_state.get("orch_choice", "— Select one —")
    orch_details = session_state.get("orch_details_text", "")
    
    orch_sentence = ""
    if orch_choice and orch_choice != "— Select one —":
        if orch_choice == "No":
            orch_sentence = "No orchestration is required for this solution."
        elif orch_details:
            orch_sentence = f"Orchestration will be handled using {orch_choice}: {orch_details}"
        else:
            orch_sentence = f"Orchestration will be handled using {orch_choice}."
    
    return {
        "summary": orch_sentence,
        "selections": {
            "choice": orch_choice,
            "details": orch_details,
        },
    }


def _build_collector_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build collector section data from session state."""
    selected_methods = _collect_checkbox_values(session_state, "collector_method_")
    selected_auth = _collect_checkbox_values(session_state, "collector_auth_")
    selected_handling = _collect_checkbox_values(session_state, "collector_handle_")
    selected_norm = _collect_checkbox_values(session_state, "collector_norm_")
    selected_tools = _collect_checkbox_values(session_state, "collection_tool_")
    
    # Add custom values if enabled
    custom_method = _get_custom_value(session_state, "collector_methods_other", "collector_methods_other_enable")
    custom_auth = _get_custom_value(session_state, "collector_auth_other", "collector_auth_other_enable")
    custom_handling = _get_custom_value(session_state, "collector_handling_other", "collector_handling_other_enable")
    custom_norm = _get_custom_value(session_state, "collector_norm_other", "collector_norm_other_enable")
    custom_tools = _get_custom_value(session_state, "collection_tools_other", "collection_tools_other_enable")
    
    if custom_method:
        selected_methods.append(custom_method)
    if custom_auth:
        selected_auth.append(custom_auth)
    if custom_handling:
        selected_handling.append(custom_handling)
    if custom_norm:
        selected_norm.append(custom_norm)
    if custom_tools:
        selected_tools.append(custom_tools)
    
    methods_sentence = _build_sentence_from_list(selected_methods, "Data will be collected using ", ".")
    auth_sentence = _build_sentence_from_list(selected_auth, "Collection authentication will use ", ".")
    handling_sentence = _build_sentence_from_list(selected_handling, "Data will be handled using ", ".")
    norm_sentence = _build_sentence_from_list(selected_norm, "Data will be normalized using ", ".")
    
    scale_sentence = ""
    devices = session_state.get("collector_devices", "")
    metrics = session_state.get("collector_metrics", "")
    cadence = session_state.get("collector_cadence", "")
    
    if devices or metrics or cadence:
        scale_parts = []
        if devices:
            scale_parts.append(f"devices/scope: {devices}")
        if metrics:
            scale_parts.append(f"metrics: {metrics}")
        if cadence:
            scale_parts.append(f"cadence: {cadence}")
        scale_sentence = "Scale considerations: " + "; ".join(scale_parts) + "."
    
    tools_sentence = _build_sentence_from_list(selected_tools, "Collection tools include ", ".")
    
    return {
        "methods": methods_sentence,
        "auth": auth_sentence,
        "handling": handling_sentence,
        "normalization": norm_sentence,
        "scale": scale_sentence,
        "tools": tools_sentence,
        "selections": {
            "methods": selected_methods,
            "auth": selected_auth,
            "handling": selected_handling,
            "normalization": selected_norm,
            "devices": devices,
            "metrics_per_sec": metrics,
            "cadence": cadence,
            "tools": selected_tools,
        },
    }


def _build_executor_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build executor section data from session state."""
    selected_exec = _collect_checkbox_values(session_state, "exec_")
    
    # Add custom methods if enabled
    custom_exec = _get_custom_value(session_state, "exec_custom_text", "exec_custom_enable")
    if custom_exec:
        selected_exec.extend([v.strip() for v in custom_exec.split(",")])
    
    exec_sentence = _build_sentence_from_list(selected_exec, "Changes will be executed using ", ".")
    
    return {
        "methods": exec_sentence,
        "selections": {
            "methods": selected_exec,
        },
    }


def _build_dependencies_data(session_state: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build dependencies list from session state."""
    dependencies = []
    
    # Check all dependency keys
    for key, value in session_state.items():
        if key.startswith("dep_") and not key.endswith("_details") and value:
            dep_key = key.replace("dep_", "")
            details = session_state.get(f"dep_{dep_key}_details", "")
            dependencies.append({"name": dep_key, "details": details})
    
    # Ensure default dependencies if none selected
    if not dependencies:
        dependencies = [
            {"name": "Network Infrastructure", "details": ""},
            {"name": "Revision Control system", "details": "GitHub"},
        ]
    
    return dependencies


def _build_timeline_data(session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Build timeline data from session state."""
    start_date = session_state.get("timeline_start_date")
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    elif not isinstance(start_date, datetime.date):
        start_date = datetime.datetime.today().date()
    
    build_buy = session_state.get("timeline_build_buy", "Build In-House")
    staff_count = int(session_state.get("timeline_staff_count", 0))
    external_staff_count = int(session_state.get("timeline_external_staff_count", 0))
    staffing_plan = session_state.get("timeline_staffing_plan", "")
    holiday_region = session_state.get("timeline_holiday_region", "None")
    
    milestones = session_state.get("timeline_milestones", [])
    
    # Calculate schedule
    schedule = []
    total_bd = 0
    cursor = start_date
    
    for milestone in milestones:
        duration = milestone.get("duration_bd", 0)
        total_bd += duration
        
        start = cursor
        # Add business days (simplified - weekends only)
        days_added = 0
        while days_added < duration:
            cursor += datetime.timedelta(days=1)
            if cursor.weekday() < 5:  # Monday-Friday
                days_added += 1
        
        end = cursor - datetime.timedelta(days=1)
        
        schedule.append({
            "name": milestone.get("name", ""),
            "duration_bd": duration,
            "start": start,
            "end": end,
            "notes": milestone.get("notes", ""),
        })
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "total_business_days": total_bd,
        "projected_completion": schedule[-1]["end"].strftime("%Y-%m-%d") if schedule else None,
        "build_buy": build_buy,
        "staff_count": staff_count,
        "external_staff_count": external_staff_count,
        "staffing_plan_md": staffing_plan,
        "holiday_region": holiday_region,
        "items": [
            {
                "name": i["name"],
                "duration_bd": i["duration_bd"],
                "start": i["start"].strftime("%Y-%m-%d"),
                "end": i["end"].strftime("%Y-%m-%d"),
                "notes": i["notes"],
            }
            for i in schedule
        ],
    }


def restore_session_state_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract session state updates from uploaded JSON data.
    
    Args:
        data: Dictionary containing the uploaded JSON data
        
    Returns:
        Dictionary of session state updates
    """
    updates = {}
    
    # Extract initiative data
    ini = data.get("initiative", {})
    if ini.get("author") is not None:
        updates["_wizard_author"] = str(ini.get("author") or "")
    elif "author" in ini:
        # Handle case where author exists but is None
        updates["_wizard_author"] = ""
    if ini.get("title") is not None:
        updates["_wizard_automation_title"] = str(ini.get("title") or "")
    if ini.get("description") is not None:
        updates["_wizard_automation_description"] = str(ini.get("description") or "")
    if ini.get("problem_statement") is not None:
        updates["_wizard_problem_statement"] = str(ini.get("problem_statement") or "")
    if ini.get("expected_use") is not None:
        updates["_wizard_expected_use"] = str(ini.get("expected_use") or "")
    if ini.get("error_conditions") is not None:
        updates["_wizard_error_conditions"] = str(ini.get("error_conditions") or "")
    if ini.get("assumptions") is not None:
        updates["_wizard_assumptions"] = str(ini.get("assumptions") or "")
    if ini.get("deployment_strategy") is not None:
        deploy_strategy = str(ini.get("deployment_strategy") or "")
        # Check if the deployment strategy is in the predefined list
        deploy_yaml_path = Path(__file__).parent / "deployment_strategies.yml"
        try:
            with open(deploy_yaml_path, "r") as f:
                deploy_data = yaml.safe_load(f)
            deploy_options = list(deploy_data.keys()) if deploy_data else []
        except Exception:
            deploy_options = []
        
        if deploy_strategy in deploy_options:
            # It's a standard strategy
            updates["_wizard_deployment_strategy"] = deploy_strategy
            updates["_wizard_deployment_strategy_other"] = ""
        elif deploy_strategy and deploy_strategy != "— Select a deployment strategy —":
            # It's a custom strategy, put it in "Other"
            updates["_wizard_deployment_strategy"] = "Other"
            updates["_wizard_deployment_strategy_other"] = deploy_strategy
        else:
            # Empty or placeholder
            updates["_wizard_deployment_strategy"] = "— Select a deployment strategy —"
            updates["_wizard_deployment_strategy_other"] = ""
    if ini.get("deployment_strategy_description") is not None:
        updates["_wizard_deployment_strategy_description"] = str(ini.get("deployment_strategy_description") or "")
    if ini.get("out_of_scope") is not None:
        updates["_wizard_out_of_scope"] = str(ini.get("out_of_scope") or "")
    if ini.get("no_move_forward") is not None:
        updates["no_move_forward"] = str(ini.get("no_move_forward") or "")
    if ini.get("no_move_forward_reasons") is not None:
        updates["no_move_forward_reasons"] = ini.get("no_move_forward_reasons", []) or []
        updates["no_move_forward_reasons"] = updates["no_move_forward_reasons"] if isinstance(updates["no_move_forward_reasons"], list) else []
    
    # Restore category
    if ini.get("category") is not None:
        category_value = ini.get("category")
        try:
            yaml_path = Path(__file__).parent / "use_case_categories.yml"
            with open(yaml_path, "r") as f:
                categories_data = yaml.safe_load(f)
            category_options = list(categories_data.keys()) if categories_data else []
        except Exception:
            category_options = []
        
        if category_value in category_options:
            updates["_wizard_category"] = category_value
            updates["_wizard_category_other"] = ""
        else:
            updates["_wizard_category"] = "Other"
            updates["_wizard_category_other"] = category_value
    
    # Restore stakeholders
    stakeholders = data.get("stakeholders", {})
    if stakeholders is not None and isinstance(stakeholders, dict):
        if stakeholders.get("choices") is not None and isinstance(stakeholders.get("choices"), dict):
            # Use choices as-is since we no longer support old category names
            updates["stakeholders_choices"] = stakeholders.get("choices")
        else:
            updates["stakeholders_choices"] = {}
        if stakeholders.get("other") is not None:
            updates["stakeholders_other_text"] = str(stakeholders.get("other") or "")
        else:
            updates["stakeholders_other_text"] = ""
    else:
        # Handle None or non-dict stakeholders
        updates["stakeholders_choices"] = {}
        updates["stakeholders_other_text"] = ""
    
    # Restore my role
    my_role = data.get("my_role", {}) or {}
    if my_role.get("who") is not None:
        updates["my_role_who"] = str(my_role.get("who") or "")
    if my_role.get("skills") is not None:
        updates["my_role_skills"] = str(my_role.get("skills") or "")
    if my_role.get("developer") is not None:
        updates["my_role_dev"] = str(my_role.get("developer") or "")
    
    # Restore presentation
    pres = data.get("presentation", {}) or {}
    pres_sel = pres.get("selections", {}) or {}
    if pres_sel.get("users") and isinstance(pres_sel.get("users"), list):
        for user in pres_sel.get("users"):
            updates[f"pres_user_{user}"] = True
    if pres_sel.get("interactions") and isinstance(pres_sel.get("interactions"), list):
        for interact in pres_sel.get("interactions"):
            updates[f"pres_interact_{interact}"] = True
    if pres_sel.get("tools") and isinstance(pres_sel.get("tools"), list):
        for tool in pres_sel.get("tools"):
            updates[f"pres_tool_{tool}"] = True
    if pres_sel.get("auth") and isinstance(pres_sel.get("auth"), list):
        for auth in pres_sel.get("auth"):
            updates[f"pres_auth_{auth}"] = True
    
    # Restore intent
    intent = data.get("intent", {}) or {}
    intent_sel = intent.get("selections", {}) or {}
    if intent_sel.get("development") and isinstance(intent_sel.get("development"), list):
        for dev in intent_sel.get("development"):
            updates[f"intent_dev_{dev}"] = True
    if intent_sel.get("provided") and isinstance(intent_sel.get("provided"), list):
        for prov in intent_sel.get("provided"):
            updates[f"intent_prov_{prov}"] = True
    
    # Restore observability
    obs = data.get("observability", {}) or {}
    obs_sel = obs.get("selections", {}) or {}
    if obs_sel.get("methods") and isinstance(obs_sel.get("methods"), list):
        for method in obs_sel.get("methods"):
            updates[f"obs_state_{method}"] = True
    if obs_sel.get("tools") and isinstance(obs_sel.get("tools"), list):
        for tool in obs_sel.get("tools"):
            updates[f"obs_tool_{tool}"] = True
    if obs.get("go_no_go") is not None:
        updates["obs_go_no_go"] = str(obs.get("go_no_go") or "")
    if obs_sel.get("additional_logic_choice") is not None:
        updates["obs_add_logic_choice"] = str(obs_sel.get("additional_logic_choice") or "")
    if obs_sel.get("additional_logic_text") is not None:
        updates["obs_add_logic_text"] = str(obs_sel.get("additional_logic_text") or "")
    
    # Restore orchestration
    orch = data.get("orchestration", {}) or {}
    orch_sel = orch.get("selections", {}) or {}
    if orch_sel.get("choice") is not None:
        updates["orch_choice"] = str(orch_sel.get("choice") or "")
    if orch_sel.get("details") is not None:
        updates["orch_details_text"] = str(orch_sel.get("details") or "")
    
    # Restore collector
    coll = data.get("collector", {}) or {}
    coll_sel = coll.get("selections", {}) or {}
    if coll_sel.get("methods") and isinstance(coll_sel.get("methods"), list):
        for method in coll_sel.get("methods"):
            updates[f"collector_method_{method}"] = True
    if coll_sel.get("auth") and isinstance(coll_sel.get("auth"), list):
        for auth in coll_sel.get("auth"):
            updates[f"collector_auth_{auth}"] = True
    if coll_sel.get("handling") and isinstance(coll_sel.get("handling"), list):
        for handling in coll_sel.get("handling"):
            updates[f"collector_handle_{handling}"] = True
    if coll_sel.get("normalization") and isinstance(coll_sel.get("normalization"), list):
        for norm in coll_sel.get("normalization"):
            updates[f"collector_norm_{norm}"] = True
    if coll_sel.get("tools") and isinstance(coll_sel.get("tools"), list):
        for tool in coll_sel.get("tools"):
            updates[f"collection_tool_{tool}"] = True
    if coll_sel.get("devices") is not None:
        updates["collector_devices"] = str(coll_sel.get("devices") or "")
    if coll_sel.get("metrics_per_sec") is not None:
        updates["collector_metrics"] = str(coll_sel.get("metrics_per_sec") or "")
    if coll_sel.get("cadence") is not None:
        updates["collector_cadence"] = str(coll_sel.get("cadence") or "")
    
    # Restore executor
    exec_data = data.get("executor", {}) or {}
    exec_sel = exec_data.get("selections", {}) or {}
    if exec_sel.get("methods") and isinstance(exec_sel.get("methods"), list):
        for i, method in enumerate(exec_sel.get("methods")):
            updates[f"exec_{i}"] = True
    
    # Restore dependencies
    deps = data.get("dependencies", []) or []
    for dep in deps:
        if dep.get("name"):
            updates[f"dep_{dep['name']}"] = True
            if dep.get("details"):
                updates[f"dep_{dep['name']}_details"] = str(dep.get("details") or "")
    
    # Restore timeline
    tl = data.get("timeline", {}) or {}
    if tl.get("build_buy") is not None:
        updates["timeline_build_buy"] = str(tl.get("build_buy") or "")
    if tl.get("staff_count") is not None:
        updates["timeline_staff_count"] = int(tl.get("staff_count") or 0)
    if tl.get("external_staff_count") is not None:
        updates["timeline_external_staff_count"] = int(tl.get("external_staff_count") or 0)
    if tl.get("staffing_plan_md") is not None:
        updates["timeline_staffing_plan"] = str(tl.get("staffing_plan_md") or "")
    if tl.get("holiday_region") is not None:
        updates["timeline_holiday_region"] = str(tl.get("holiday_region") or "")
    if tl.get("start_date") is not None:
        try:
            from datetime import datetime
            updates["timeline_start_date"] = datetime.strptime(tl.get("start_date"), "%Y-%m-%d").date()
        except Exception:
            pass
    if tl.get("items") and isinstance(tl.get("items"), list):
        milestones = []
        for item in tl.get("items"):
            milestones.append({
                "name": str(item.get("name", "")),
                "duration_bd": int(item.get("duration_bd", 0)),
                "notes": str(item.get("notes", "")),
            })
        updates["timeline_milestones"] = milestones
    
    return updates


def get_title_only_session_state(title: str) -> Dict[str, Any]:
    """
    Create a minimal session state with only the title field set.
    Used for testing the title field round-trip.
    
    Args:
        title: The title to set
        
    Returns:
        Minimal session state dictionary
    """
    return {
        "_wizard_automation_title": title,
        "_wizard_automation_description": "Here is a short description of my my new network automation project",
        "_wizard_category": "— Select a category —",
        "_wizard_category_other": "",
        "_wizard_problem_statement": "",
        "_wizard_expected_use": "This automation will be used whenever this task needs to be executed.",
        "_wizard_error_conditions": "",
        "_wizard_assumptions": "",
        "_wizard_deployment_strategy": "",
        "_wizard_deployment_strategy_description": "",
        "_wizard_out_of_scope": "",
        "no_move_forward": "",
        "no_move_forward_reasons": ["— Select one or more risks —"],
        "stakeholders_choices": {},
        "stakeholders_other_text": "",
        "my_role_who": "I'm a network engineer.",
        "my_role_skills": "I have some scripting skills and basic software development experience.",
        "my_role_dev": "I'll do it myself.",
        "my_role_who_other": "",
        "my_role_skills_other": "",
        "my_role_dev_other": "",
    }
