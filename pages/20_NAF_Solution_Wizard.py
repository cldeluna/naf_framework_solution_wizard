#!/usr/bin/python3 -tt
# Project: naf_framework_solution_wizard
# Filename: naf_framework_solution_wizard.py
# claudiadeluna
# PyCharm

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "11/25/25"
__copyright__ = "Copyright (c) 2025 Claudia"
__license__ = "Python"

# Streamlit page: NAF Solution Wizard
#
# This page hosts the main Solution Wizard experience for the
# Network Automation Forum's Network Automation Framework (NAF).
#
# The implementation lives in NAF_NAF_Solution_Wizard.solution_wizard_main.


# from NAF_NAF_Solution_Wizard import solution_wizard_main


# When this file is run as a Streamlit page, simply delegate to the
# existing Solution Wizard implementation.
# solution_wizard_main()


from typing import List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import io
import re
import json
import yaml
import zipfile
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
import getpass
import os

import sys as _sys
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in _sys.path:
    _sys.path.insert(0, _project_root)

import utils
from puzzle_progress import (
    render_puzzle_progress, PUZZLE_SECTIONS, FRAME_SECTIONS,
    get_completion_state, get_frame_completion_state,
)

# Optional lightweight holiday support
try:
    import holidays as _hol
except Exception:  # pragma: no cover
    _hol = None


# --- Module-level constants ---
# Default values to avoid repetition
DEFAULT_TITLE = "My new network automation project"
DEFAULT_DESCRIPTION = "Here is a short description of my new network automation project"


# Utility functions moved to utils.py - local aliases for brevity
join_human = utils.join_human
md_line = utils.md_line
is_meaningful = utils.is_meaningful
_join = utils.join_human
from payload_builder import build_payload_from_state


# --- Module-level helper functions ---


def _sorted_deps(items):
    """Sort dependency items by name and details for comparison."""
    return sorted(items, key=lambda x: (x.get("name") or "", x.get("details") or ""))


def _render_template_preview(payload: dict, summary_md: str) -> str:
    """Render the Jinja template for preview, removing images."""
    try:
        templates_dir = (Path(__file__).parent.parent / "templates").resolve()
        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=False,
        )
        tmpl = env.get_template("Solution_Design_Report.j2")
        sdd_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        context = {
            "generated_timestamp": sdd_ts,
            "highlights": summary_md,
            "initiative": payload.get("initiative", {}),
            "my_role": payload.get("my_role", {}),
            "stakeholders": payload.get("stakeholders", {}),
            "presentation": payload.get("presentation", {}),
            "intent": payload.get("intent", {}),
            "observability": payload.get("observability", {}),
            "orchestration": payload.get("orchestration", {}),
            "collector": payload.get("collector", {}),
            "executor": payload.get("executor", {}),
            "dependencies": payload.get("dependencies", {}),
            "timeline": payload.get("timeline", {}),
        }
        
        rendered = tmpl.render(**context)
        
        # Remove image references from the rendered markdown
        import re
        # Remove markdown image syntax: ![alt text](url)
        rendered = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[\1]', rendered)
        # Remove HTML img tags
        rendered = re.sub(r'<img[^>]+src="[^"]+"[^>]*>', '', rendered)
        
        return rendered
    except Exception as e:
        # Fallback to simple summary if template rendering fails
        return f"Error rendering template: {e}\n\n---\n\n{summary_md}"


def _has_list_selections(d: dict) -> bool:
    """Check if a dict contains any non-empty list values."""
    return any(isinstance(v, list) and v for v in d.values())


def _norm_role_choice(choice, other, sentinel="— Select one —"):
    """Normalize a role radio choice, handling 'Other' and sentinel values."""
    if choice == "Other (fill in)":
        return (other or "").strip()
    if choice == sentinel:
        return ""
    return choice or ""


def _add_business_days(d, n, holiday_set=None):
    """Add n business days (Mon-Fri) to date d, optionally skipping holidays."""
    days = int(n or 0)
    cur = d
    while days > 0:
        cur = cur + datetime.timedelta(days=1)
        if cur.weekday() < 5 and (holiday_set is None or cur not in holiday_set):
            days -= 1
    return cur


def _section_md(title, lines):
    """Build a markdown section with title and bullet lines."""
    lines = [l for l in (lines or []) if (l or "").strip()]
    if not lines:
        return ""
    return f"## {title}\n" + "\n".join(lines) + "\n\n"


def _sanitize_title(t: str) -> str:
    """Sanitize a title string for use in filenames."""
    t = (t or "").strip()
    out = []
    for ch in t:
        if ch.isalnum() or ch in {"-", "_"}:
            out.append(ch)
        else:
            out.append("_")
    t = "".join(out)
    while "__" in t:
        t = t.replace("__", "_")
    t = t.strip("_")
    return (t or "solution")[0:30]


def _load_stakeholders_catalog() -> dict:
    p = Path(__file__).resolve().parents[1] / "stakeholders.json"
    try:
        raw = p.read_text(encoding="utf-8")
    except Exception:
        return {}

    for _ in range(2):
        try:
            data = json.loads(raw)
            return data if isinstance(data, dict) else {}
        except Exception:
            raw = (raw or "").strip()
            if raw.endswith("."):
                raw = raw[:-1]
                continue
            return {}


def _has_any_content(p: dict) -> bool:
    """Determine if payload has meaningful content beyond defaults."""
    try:
        pres_narr = p.get("presentation", {}) or {}
        intent_narr = p.get("intent", {}) or {}
        obs_narr = p.get("observability", {}) or {}
        orch_narr = p.get("orchestration", {}) or {}
        coll_narr = p.get("collector", {}) or {}
        exec_narr = p.get("executor", {}) or {}
        deps = p.get("dependencies", []) or []
        tl = p.get("timeline", {}) or {}
        ini = p.get("initiative", {}) or {}
        my_role = p.get("my_role", {}) or {}

        pres_flag = any(
            is_meaningful(pres_narr.get(k))
            for k in ("users", "interaction", "tools", "auth")
        )
        intent_flag = any(
            is_meaningful(intent_narr.get(k)) for k in ("development", "provided")
        )
        obs_flag = any(
            is_meaningful(obs_narr.get(k))
            for k in ("methods", "go_no_go", "additional_logic", "tools")
        )
        _orch_sel = (
            (orch_narr.get("selections") or {}) if isinstance(orch_narr, dict) else {}
        )
        _orch_choice = (_orch_sel.get("choice") or "").strip()
        orch_flag = bool(
            _orch_choice and _orch_choice != "— Select one —"
        ) or is_meaningful(orch_narr.get("summary"))
        coll_flag = any(
            is_meaningful(coll_narr.get(k))
            for k in ("methods", "auth", "handling", "normalization", "scale", "tools")
        )
        exec_flag = is_meaningful(exec_narr.get("methods"))

        deps_flag = False
        if deps:
            deps_slim = [
                {
                    "name": (d or {}).get("name"),
                    "details": (d or {}).get("details", "").strip(),
                }
                for d in deps
                if (d or {}).get("name")
            ]
            default_deps = [
                {"name": "Network Infrastructure", "details": ""},
                {"name": "Revision Control system", "details": "GitHub"},
            ]
            deps_flag = _sorted_deps(deps_slim) != _sorted_deps(default_deps)

        tl_flag = bool((tl.get("staffing_plan_md") or "").strip())

        default_title = DEFAULT_TITLE
        default_desc = DEFAULT_DESCRIPTION
        title = (ini.get("title") or "").strip()
        desc = (ini.get("description") or "").strip()
        ini_flag = bool(
            (title and title != default_title) or (desc and desc != default_desc)
        )
        role_flag = any(
            ((my_role.get(k) or "").strip()) for k in ("who", "skills", "developer")
        )

        return any(
            [
                pres_flag,
                intent_flag,
                obs_flag,
                orch_flag,
                coll_flag,
                exec_flag,
                deps_flag,
                tl_flag,
                ini_flag,
                role_flag,
            ]
        )
    except Exception:
        pass
    return False


# --- End module-level helper functions ---


def solution_wizard_main():
    """
    Solution Wizard (NAF Framework) interactive page

    A comprehensive tool for designing network automation solutions using the
    Network Automation Forum's Network Automation Framework (NAF).

    Includes guided inputs for:
    - Initiative: Title, description, category, problem statement, expected use,
      error conditions, assumptions, deployment strategy
    - Stakeholders: Who is supporting the project
    - My Role: Who is filling out the wizard and their skills
    - Presentation: User types, interaction modes, presentation tools, authentication
    - Intent: Development approaches, provided formats
    - Observability: Methods, go/no-go criteria, additional logic, tools
    - Orchestration: Choice and details for workflow automation
    - Collector: Methods, authentication, handling, normalization, scale, tools
    - Executor: Methods for executing automation

    Planning section:
    - "Staffing, Timeline, & Milestones" with:
      - Staffing fields (direct staff count and markdown-supported staffing plan)
      - Start date calendar
      - Editable milestone rows (name, duration in business days, notes)
      - Business-day scheduling that skips weekends and optionally public holidays (via python-holidays)
      - Optional Plotly Gantt chart visualization
      - Summary callouts for expected delivery date (st.success) and approximate duration in months/years (st.info)

    Dependencies section:
    - Add/remove network infrastructure dependencies
    - Default dependencies: Network Infrastructure, Revision Control system

    Export functionality:
    - Download complete solution design as ZIP with JSON and Markdown files
    - Upload previously saved JSON to restore wizard state
    - Solution Design Document template with all sections

    ==================================================================================
    STATE PERSISTENCE (LEGACY)
    ==================================================================================
    Previously used backing storage pattern for inter-page navigation.
    With single-page operation, widget state persists naturally.
    Legacy code marked for potential removal:
    - "_wizard_data": dict storing scalar field values
    - "_wizard_checkboxes": dict storing checkbox/toggle states

    ==================================================================================
    GUI FIELD TO VARIABLE MAPPING
    ==================================================================================
    Below is a mapping of GUI field labels to their session_state keys and types.

    MY ROLE SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key     | Type
    ---------------------------------------------------------------------------------
    Who's filling out this wizard?               | my_role_who              | str (radio, single)
    What best describes your technical skills?   | my_role_skills           | str (radio, single)
    Who will actually develop the automation?    | my_role_dev              | str (radio, single)

    INITIATIVE/PROJECT SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key             | Type
    ---------------------------------------------------------------------------------
    Automation initiative title                  | _wizard_automation_title         | str (text_input)
    Short description / scope                    | _wizard_automation_description   | str (text_area)
    Problem statement                            | _wizard_problem_statement        | str (text_area)
    Expected use (Markdown supported)            | _wizard_expected_use             | str (text_area)
    Out of scope (optional)                      | _wizard_out_of_scope             | str (text_area)
    Standard reasons                             | no_move_forward_reasons          | list[str] (multiselect, multi)
    Additional risks in not moving forward       | no_move_forward                  | str (text_area)

    PRESENTATION SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key Pattern     | Type
    ---------------------------------------------------------------------------------
    Intended users checkboxes                    | pres_user_{option}               | bool (checkbox, multi)
    Custom users enable                          | pres_user_custom_enable          | bool (checkbox)
    Custom users text                            | pres_user_custom                 | str (text_input)
    Interaction method checkboxes                | pres_interact_{option}           | bool (checkbox, multi)
    Custom interaction enable                    | pres_interact_custom_enable      | bool (checkbox)
    Tools checkboxes                             | pres_tool_{option}               | bool (checkbox, multi)
    Custom tool enable                           | pres_tool_custom_enable          | bool (checkbox)
    Authentication checkboxes                    | pres_auth_{option}               | bool (checkbox, multi)
    Other auth enable                            | pres_auth_other_enable           | bool (checkbox)
    Other auth details                           | pres_auth_other_text             | str (text_input)

    INTENT SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key Pattern     | Type
    ---------------------------------------------------------------------------------
    Intent development checkboxes                | intent_dev_{option}              | bool (checkbox, multi)
    Custom intent enable                         | intent_dev_custom_enable         | bool (checkbox)
    Intent provision checkboxes                  | intent_prov_{option}             | bool (checkbox, multi)
    Custom provision enable                      | intent_prov_custom_enable        | bool (checkbox)

    OBSERVABILITY SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key Pattern     | Type
    ---------------------------------------------------------------------------------
    State representation checkboxes              | obs_state_{option}               | bool (checkbox, multi)
    Observability tools checkboxes               | obs_tool_{option}                | bool (checkbox, multi)
    Other tool enable                            | obs_tool_other_enable            | bool (checkbox)
    Other tool text                              | obs_tool_other_text              | str (text_input)
    Go/No-Go criteria                            | obs_go_no_go                     | str (text_area)
    Additional gating logic choice               | obs_add_logic_choice             | str (radio, single)
    Additional gating logic text                 | obs_add_logic_text               | str (text_area)

    ORCHESTRATION SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key             | Type
    ---------------------------------------------------------------------------------
    Orchestration choice                         | orch_choice                      | str (radio, single)
    Orchestration details                        | orch_details_text                | str (text_area)

    COLLECTOR SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key Pattern     | Type
    ---------------------------------------------------------------------------------
    Collection method checkboxes                 | collector_method_{option}        | bool (checkbox, multi)
    Custom method enable                         | collector_methods_other_enable   | bool (checkbox)
    Authentication checkboxes                    | collector_auth_{option}          | bool (checkbox, multi)
    Custom auth enable                           | collector_auth_other_enable      | bool (checkbox)
    Data handling checkboxes                     | collector_handle_{option}        | bool (checkbox, multi)
    Custom handling enable                       | collector_handling_other_enable  | bool (checkbox)
    Normalization checkboxes                     | collector_norm_{option}          | bool (checkbox, multi)
    Custom normalization enable                  | collector_norm_other_enable      | bool (checkbox)
    Collection tools checkboxes                  | collection_tools_{option}        | bool (checkbox, multi)
    Custom tools enable                          | collection_tools_other_enable    | bool (checkbox)
    Devices/scope                                | collector_devices                | str (text_area)
    Metrics/data                                 | collector_metrics                | str (text_area)
    Cadence                                      | collector_cadence                | str (text_input)

    EXECUTOR SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key Pattern     | Type
    ---------------------------------------------------------------------------------
    Execution method checkboxes                  | exec_{index}                     | bool (checkbox, multi)

    DEPENDENCIES SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key Pattern     | Type
    ---------------------------------------------------------------------------------
    Dependency checkboxes                        | dep_{key}                        | bool (checkbox, multi)
    Dependency details                           | dep_{key}_details                | str (text_input)

    TIMELINE SECTION:
    ---------------------------------------------------------------------------------
    GUI Label                                    | st.session_state Key             | Type
    ---------------------------------------------------------------------------------
    Development approach                         | timeline_build_buy               | str (radio, single)
    Direct staff on project                      | timeline_staff_count             | int (number_input)
    Professional services staff                  | timeline_external_staff_count    | int (number_input)
    Staffing plan (markdown)                     | timeline_staffing_plan           | str (text_area)
    Holiday calendar                             | timeline_holiday_region          | str (selectbox, single)
    Project start date                           | timeline_start_date              | date (date_input)
    Milestone rows                               | timeline_milestones              | list[dict] (dynamic)
    Milestone name (row N)                       | _tl_name_{N}                     | str (text_input)
    Milestone duration (row N)                   | _tl_duration_{N}                 | int (number_input)
    Milestone notes (row N)                      | _tl_notes_{N}                    | str (text_input)

    SHARED KEYS:
    ---------------------------------------------------------------------------------
    Key                                          | Type                             | Description
    ---------------------------------------------------------------------------------
    """
    # Page config (use same favicon as landing page for consistency)
    st.set_page_config(
        page_title="Solution Wizard",
        page_icon="images/naf_favicon-96x96.png",
        layout="wide",
    )

    # Global sidebar branding (shared across pages)
    utils.render_global_sidebar()

    # Colors for main content separators
    hr_color_dict = utils.hr_colors()

    # JSON upload/reset controls now live in the main page body
    with st.expander("Load Saved Solution Wizard (JSON)", expanded=False):
        # Upload naf_report_*.json: allows Merge/Overwrite to rehydrate a previous session.
        # Filename must match naf_report_*.json; otherwise show guidance.

        uploaded = st.file_uploader(
            "Upload naf_report_*.json", type=["json"], key="wizard_upload_json"
        )
        if uploaded is not None:
            fname = (uploaded.name or "").strip()
            if not fname.lower().endswith(".json"):
                st.error(
                    "Invalid file. Please upload a .json file exported from this tool."
                )
            elif not fname.lower().startswith("naf_report_"):
                st.info(
                    "Tip: Expected a file named like 'naf_report_*.json' (use the Save Solution Artifacts download). Rename the file or download a fresh export."
                )
            else:
                if st.button(
                    "Apply uploaded JSON",
                    type="primary",
                    key="wizard_apply_upload_btn",
                ):
                    try:
                        data = json.load(uploaded)
                        if not isinstance(data, dict):
                            st.error(
                                "Uploaded JSON is not a valid Solution Wizard export (expected an object)."
                            )
                        else:
                            # Clear ALL existing wizard-related state before applying (Overwrite mode)
                            prefixes = (
                                "pres_",
                                "intent_",
                                "obs_",
                                "orch_",
                                "collector_",
                                "collection_tool_",
                                "collection_tools_",
                                "exec_",
                                "my_role_",
                                "dep_",
                                "_tl_",
                                "_timeline_",
                                "obs_tool_",
                                "obs_state_",
                                "collector_method_",
                                "collector_auth_",
                                "collector_handle_",
                                "collector_norm_",
                                "_wizard_",
                                "_widget_",
                                "stakeholders_",
                            )
                            for k in list(st.session_state.keys()):
                                if any([k.startswith(p) for p in prefixes]):
                                    st.session_state.pop(k, None)
                            # Force-uncheck known checkbox/toggle keys
                            for k in list(st.session_state.keys()):
                                if k.startswith(
                                    (
                                        "pres_user_",
                                        "pres_interact_",
                                        "pres_tool_",
                                        "pres_auth_",
                                        "intent_dev_",
                                        "intent_prov_",
                                        "obs_state_",
                                        "obs_tool_",
                                        "collector_method_",
                                        "collector_auth_",
                                        "collector_handle_",
                                        "collector_norm_",
                                        "collection_tool_",
                                        "collection_tools_",
                                    )
                                ):
                                    st.session_state[k] = False
                            for k in [
                                "pres_user_custom_enable",
                                "pres_interact_custom_enable",
                                "pres_tool_custom_enable",
                                "pres_auth_other_enable",
                                "intent_dev_custom_enable",
                                "intent_prov_custom_enable",
                                "obs_tool_other_enable",
                                "collector_methods_other_enable",
                                "collector_auth_other_enable",
                                "collector_handling_other_enable",
                                "collector_norm_other_enable",
                                "collection_tools_other_enable",
                                "stakeholders_other_enable",
                            ]:
                                st.session_state[k] = False
                            # Set Orchestration radio to sentinel
                            st.session_state["orch_choice"] = "— Select one —"
                            st.session_state["orch_details_text"] = ""
                            # Also set My Role radios to sentinel explicitly
                            st.session_state["my_role_who"] = "— Select one —"
                            st.session_state["my_role_skills"] = "— Select one —"
                            st.session_state["my_role_dev"] = "— Select one —"
                            st.session_state.pop("my_role_who_other", None)
                            st.session_state.pop("my_role_skills_other", None)
                            st.session_state.pop("my_role_dev_other", None)
                            for k in [
                                "automation_title",
                                "automation_description",
                                "expected_use",
                                "out_of_scope",
                                "no_move_forward",
                                "no_move_forward_reasons",
                                "timeline_milestones",
                                "timeline_build_buy",
                                "timeline_staff_count",
                                "timeline_external_staff_count",
                                "timeline_staffing_plan",
                                "timeline_holiday_region",
                                "timeline_start_date",
                                "collector_devices",
                                "collector_metrics",
                                "collector_cadence",
                                "orch_choice",
                                "orch_details_text",
                                "stakeholders_choices",
                                "stakeholders_other_text",
                            ]:
                                st.session_state.pop(k, None)

                            # Load Initiative data
                            ini = data.get("initiative", {}) or {}
                            if ini.get("author") is not None:
                                st.session_state["_wizard_author"] = str(
                                    ini.get("author") or ""
                                )
                            if ini.get("title") is not None:
                                st.session_state["_wizard_automation_title"] = str(
                                    ini.get("title") or ""
                                )
                            if ini.get("description") is not None:
                                st.session_state["_wizard_automation_description"] = (
                                    str(ini.get("description") or "")
                                )
                            if ini.get("problem_statement") is not None:
                                st.session_state["_wizard_problem_statement"] = str(
                                    ini.get("problem_statement") or ""
                                )
                            if ini.get("expected_use") is not None:
                                st.session_state["_wizard_expected_use"] = str(
                                    ini.get("expected_use") or ""
                                )
                            if ini.get("error_conditions") is not None:
                                st.session_state["_wizard_error_conditions"] = str(
                                    ini.get("error_conditions") or ""
                                )
                            if ini.get("assumptions") is not None:
                                st.session_state["_wizard_assumptions"] = str(
                                    ini.get("assumptions") or ""
                                )
                            if ini.get("deployment_strategy") is not None:
                                deploy_strategy = str(
                                    ini.get("deployment_strategy") or ""
                                )
                                # Check if the deployment strategy is in the predefined list
                                deploy_yaml_path = (
                                    Path(__file__).parent.parent
                                    / "deployment_strategies.yml"
                                )
                                try:
                                    with open(deploy_yaml_path, "r") as f:
                                        deploy_data = yaml.safe_load(f)
                                    deploy_options = (
                                        list(deploy_data.keys()) if deploy_data else []
                                    )
                                except Exception:
                                    deploy_options = []

                                if deploy_strategy in deploy_options:
                                    # It's a standard strategy
                                    st.session_state["_wizard_deployment_strategy"] = (
                                        deploy_strategy
                                    )
                                    st.session_state[
                                        "_wizard_deployment_strategy_other"
                                    ] = ""
                                elif (
                                    deploy_strategy
                                    and deploy_strategy
                                    != ""
                                ):
                                    # It's a custom strategy, put it in "Other"
                                    st.session_state["_wizard_deployment_strategy"] = (
                                        "Other"
                                    )
                                    st.session_state[
                                        "_wizard_deployment_strategy_other"
                                    ] = deploy_strategy
                                else:
                                    # Empty or placeholder
                                    st.session_state["_wizard_deployment_strategy"] = (
                                        ""
                                    )
                                    st.session_state[
                                        "_wizard_deployment_strategy_other"
                                    ] = ""
                            if ini.get("deployment_strategy_description") is not None:
                                st.session_state[
                                    "_wizard_deployment_strategy_description"
                                ] = str(
                                    ini.get("deployment_strategy_description") or ""
                                )
                            if ini.get("category") is not None:
                                # Check if the category is in the predefined list
                                yaml_path = (
                                    Path(__file__).parent.parent
                                    / "use_case_categories.yml"
                                )
                                try:
                                    with open(yaml_path, "r") as f:
                                        categories_data = yaml.safe_load(f)
                                    category_options = (
                                        list(categories_data.keys())
                                        if categories_data
                                        else []
                                    )
                                except Exception:
                                    category_options = []

                                category_value = ini.get("category")
                                if category_value in category_options:
                                    st.session_state["_wizard_category"] = (
                                        category_value
                                    )
                                    st.session_state["_wizard_category_other"] = ""
                                else:
                                    st.session_state["_wizard_category"] = "Other"
                                    st.session_state["_wizard_category_other"] = (
                                        category_value or ""
                                    )
                            if ini.get("out_of_scope") is not None:
                                st.session_state["_wizard_out_of_scope"] = str(
                                    ini.get("out_of_scope") or ""
                                )
                            if ini.get("no_move_forward") is not None:
                                st.session_state["no_move_forward"] = ini.get(
                                    "no_move_forward"
                                )
                            if ini.get("no_move_forward_reasons") is not None:
                                # Set the widget key directly
                                vals = ini.get("no_move_forward_reasons") or []
                                if isinstance(vals, list):
                                    st.session_state["no_move_forward_reasons"] = vals
                                else:
                                    st.session_state["no_move_forward_reasons"] = []
                            # ignore legacy initiative.solution_details_md in uploads

                            # My Role
                            my_role = data.get("my_role", {}) or {}
                            who = (my_role.get("who") or "").strip()
                            skills = (my_role.get("skills") or "").strip()
                            dev = (my_role.get("developer") or "").strip()
                            # For each, set radio to value or 'Other' and capture other text
                            if who:
                                known_who = {
                                    "I'm a network engineer.",
                                    "I'm a software developer.",
                                    "I manage technical projects or teams.",
                                }
                                if who in known_who:
                                    st.session_state["my_role_who"] = who
                                else:
                                    st.session_state["my_role_who"] = "Other (fill in)"
                                    st.session_state["my_role_who_other"] = who
                            if skills:
                                known_sk = {
                                    "I have some scripting skills and basic software development experience.",
                                    "I am an advanced software developer.",
                                    "I provide techncial management on network and automation projects.",
                                }
                                if skills in known_sk:
                                    st.session_state["my_role_skills"] = skills
                                else:
                                    st.session_state["my_role_skills"] = (
                                        "Other (fill in)"
                                    )
                                    st.session_state["my_role_skills_other"] = skills
                            if dev:
                                known_dev = {
                                    "I'll do it myself.",
                                    "My in-house team and I will build it.",
                                    "We will have outside experts build it, but I'll provide technical oversight.",
                                }
                                if dev in known_dev:
                                    st.session_state["my_role_dev"] = dev
                                else:
                                    st.session_state["my_role_dev"] = "Other (fill in)"
                                    st.session_state["my_role_dev_other"] = dev

                            # Stakeholders
                            stakeholders = data.get("stakeholders", {}) or {}
                            if stakeholders.get("choices") is not None:
                                # Ensure choices is a dictionary
                                choices = stakeholders.get("choices")
                                if isinstance(choices, dict):
                                    # Use choices as-is since we no longer support old category names
                                    st.session_state["stakeholders_choices"] = choices
                                else:
                                    st.session_state["stakeholders_choices"] = {}
                            else:
                                st.session_state["stakeholders_choices"] = {}
                            if stakeholders.get("other") is not None:
                                st.session_state["stakeholders_other_text"] = str(
                                    stakeholders.get("other") or ""
                                )

                            # Presentation
                            pres = data.get("presentation", {}) or {}
                            pres_sel = pres.get("selections", {}) or {}
                            for u in pres_sel.get("users", []) or []:
                                st.session_state[f"pres_user_{u}"] = True
                            known_interact = {"CLI", "Web GUI", "Other GUI", "API"}
                            for it in pres_sel.get("interactions", []) or []:
                                if it in known_interact:
                                    st.session_state[f"pres_interact_{it}"] = True
                                else:
                                    st.session_state["pres_interact_custom_enable"] = (
                                        True
                                    )
                                    st.session_state["pres_interact_custom"] = it
                            known_tools = {
                                "Python",
                                "Python Web Framework (Streamlit, Flask, etc.)",
                                "General Web Framework",
                                "Automation Framework",
                                "REST API",
                                "GraphQL API",
                                "Custom API",
                            }
                            for t in pres_sel.get("tools", []) or []:
                                if t in known_tools:
                                    st.session_state[f"pres_tool_{t}"] = True
                                else:
                                    st.session_state["pres_tool_custom_enable"] = True
                                    st.session_state["pres_tool_custom"] = t
                            known_auth = {
                                "No Authentication (suitable only for demos and very specific use cases)",
                                "Repository authorization/sharing",
                                "Built-in Authentication via Username/Password or TOKEN",
                                "Custom Authentication to external system (AD, SSH Keys, OAUTH2)",
                            }
                            for a in pres_sel.get("auth", []) or []:
                                if a in known_auth:
                                    st.session_state[f"pres_auth_{a}"] = True
                                else:
                                    st.session_state["pres_auth_other_enable"] = True
                                    st.session_state["pres_auth_other_text"] = a

                            # Intent
                            intent = data.get("intent", {}) or {}
                            intent_sel = intent.get("selections", {}) or {}
                            known_dev = {
                                "Templates",
                                "Policies",
                                "Service Profiles",
                                "Model-driven (data models)",
                                "Declarative (YAML/JSON)",
                                "Forms/GUI",
                                "Domain-specific language (DSL)",
                                "GitOps workflow (PRs/Reviews)",
                                "API-driven",
                                "Import from Source of Truth (CMDB/IPAM/Inventory/Git)",
                            }
                            unknown_devs = []
                            for v in intent_sel.get("development", []) or []:
                                if v in known_dev:
                                    st.session_state[f"intent_dev_{v}"] = True
                                else:
                                    unknown_devs.append(v)
                            if unknown_devs:
                                st.session_state["intent_dev_custom_enable"] = True
                                st.session_state["intent_dev_custom"] = ", ".join(
                                    unknown_devs
                                )
                            known_prov = {
                                "Text file",
                                "Serialized format (JSON, YAML)",
                                "CSV",
                                "Excel",
                                "API",
                            }
                            unknown_prov = []
                            for v in intent_sel.get("provided", []) or []:
                                if v in known_prov:
                                    st.session_state[f"intent_prov_{v}"] = True
                                else:
                                    unknown_prov.append(v)
                            if unknown_prov:
                                st.session_state["intent_prov_custom_enable"] = True
                                st.session_state["intent_prov_custom"] = ", ".join(
                                    unknown_prov
                                )

                            # Observability
                            obs = data.get("observability", {}) or {}
                            obs_sel = obs.get("selections", {}) or {}
                            for m in obs_sel.get("methods", []) or []:
                                st.session_state[f"obs_state_{m}"] = True
                            known_obs_tools = {
                                "Open Source",
                                "Commercial/Enterprise Product",
                                "Network Vendor Product (Cisco Catalyst Center, Arista CVP, PAN Panorama,etc.)",
                                "Custom Python Scripts",
                            }
                            for t in obs_sel.get("tools", []) or []:
                                if t in known_obs_tools:
                                    st.session_state[f"obs_tool_{t}"] = True
                                else:
                                    st.session_state["obs_tool_other_enable"] = True
                                    st.session_state["obs_tool_other_text"] = t
                            if obs_sel.get("go_no_go_text") is not None:
                                st.session_state["obs_go_no_go"] = obs_sel.get(
                                    "go_no_go_text"
                                )
                            st.session_state["obs_add_logic_choice"] = (
                                "Yes"
                                if obs_sel.get("additional_logic_enabled")
                                else "No"
                            )
                            if obs_sel.get("additional_logic_text") is not None:
                                st.session_state["obs_add_logic_text"] = obs_sel.get(
                                    "additional_logic_text"
                                )

                            # Orchestration
                            orch_sel = (data.get("orchestration", {}) or {}).get(
                                "selections", {}
                            )
                            if orch_sel.get("choice") is not None:
                                st.session_state["orch_choice"] = orch_sel.get("choice")
                            if orch_sel.get("details") is not None:
                                st.session_state["orch_details_text"] = orch_sel.get(
                                    "details"
                                )

                            # Collector
                            col_sel = (data.get("collector", {}) or {}).get(
                                "selections", {}
                            )
                            for m in col_sel.get("methods", []) or []:
                                for known in [
                                    "SNMP",
                                    "CLI/SSH",
                                    "NETCONF",
                                    "gNMI",
                                    "REST API",
                                    "Webhooks",
                                    "Syslog",
                                    "Streaming Telemetry",
                                ]:
                                    if m == known:
                                        st.session_state[
                                            f"collector_method_{known}"
                                        ] = True
                                        break
                                else:
                                    st.session_state[
                                        "collector_methods_other_enable"
                                    ] = True
                                    st.session_state["collector_methods_other"] = m
                            for a in col_sel.get("auth", []) or []:
                                for known in [
                                    "Username/Password",
                                    "SSH Keys",
                                    "OAuth2",
                                    "API Token",
                                    "mTLS",
                                ]:
                                    if a == known:
                                        st.session_state[f"collector_auth_{known}"] = (
                                            True
                                        )
                                        break
                                else:
                                    st.session_state["collector_auth_other_enable"] = (
                                        True
                                    )
                                    st.session_state["collector_auth_other"] = a
                            for h in col_sel.get("handling", []) or []:
                                for known in [
                                    "None",
                                    "Rate limiting",
                                    "Retries",
                                    "Exponential backoff",
                                    "Buffering/Queue",
                                ]:
                                    if h == known:
                                        st.session_state[
                                            f"collector_handle_{known}"
                                        ] = True
                                        break
                                else:
                                    st.session_state[
                                        "collector_handling_other_enable"
                                    ] = True
                                    st.session_state["collector_handling_other"] = h
                            for n in col_sel.get("normalization", []) or []:
                                for known in [
                                    "None",
                                    "Timestamping",
                                    "Tagging/labels",
                                    "Topology enrichment",
                                    "Schema mapping",
                                ]:
                                    if n == known:
                                        st.session_state[f"collector_norm_{known}"] = (
                                            True
                                        )
                                        break
                                else:
                                    st.session_state["collector_norm_other_enable"] = (
                                        True
                                    )
                                    st.session_state["collector_norm_other"] = n
                            for t in col_sel.get("tools", []) or []:
                                for known in [
                                    "None",
                                    "Open Source",
                                    "Commercial/Enterprise Product",
                                    "Network Vendor Product (Cisco Catalyst Center, Arista CVP, PAN Panorama, etc.)",
                                    "Custom Python Scripts",
                                ]:
                                    if t == known:
                                        st.session_state[f"collection_tool_{known}"] = (
                                            True
                                        )
                                        break
                                else:
                                    st.session_state[
                                        "collection_tools_other_enable"
                                    ] = True
                                    st.session_state["collection_tools_other"] = t
                            if col_sel.get("devices") is not None:
                                st.session_state["collector_devices"] = str(
                                    col_sel.get("devices")
                                )
                            if col_sel.get("metrics_per_sec") is not None:
                                st.session_state["collector_metrics"] = str(
                                    col_sel.get("metrics_per_sec")
                                )
                            if col_sel.get("cadence") is not None:
                                st.session_state["collector_cadence"] = str(
                                    col_sel.get("cadence")
                                )

                            # Executor
                            exec_sel = (data.get("executor", {}) or {}).get(
                                "selections", {}
                            )
                            exec_opts = [
                                "Automating CLI interaction with Python automation frameworks (Netmiko, Napalm, Nornir, PyATS)",
                                "Automating execution with a tool like Ansible",
                                "Custom Python scripts",
                                "Via manufacturer management application (Cisco DNA Center, Arista CVP)",
                            ]
                            for m in exec_sel.get("methods", []) or []:
                                for i, known in enumerate(exec_opts):
                                    if m == known:
                                        st.session_state[f"exec_{i}"] = True
                                        break
                                else:
                                    # Custom executor method
                                    st.session_state["exec_custom_enable"] = True
                                    st.session_state["exec_custom_text"] = m

                            # Dependencies
                            dep_list = data.get("dependencies", []) or []
                            label_to_key = {
                                "Network Infrastructure": "network_infra",
                                "Network Controllers": "network_controllers",
                                "Revision Control system": "revision_control",
                                "ITSM/Change Management System": "itsm",
                                "Authentication System": "authn",
                                "IPAMS Systems": "ipams",
                                "Inventory Systems": "inventory",
                                "Design Data/Intent Systems": "design_intent",
                                "Observability System": "observability",
                                "Vendor Tool/Management System": "vendor_mgmt",
                            }
                            for d in dep_list:
                                lbl = (d or {}).get("name")
                                details = (d or {}).get("details", "")
                                key = label_to_key.get(lbl)
                                if key:
                                    st.session_state[f"dep_{key}"] = True
                                    if details:
                                        st.session_state[f"dep_{key}_details"] = details

                            # Timeline basics
                            tl = data.get("timeline", {}) or {}
                            if tl.get("build_buy") is not None:
                                st.session_state["timeline_build_buy"] = tl.get(
                                    "build_buy"
                                )
                            if tl.get("staff_count") is not None:
                                st.session_state["timeline_staff_count"] = int(
                                    tl.get("staff_count") or 0
                                )
                            if tl.get("external_staff_count") is not None:
                                st.session_state["timeline_external_staff_count"] = int(
                                    tl.get("external_staff_count") or 0
                                )
                            if tl.get("staffing_plan_md") is not None:
                                st.session_state["timeline_staffing_plan"] = tl.get(
                                    "staffing_plan_md"
                                )
                            if tl.get("holiday_region") is not None:
                                st.session_state["timeline_holiday_region"] = (
                                    tl.get("holiday_region") or "None"
                                )
                            if tl.get("start_date"):
                                parsed = None
                                try:
                                    parsed = datetime.datetime.strptime(
                                        str(tl.get("start_date")), "%Y-%m-%d"
                                    ).date()
                                except Exception:
                                    try:
                                        parsed = datetime.datetime.fromisoformat(
                                            str(tl.get("start_date"))
                                        ).date()
                                    except Exception:
                                        parsed = None
                                if parsed is not None:
                                    st.session_state["timeline_start_date"] = parsed

                            # Timeline milestones from items
                            items = tl.get("items") or []
                            if isinstance(items, list) and items:
                                # Clear existing row-level timeline widget keys so widgets adopt new values
                                for k in list(st.session_state.keys()):
                                    if k.startswith(
                                        (
                                            "_tl_name_",
                                            "_tl_duration_",
                                            "_tl_notes_",
                                            "_tl_del_",
                                        )
                                    ):
                                        st.session_state.pop(k, None)
                                ms = []
                                for it in items:
                                    try:
                                        nm = str((it or {}).get("name") or "").strip()
                                        dur = int((it or {}).get("duration_bd") or 0)
                                        notes = str((it or {}).get("notes") or "")
                                    except Exception:
                                        nm, dur, notes = (
                                            str((it or {}).get("name") or ""),
                                            0,
                                            str((it or {}).get("notes") or ""),
                                        )
                                    ms.append(
                                        {
                                            "name": nm,
                                            "duration": dur,
                                            "notes": notes,
                                        }
                                    )
                                if ms:
                                    st.session_state["timeline_milestones"] = ms
                                    # Seed row-level widget keys to reflect uploaded values
                                    for i, r in enumerate(ms):
                                        st.session_state[f"_tl_name_{i}"] = r.get(
                                            "name", ""
                                        )
                                        st.session_state[f"_tl_duration_{i}"] = int(
                                            r.get("duration", 0)
                                        )
                                        st.session_state[f"_tl_notes_{i}"] = r.get(
                                            "notes", ""
                                        )

                            # LEGACY: Store all wizard data in backing storage for inter-page navigation
                            # No longer needed with single-page operation
                            # TODO: Remove this entirely after confirming stability
                            st.session_state["_wizard_data"] = {
                                "my_role_who": st.session_state.get("my_role_who"),
                                "my_role_skills": st.session_state.get(
                                    "my_role_skills"
                                ),
                                "my_role_dev": st.session_state.get("my_role_dev"),
                                "my_role_who_other": st.session_state.get(
                                    "my_role_who_other"
                                ),
                                "my_role_skills_other": st.session_state.get(
                                    "my_role_skills_other"
                                ),
                                "my_role_dev_other": st.session_state.get(
                                    "my_role_dev_other"
                                ),
                                "stakeholders_choices": st.session_state.get(
                                    "stakeholders_choices"
                                ),
                                "stakeholders_other_text": st.session_state.get(
                                    "stakeholders_other_text"
                                ),
                                "orch_choice": st.session_state.get("orch_choice"),
                                "orch_details_text": st.session_state.get(
                                    "orch_details_text"
                                ),
                                "_wizard_automation_title": st.session_state.get(
                                    "_wizard_automation_title"
                                ),
                                "_wizard_automation_description": st.session_state.get(
                                    "_wizard_automation_description"
                                ),
                                "_wizard_category": st.session_state.get(
                                    "_wizard_category"
                                ),
                                "_wizard_category_other": st.session_state.get(
                                    "_wizard_category_other"
                                ),
                                "_wizard_problem_statement": st.session_state.get(
                                    "_wizard_problem_statement"
                                ),
                                "_wizard_expected_use": st.session_state.get(
                                    "_wizard_expected_use"
                                ),
                                "_wizard_error_conditions": st.session_state.get(
                                    "_wizard_error_conditions"
                                ),
                                "_wizard_assumptions": st.session_state.get(
                                    "_wizard_assumptions"
                                ),
                                "_wizard_deployment_strategy": st.session_state.get(
                                    "_wizard_deployment_strategy"
                                ),
                                "_wizard_deployment_strategy_other": st.session_state.get(
                                    "_wizard_deployment_strategy_other"
                                ),
                                "_wizard_deployment_strategy_description": st.session_state.get(
                                    "_wizard_deployment_strategy_description"
                                ),
                                "_wizard_out_of_scope": st.session_state.get(
                                    "_wizard_out_of_scope"
                                ),
                                "no_move_forward": st.session_state.get(
                                    "no_move_forward"
                                ),
                                "no_move_forward_reasons": st.session_state.get(
                                    "no_move_forward_reasons"
                                ),
                                "obs_go_no_go": st.session_state.get("obs_go_no_go"),
                                "obs_add_logic_choice": st.session_state.get(
                                    "obs_add_logic_choice"
                                ),
                                "obs_add_logic_text": st.session_state.get(
                                    "obs_add_logic_text"
                                ),
                                "collector_devices": st.session_state.get(
                                    "collector_devices"
                                ),
                                "collector_metrics": st.session_state.get(
                                    "collector_metrics"
                                ),
                                "collector_cadence": st.session_state.get(
                                    "collector_cadence"
                                ),
                            }
                            # Also store all checkbox and widget states that need to persist
                            widget_keys = [
                                k
                                for k in st.session_state.keys()
                                if any(
                                    k.startswith(p)
                                    for p in (
                                        "pres_user_",
                                        "pres_interact_",
                                        "pres_tool_",
                                        "pres_auth_",
                                        "intent_dev_",
                                        "intent_prov_",
                                        "obs_state_",
                                        "obs_tool_",
                                        "collector_method_",
                                        "collector_auth_",
                                        "collector_handle_",
                                        "collector_norm_",
                                        "collection_tool_",
                                        "collection_tools_",
                                        "collector_methods_",
                                        "collector_handling_",
                                        "exec_",
                                        "dep_",
                                        "_tl_",
                                        "_timeline_",
                                    )
                                )
                            ]
                            st.session_state["_wizard_checkboxes"] = {
                                k: st.session_state.get(k) for k in widget_keys
                            }

                            # Mark that JSON was loaded (for debugging/verification)
                            st.session_state["_json_loaded"] = True
                            st.success(
                                "Applied uploaded JSON to this session. Widgets will reflect values now."
                            )
                            st.rerun()

                    except Exception as e:
                        st.error(f"Failed to load JSON: {e}")

    # --------------- END of SIDEBAR -----------------

    # LEGACY: Restore widget keys from backing storage (no longer needed with single page)
    # This was required when navigating between pages because Streamlit clears widget state
    # TODO: Consider removing this entirely after confirming single-page operation is stable
    if "_wizard_data" in st.session_state:
        wd = st.session_state["_wizard_data"]
        for key, value in wd.items():
            if value is not None and key not in st.session_state:
                st.session_state[key] = value

    if "_wizard_checkboxes" in st.session_state:
        wc = st.session_state["_wizard_checkboxes"]
        for key, value in wc.items():
            if key not in st.session_state:
                st.session_state[key] = value

    # Title with NAF icon
    title_cols = st.columns([0.08, 0.92])
    with title_cols[0]:
        st.image("images/naf_icon.png", width="stretch")
    with title_cols[1]:
        st.markdown("**Network Automation Forum's Network Automation Framework**")

    # ── Puzzle Progress (interactive – TODO: remove demo scaffolding after testing) ──

    # Initialize demo completion tracking (separate from expander-based completion)
    if "_demo_completed" not in st.session_state:
        st.session_state["_demo_completed"] = {key: False for key in PUZZLE_SECTIONS}

    # ── Dialog definitions (placeholder forms for testing) ──────────
    # TODO: Replace placeholder dialogs with full section forms once tested.
    #       When doing so, remove the matching expander sections below to
    #       avoid DuplicateWidgetID errors on shared session_state keys.

    @st.dialog("Presentation", width="large")
    def _dlg_presentation():
        st.markdown(
            """
**Presentation Layer Characteristics**
- Provides robust, flexible authentication and authorization.
- Can take many forms: GUIs, ITSM/change systems, chat/messaging, portals, reports.
- May support read and write: view data, initiate tasks, approve changes.
- Interfaces with other framework blocks as needed; it is the primary human touchpoint.
            """
        )

        # --- Intended users ---
        st.subheader("Intended users")
        _du_cols = st.columns(3)
        _du_user_opts = [
            "Network Engineers", "IT", "Operations", "Help Desk",
            "Other IT Organizations", "Any User", "Authorized Users", "Automation Pipeline",
        ]
        for i, opt in enumerate(_du_user_opts):
            with _du_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_pres_user_{opt}",
                            value=st.session_state.get(f"pres_user_{opt}", False))
        with _du_cols[0]:
            _du_cust_en = st.checkbox("Custom (fill in)", key="dlg_pres_user_custom_enable",
                                      value=st.session_state.get("pres_user_custom_enable", False))
            if _du_cust_en:
                st.text_input("Custom users", key="dlg_pres_user_custom",
                              value=st.session_state.get("pres_user_custom", ""))

        # --- Interaction modes ---
        st.subheader("How will your users interact with your solution?")
        _di_cols = st.columns(3)
        _di_opts = [
            "CLI", "Purpose-built Web GUI", "Other GUI",
            "API", "Commercial Product/GUI", "Open Source Product/GUI",
        ]
        for i, opt in enumerate(_di_opts):
            with _di_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_pres_interact_{opt}",
                            value=st.session_state.get(f"pres_interact_{opt}", False))
        with _di_cols[0]:
            _di_cust_en = st.checkbox("Custom (fill in)", key="dlg_pres_interact_custom_enable",
                                      value=st.session_state.get("pres_interact_custom_enable", False))
            if _di_cust_en:
                st.text_input("Custom interaction", key="dlg_pres_interact_custom",
                              value=st.session_state.get("pres_interact_custom", ""))

        # --- Tools ---
        st.subheader("What tools will the Presentation layer use?")
        _dt_cols = st.columns(3)
        _dt_opts = [
            "Python", "Python Web Framework (Streamlit, Flask, etc.)",
            "General Web Framework", "Automation Framework",
            "REST API", "GraphQL API", "Custom API",
        ]
        for i, opt in enumerate(_dt_opts):
            with _dt_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_pres_tool_{opt}",
                            value=st.session_state.get(f"pres_tool_{opt}", False))
        with _dt_cols[0]:
            _dt_cust_en = st.checkbox("Custom (fill in)", key="dlg_pres_tool_custom_enable",
                                      value=st.session_state.get("pres_tool_custom_enable", False))
            if _dt_cust_en:
                st.text_input("Custom tool(s)", key="dlg_pres_tool_custom",
                              value=st.session_state.get("pres_tool_custom", ""))

        # --- Authentication ---
        st.subheader("How will your users authenticate?")
        _da_cols = st.columns(2)
        _da_opts = [
            "No Authentication (suitable only for demos and very specific use cases)",
            "Repository authorization/sharing",
            "Built-in (to the automation) Authentication via Username/Password or TOKEN",
            "Custom Authentication to external system (AD, SSH Keys, OAUTH2)",
        ]
        for i, opt in enumerate(_da_opts):
            with _da_cols[i % 2]:
                st.checkbox(opt, key=f"dlg_pres_auth_{opt}",
                            value=st.session_state.get(f"pres_auth_{opt}", False))
        with _da_cols[0]:
            _da_oth_en = st.checkbox("Other (fill in details)", key="dlg_pres_auth_other_enable",
                                     value=st.session_state.get("pres_auth_other_enable", False))
            if _da_oth_en:
                st.text_input("Other authentication details", key="dlg_pres_auth_other_text",
                              value=st.session_state.get("pres_auth_other_text", ""))

        # --- Submit ---
        st.divider()
        if st.button("Submit Presentation", type="primary", use_container_width=True):
            # Copy dialog selections to the real session_state keys
            ss = st.session_state
            for opt in _du_user_opts:
                ss[f"pres_user_{opt}"] = ss.get(f"dlg_pres_user_{opt}", False)
            ss["pres_user_custom_enable"] = ss.get("dlg_pres_user_custom_enable", False)
            ss["pres_user_custom"] = ss.get("dlg_pres_user_custom", "")
            for opt in _di_opts:
                ss[f"pres_interact_{opt}"] = ss.get(f"dlg_pres_interact_{opt}", False)
            ss["pres_interact_custom_enable"] = ss.get("dlg_pres_interact_custom_enable", False)
            ss["pres_interact_custom"] = ss.get("dlg_pres_interact_custom", "")
            for opt in _dt_opts:
                ss[f"pres_tool_{opt}"] = ss.get(f"dlg_pres_tool_{opt}", False)
            ss["pres_tool_custom_enable"] = ss.get("dlg_pres_tool_custom_enable", False)
            ss["pres_tool_custom"] = ss.get("dlg_pres_tool_custom", "")
            for opt in _da_opts:
                ss[f"pres_auth_{opt}"] = ss.get(f"dlg_pres_auth_{opt}", False)
            ss["pres_auth_other_enable"] = ss.get("dlg_pres_auth_other_enable", False)
            ss["pres_auth_other_text"] = ss.get("dlg_pres_auth_other_text", "")
            # Mark puzzle piece as complete
            ss["_demo_completed"]["presentation"] = True
            st.rerun()

    @st.dialog("Observability", width="large")
    def _dlg_observability():
        st.markdown(
            """
**Observability Layer Characteristics**
- Supports historical data persistence with powerful programmatic access for analytics, reporting, and troubleshooting.
- Provides a capable query language to extract and explore data.
- Surfaces current-state insights and emits events when drift is detected between observed and intended state.
- Data may be enriched with context from intended state and third parties (e.g., EoL, CVEs, maintenance notices).
            """
        )

        # --- How will you determine network state? ---
        st.subheader("How will you determine network state?")
        _do_cols = st.columns(3)
        _do_state_opts = ["Manual", "Purpose-built Python Script", "API call"]
        for i, opt in enumerate(_do_state_opts):
            with _do_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_obs_state_{opt}",
                            value=st.session_state.get(f"obs_state_{opt}", False))

        # --- Go/No-Go criteria ---
        st.subheader("Describe the basic go/no go logic")
        st.text_area(
            "Go/No-Go criteria",
            key="dlg_obs_go_no_go",
            value=st.session_state.get("obs_go_no_go", ""),
            placeholder="e.g., Proceed if all pre-checks pass and no policy violations are detected",
        )

        # --- Additional gating logic ---
        st.subheader("Will there be additional logic applied to state to determine if the automation can move forward?")
        _do_add_opts = ["No", "Yes"]
        _do_add_idx = _do_add_opts.index(st.session_state.get("obs_add_logic_choice", "No")) if st.session_state.get("obs_add_logic_choice", "No") in _do_add_opts else 0
        _do_add_choice = st.radio(
            "Additional gating logic?",
            _do_add_opts,
            horizontal=True,
            key="dlg_obs_add_logic_choice",
            index=_do_add_idx,
        )
        if _do_add_choice == "Yes":
            st.text_area(
                "Describe additional logic",
                key="dlg_obs_add_logic_text",
                value=st.session_state.get("obs_add_logic_text", ""),
            )

        # --- Observability tools ---
        st.subheader("What tools will be used to support the observability layer?")
        _do_t_cols = st.columns(3)
        _do_tool_opts = [
            "Open Source Software",
            "Commercial/Enterprise Product",
            "Network Vendor Product (Cisco Catalyst Center, Arista CVP, etc.)",
            "Custom Python Scripts",
        ]
        for i, opt in enumerate(_do_tool_opts):
            with _do_t_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_obs_tool_{opt}",
                            value=st.session_state.get(f"obs_tool_{opt}", False))
        _do_t_oth_en = st.checkbox("Other (fill in)", key="dlg_obs_tool_other_enable",
                                   value=st.session_state.get("obs_tool_other_enable", False))
        if _do_t_oth_en:
            st.text_input("Other observability tool(s)", key="dlg_obs_tool_other_text",
                          value=st.session_state.get("obs_tool_other_text", ""))

        # --- Submit ---
        st.divider()
        if st.button("Submit Observability", type="primary", use_container_width=True):
            ss = st.session_state
            # Copy state method selections
            for opt in _do_state_opts:
                ss[f"obs_state_{opt}"] = ss.get(f"dlg_obs_state_{opt}", False)
            # Copy go/no-go
            ss["obs_go_no_go"] = ss.get("dlg_obs_go_no_go", "")
            # Copy additional logic
            ss["obs_add_logic_choice"] = ss.get("dlg_obs_add_logic_choice", "No")
            ss["obs_add_logic_text"] = ss.get("dlg_obs_add_logic_text", "")
            # Copy tool selections
            for opt in _do_tool_opts:
                ss[f"obs_tool_{opt}"] = ss.get(f"dlg_obs_tool_{opt}", False)
            ss["obs_tool_other_enable"] = ss.get("dlg_obs_tool_other_enable", False)
            ss["obs_tool_other_text"] = ss.get("dlg_obs_tool_other_text", "")
            # Mark puzzle piece as complete
            ss["_demo_completed"]["observability"] = True
            st.rerun()

    @st.dialog("Orchestration", width="large")
    def _dlg_orchestration():
        st.markdown(
            """
**Orchestration Layer Characteristics**
- Coordinates processes across framework components to create end-to-end workflows.
- Event-driven execution (sync, async, scheduled) with safe rollback/compensation on errors.
- Dry-run previews before execution, scheduling (one-time or recurring).
- Logging, tracing, and audit visibility; optional event correlation and inference.
            """
        )

        st.subheader("Will the solution utilize orchestration?")
        _ORCH_SENTINEL = "— Select one —"
        _do_orch_options = [
            _ORCH_SENTINEL,
            "No",
            "Yes – internal via custom scripts and logic",
            "Yes – provide details",
        ]
        _do_cur = st.session_state.get("orch_choice", _ORCH_SENTINEL)
        _do_idx = _do_orch_options.index(_do_cur) if _do_cur in _do_orch_options else 0
        _do_orch_choice = st.radio(
            "Select an option",
            _do_orch_options,
            key="dlg_orch_choice",
            index=_do_idx,
            horizontal=False,
        )

        _do_orch_details = ""
        if _do_orch_choice == "Yes – provide details":
            _do_orch_details = st.text_area(
                "Describe the orchestration approach",
                key="dlg_orch_details_text",
                value=st.session_state.get("orch_details_text", ""),
                placeholder="e.g., Use a workflow engine to trigger validations, approvals, execution, and post-checks; event-driven via webhooks; nightly reconciliations; rollback on failure; full traceability.",
            )

        # --- Submit ---
        st.divider()
        if st.button("Submit Orchestration", type="primary", use_container_width=True):
            ss = st.session_state
            ss["orch_choice"] = ss.get("dlg_orch_choice", _ORCH_SENTINEL)
            ss["orch_details_text"] = ss.get("dlg_orch_details_text", "")
            ss["_demo_completed"]["orchestration"] = True
            st.rerun()

    @st.dialog("Intent", width="large")
    def _dlg_intent():
        st.markdown(
            """
**Intent Layer Characteristics**
- Represents any network aspect in a structured form (addressing, DC infrastructure, routing, virtual services, secrets, operational limits, templates/mappings, policies, artifacts).
- Supports full CRUD operations and exposes a standard, well-documented API (e.g., REST, GraphQL).
- Uses neutral models that derive into vendor-specific configurations.
- Provides a unified desired-state view across potentially distributed data sources.
- Includes governance metadata (timestamps, origin, ownership, validity windows).

***When first starting out abstraction may be low and so intent could be as simple as a file with vlan numbers and names you want to provision.***
            """
        )

        # --- How will Intent be developed? ---
        st.subheader("How will Intent be developed?")
        _di_cols = st.columns(3)
        _di_dev_opts = [
            "Templates", "Policies", "Service Profiles",
            "Model-driven (data models)", "Declarative (YAML/JSON)", "Forms/GUI",
            "Domain-specific language (DSL)", "GitOps workflow (PRs/Reviews)",
            "API-driven", "Import from Source of Truth (CMDB/IPAM/Inventory/Git)",
        ]
        for i, opt in enumerate(_di_dev_opts):
            with _di_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_intent_dev_{opt}",
                            value=st.session_state.get(f"intent_dev_{opt}", False))
        _di_cust_en = st.checkbox("Custom (fill in)", key="dlg_intent_dev_custom_enable",
                                  value=st.session_state.get("intent_dev_custom_enable", False))
        if _di_cust_en:
            st.text_input("Custom intent development approach", key="dlg_intent_dev_custom",
                          value=st.session_state.get("intent_dev_custom", ""))

        # --- How will intent be consumed by automation? ---
        st.subheader("How will intent be consumed by automation?")
        _di_p_cols = st.columns(3)
        _di_prov_opts = [
            "Text file", "Serialized format (JSON, YAML)", "CSV", "Excel", "API",
        ]
        for i, opt in enumerate(_di_prov_opts):
            with _di_p_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_intent_prov_{opt}",
                            value=st.session_state.get(f"intent_prov_{opt}", False))
        with _di_p_cols[0]:
            _di_p_cust_en = st.checkbox("Custom (fill in)", key="dlg_intent_prov_custom_enable",
                                        value=st.session_state.get("intent_prov_custom_enable", False))
            if _di_p_cust_en:
                st.text_input("Custom provider format", key="dlg_intent_prov_custom",
                              value=st.session_state.get("intent_prov_custom", ""))

        # --- Submit ---
        st.divider()
        if st.button("Submit Intent", type="primary", use_container_width=True):
            ss = st.session_state
            for opt in _di_dev_opts:
                ss[f"intent_dev_{opt}"] = ss.get(f"dlg_intent_dev_{opt}", False)
            ss["intent_dev_custom_enable"] = ss.get("dlg_intent_dev_custom_enable", False)
            ss["intent_dev_custom"] = ss.get("dlg_intent_dev_custom", "")
            for opt in _di_prov_opts:
                ss[f"intent_prov_{opt}"] = ss.get(f"dlg_intent_prov_{opt}", False)
            ss["intent_prov_custom_enable"] = ss.get("dlg_intent_prov_custom_enable", False)
            ss["intent_prov_custom"] = ss.get("dlg_intent_prov_custom", "")
            ss["_demo_completed"]["intent"] = True
            st.rerun()

    @st.dialog("Collector", width="large")
    def _dlg_collector():
        st.markdown(
            """
**Collector Layer Characteristics**
- Retrieves the actual state of the network over time, ideally in a normalized format.
- Can be thought of as a "read only" version of the executor.
- Retrieved data should be normalized across vendors and collection methods in a time series format.
            """
        )

        # --- Collection methods ---
        st.subheader("Collection methods (protocols/APIs)")
        st.caption("Build your own approaches (protocols, handling, normalization)")
        _dc_cols = st.columns(3)
        _dc_method_opts = [
            "SNMP", "CLI/SSH", "NETCONF", "gNMI",
            "REST API", "Webhooks", "Syslog", "Streaming Telemetry",
        ]
        for i, opt in enumerate(_dc_method_opts):
            with _dc_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_collector_method_{opt}",
                            value=st.session_state.get(f"collector_method_{opt}", False))
        _dc_m_oth_en = st.checkbox("Other (fill in)", key="dlg_collector_methods_other_enable",
                                   value=st.session_state.get("collector_methods_other_enable", False))
        if _dc_m_oth_en:
            st.text_input("Other protocol/API", key="dlg_collector_methods_other",
                          value=st.session_state.get("collector_methods_other", ""))

        # --- Authentication ---
        st.subheader("Authentication")
        _dc_a_cols = st.columns(3)
        _dc_auth_opts = ["Username/Password", "SSH Keys", "OAuth2", "API Token", "mTLS"]
        for i, opt in enumerate(_dc_auth_opts):
            with _dc_a_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_collector_auth_{opt}",
                            value=st.session_state.get(f"collector_auth_{opt}", False))
        _dc_a_oth_en = st.checkbox("Other (fill in)", key="dlg_collector_auth_other_enable",
                                   value=st.session_state.get("collector_auth_other_enable", False))
        if _dc_a_oth_en:
            st.text_input("Other authentication method(s)", key="dlg_collector_auth_other",
                          value=st.session_state.get("collector_auth_other", ""))

        # --- Traffic handling ---
        st.subheader("Traffic handling")
        _dc_h_cols = st.columns(3)
        _dc_handle_opts = ["None", "Rate limiting", "Retries", "Exponential backoff", "Buffering/Queue"]
        for i, opt in enumerate(_dc_handle_opts):
            with _dc_h_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_collector_handle_{opt}",
                            value=st.session_state.get(f"collector_handle_{opt}", False))
        _dc_h_oth_en = st.checkbox("Other (fill in)", key="dlg_collector_handling_other_enable",
                                   value=st.session_state.get("collector_handling_other_enable", False))
        if _dc_h_oth_en:
            st.text_input("Other traffic handling approach(es)", key="dlg_collector_handling_other",
                          value=st.session_state.get("collector_handling_other", ""))

        # --- Normalization and schemas ---
        st.subheader("Normalization and schemas")
        _dc_n_cols = st.columns(3)
        _dc_norm_opts = ["None", "Timestamping", "Tagging/labels", "Topology enrichment", "Schema mapping"]
        for i, opt in enumerate(_dc_norm_opts):
            with _dc_n_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_collector_norm_{opt}",
                            value=st.session_state.get(f"collector_norm_{opt}", False))
        _dc_n_oth_en = st.checkbox("Other (fill in)", key="dlg_collector_norm_other_enable",
                                   value=st.session_state.get("collector_norm_other_enable", False))
        if _dc_n_oth_en:
            st.text_input("Other normalization/schema approach(es)", key="dlg_collector_norm_other",
                          value=st.session_state.get("collector_norm_other", ""))

        # --- OR divider ---
        st.divider()
        _or_c1, _or_c2, _or_c3 = st.columns([1, 1, 1])
        with _or_c2:
            st.markdown("**OR**")

        # --- Collection tools ---
        st.subheader("Collection tools")
        st.caption("Buy/use existing platforms (collection tools)")
        _dc_t_cols = st.columns(3)
        _dc_tool_opts = ["None", "Open Source Software", "Commercial/Enterprise Product", "In-house Software"]
        for i, opt in enumerate(_dc_tool_opts):
            with _dc_t_cols[i % 3]:
                st.checkbox(opt, key=f"dlg_collection_tool_{opt}",
                            value=st.session_state.get(f"collection_tool_{opt}", False))
        _dc_t_oth_en = st.checkbox("Other (fill in)", key="dlg_collection_tools_other_enable",
                                   value=st.session_state.get("collection_tools_other_enable", False))
        if _dc_t_oth_en:
            st.text_input("Other collection tool(s)", key="dlg_collection_tools_other",
                          value=st.session_state.get("collection_tools_other", ""))

        # --- Expected scale ---
        st.subheader("Expected scale")
        _dc_s1, _dc_s2, _dc_s3 = st.columns(3)
        with _dc_s1:
            st.text_input("Devices (approx)", key="dlg_collector_devices",
                          value=st.session_state.get("collector_devices", ""),
                          placeholder="e.g., 500")
        with _dc_s2:
            st.text_input("Metrics/sec (approx)", key="dlg_collector_metrics",
                          value=st.session_state.get("collector_metrics", ""),
                          placeholder="e.g., 50k")
        with _dc_s3:
            st.text_input("Polling/stream cadence", key="dlg_collector_cadence",
                          value=st.session_state.get("collector_cadence", ""),
                          placeholder="e.g., 30s polling; streaming realtime")

        # --- Submit ---
        st.divider()
        if st.button("Submit Collector", type="primary", use_container_width=True):
            ss = st.session_state
            for opt in _dc_method_opts:
                ss[f"collector_method_{opt}"] = ss.get(f"dlg_collector_method_{opt}", False)
            ss["collector_methods_other_enable"] = ss.get("dlg_collector_methods_other_enable", False)
            ss["collector_methods_other"] = ss.get("dlg_collector_methods_other", "")
            for opt in _dc_auth_opts:
                ss[f"collector_auth_{opt}"] = ss.get(f"dlg_collector_auth_{opt}", False)
            ss["collector_auth_other_enable"] = ss.get("dlg_collector_auth_other_enable", False)
            ss["collector_auth_other"] = ss.get("dlg_collector_auth_other", "")
            for opt in _dc_handle_opts:
                ss[f"collector_handle_{opt}"] = ss.get(f"dlg_collector_handle_{opt}", False)
            ss["collector_handling_other_enable"] = ss.get("dlg_collector_handling_other_enable", False)
            ss["collector_handling_other"] = ss.get("dlg_collector_handling_other", "")
            for opt in _dc_norm_opts:
                ss[f"collector_norm_{opt}"] = ss.get(f"dlg_collector_norm_{opt}", False)
            ss["collector_norm_other_enable"] = ss.get("dlg_collector_norm_other_enable", False)
            ss["collector_norm_other"] = ss.get("dlg_collector_norm_other", "")
            for opt in _dc_tool_opts:
                ss[f"collection_tool_{opt}"] = ss.get(f"dlg_collection_tool_{opt}", False)
            ss["collection_tools_other_enable"] = ss.get("dlg_collection_tools_other_enable", False)
            ss["collection_tools_other"] = ss.get("dlg_collection_tools_other", "")
            ss["collector_devices"] = ss.get("dlg_collector_devices", "")
            ss["collector_metrics"] = ss.get("dlg_collector_metrics", "")
            ss["collector_cadence"] = ss.get("dlg_collector_cadence", "")
            ss["_demo_completed"]["collector"] = True
            st.rerun()

    @st.dialog("Executor", width="large")
    def _dlg_executor():
        st.markdown(
            """
**Executor Layer Characteristics**
- Executes the actual changes to the network.
- MUST be capable of interacting with any supported network write interfaces (SSH/CLI, NETCONF, gNMI/gNOI, REST APIs).
- SHOULD support operations that alter network state, from deploying full/partial configs to device actions (reboots, upgrades).
- SHOULD provide a dry-run capability and support transactional execution.
- MAY support both imperative and declarative approaches, and operations SHOULD be idempotent.
            """
        )

        st.subheader("How will your solution execute change?")
        _de_cols = st.columns(2)
        _de_opts = [
            "Automating CLI interaction with Python automation frameworks (Netmiko, Napalm, Nornir, PyATS)",
            "Using Open Source Software (Ansible, Terraform, etc.)",
            "Using Custom Python scripts",
            "Using Network Vendor Product (Cisco DNA Center, Arista CVP)",
            "Using a Commercial/Enterprise Product",
        ]
        for i, opt in enumerate(_de_opts):
            with _de_cols[i % 2]:
                st.checkbox(opt, key=f"dlg_exec_{i}",
                            value=st.session_state.get(f"exec_{i}", False))
        with _de_cols[0]:
            _de_cust_en = st.checkbox("Custom (describe in detail)", key="dlg_exec_custom_enable",
                                      value=st.session_state.get("exec_custom_enable", False))
            if _de_cust_en:
                st.text_area("Custom execution approach", key="dlg_exec_custom_text",
                             value=st.session_state.get("exec_custom_text", ""))

        # --- Submit ---
        st.divider()
        if st.button("Submit Executor", type="primary", use_container_width=True):
            ss = st.session_state
            for i in range(len(_de_opts)):
                ss[f"exec_{i}"] = ss.get(f"dlg_exec_{i}", False)
            ss["exec_custom_enable"] = ss.get("dlg_exec_custom_enable", False)
            ss["exec_custom_text"] = ss.get("dlg_exec_custom_text", "")
            ss["_demo_completed"]["executor"] = True
            st.rerun()

    # ── Project Context & Planning dialogs ──────────────────────────

    @st.dialog("Problem Statement & Description", width="large")
    def _dlg_problem_statement():
        ss = st.session_state

        # ── Author, Title, Description ───────────────────────────────
        st.text_input(
            "Author",
            key="dlg_wizard_author",
            value=ss.get("_wizard_author", ""),
            help="Name of the person creating this automation initiative",
        )
        _dc1, _dc2 = st.columns([2, 3])
        with _dc1:
            st.text_input(
                "Automation initiative title",
                key="dlg_wizard_automation_title",
                value=ss.get("_wizard_automation_title", ""),
            )
        with _dc2:
            st.text_area(
                "Short description / scope",
                height=80,
                key="dlg_wizard_automation_description",
                value=ss.get("_wizard_automation_description", ""),
            )

        # ── Category (from YAML) ─────────────────────────────────────
        _cat_yaml = Path(__file__).parent.parent / "use_case_categories.yml"
        try:
            with open(_cat_yaml, "r") as f:
                _cat_data = yaml.safe_load(f)
            _cat_opts = list(_cat_data.keys()) if _cat_data else []
        except Exception:
            _cat_opts = []
        _cat_all = _cat_opts + ["Other"]
        _cur_cat = ss.get("_wizard_category", "")
        _cat_idx = _cat_all.index(_cur_cat) if _cur_cat in _cat_all else None
        dlg_cat = st.selectbox(
            "Category", options=_cat_all, index=_cat_idx,
            key="dlg_wizard_category", placeholder="Choose a category",
            help="Select a category from the list. Choose 'Other' if your initiative doesn't fit.",
        )
        if dlg_cat == "Other":
            st.text_input(
                "Custom category", key="dlg_wizard_category_other",
                value=ss.get("_wizard_category_other", ""),
            )

        # ── Core text fields ─────────────────────────────────────────
        st.text_area(
            "Problem Statement (Markdown supported)", height=80,
            key="dlg_wizard_problem_statement",
            value=ss.get("_wizard_problem_statement", ""),
            help="Describe the circumstances under which this automation will be used.",
        )
        st.text_area(
            "Expected Use/Triggers (Markdown supported)", height=80,
            key="dlg_wizard_expected_use",
            value=ss.get("_wizard_expected_use", ""),
            help="Describe the circumstances under which this automation will be used or triggered.",
        )
        st.text_area(
            "Error Conditions (Markdown supported)", height=80,
            key="dlg_wizard_error_conditions",
            value=ss.get("_wizard_error_conditions", ""),
            help="Note any expected error conditions that need to be addressed in the initial version",
        )
        st.text_area(
            "Assumptions (Markdown supported)", height=80,
            key="dlg_wizard_assumptions",
            value=ss.get("_wizard_assumptions", ""),
            help="List any assumptions made for this automation initiative.",
        )
        st.text_area(
            "Out of Scope (optional)", height=80,
            key="dlg_wizard_out_of_scope",
            value=ss.get("_wizard_out_of_scope", ""),
            help="List areas intentionally excluded from this initiative.",
        )

        # ── Deployment Strategy (from YAML) ──────────────────────────
        _dep_yaml = Path(__file__).parent.parent / "deployment_strategies.yml"
        try:
            with open(_dep_yaml, "r") as f:
                _dep_data = yaml.safe_load(f)
            _dep_opts = list(_dep_data.keys()) if _dep_data else []
        except Exception:
            _dep_opts = []
        _dep_all = _dep_opts + ["Other"]
        _cur_dep = ss.get("_wizard_deployment_strategy", "")
        _dep_idx = _dep_all.index(_cur_dep) if _cur_dep in _dep_all else None
        dlg_dep = st.selectbox(
            "Standard Deployment Strategy", options=_dep_all, index=_dep_idx,
            key="dlg_wizard_deployment_strategy", placeholder="Choose a deployment strategy",
            help="Select a standard deployment strategy or choose 'Other' to enter a custom one.",
        )
        if dlg_dep == "Other":
            st.text_input(
                "Custom Deployment Strategy", key="dlg_wizard_deployment_strategy_other",
                value=ss.get("_wizard_deployment_strategy_other", ""),
                placeholder="e.g., Pilot Program",
            )
        st.text_area(
            "Deployment Strategy Description (optional)", height=80,
            key="dlg_wizard_deployment_strategy_description",
            value=ss.get("_wizard_deployment_strategy_description", ""),
            help="Additional details about how the automation will be deployed.",
        )

        # ── Risk of not automating ───────────────────────────────────
        _standard_reasons = [
            "We are not improving the way our customers interact with us for service provisioning",
            "We are not improving the speed and quality of our service provisioning",
            "We are not meeting feature or service demands from our customers",
            "We will continue to pay for 3rd party support for this task",
            "This task will continue to be executed individually in an inconsistent and ad-hoc manner with varying degrees of success and documentation",
            "This task will continue to take far longer than it should resulting in poor customer satisfaction",
            "We risk continuing to add technical debt to the logical infrastructure",
        ]
        st.multiselect(
            "Risk of not doing the automation", options=_standard_reasons,
            default=ss.get("no_move_forward_reasons", []),
            key="dlg_no_move_forward_reasons",
            help="Select one or more risks that apply to your project.",
            placeholder="Choose one or more options",
        )
        st.text_area(
            "Additional risks in not moving forward (optional)", height=80,
            key="dlg_no_move_forward",
            value=ss.get("no_move_forward", ""),
        )

        # ── Submit ───────────────────────────────────────────────────
        st.divider()
        if st.button("Submit Problem Statement", type="primary", use_container_width=True):
            # Sync all dlg_ keys to real keys
            _text_map = {
                "dlg_wizard_author": "_wizard_author",
                "dlg_wizard_automation_title": "_wizard_automation_title",
                "dlg_wizard_automation_description": "_wizard_automation_description",
                "dlg_wizard_problem_statement": "_wizard_problem_statement",
                "dlg_wizard_expected_use": "_wizard_expected_use",
                "dlg_wizard_error_conditions": "_wizard_error_conditions",
                "dlg_wizard_assumptions": "_wizard_assumptions",
                "dlg_wizard_out_of_scope": "_wizard_out_of_scope",
                "dlg_wizard_deployment_strategy": "_wizard_deployment_strategy",
                "dlg_wizard_deployment_strategy_other": "_wizard_deployment_strategy_other",
                "dlg_wizard_deployment_strategy_description": "_wizard_deployment_strategy_description",
                "dlg_wizard_category": "_wizard_category",
                "dlg_wizard_category_other": "_wizard_category_other",
                "dlg_no_move_forward": "no_move_forward",
            }
            for dlg_k, real_k in _text_map.items():
                ss[real_k] = ss.get(dlg_k, "")
            ss["no_move_forward_reasons"] = ss.get("dlg_no_move_forward_reasons", [])
            st.rerun()

    @st.dialog("Stakeholders", width="large")
    def _dlg_stakeholders():
        SENTINEL_SELECT = "— Select one —"

        # ── My Role ──────────────────────────────────────────────────
        st.header("My Role")

        # Q1: Who's filling out this wizard?
        st.subheader("Who's filling out this wizard?")
        role_opts = [
            SENTINEL_SELECT,
            "I'm a network engineer.",
            "I'm a security engineer.",
            "I'm a software developer.",
            "I manage technical projects or teams.",
            "Other (fill in)",
        ]
        _cur_who = st.session_state.get("my_role_who", SENTINEL_SELECT)
        _idx_who = role_opts.index(_cur_who) if _cur_who in role_opts else 0
        role_choice = st.radio("Select one", role_opts, index=_idx_who, key="dlg_my_role_who")
        if role_choice == "Other (fill in)":
            st.text_input("Please describe", key="dlg_my_role_who_other",
                          value=st.session_state.get("my_role_who_other", ""))

        # Q2: Technical skills
        st.subheader("What best describes your technical skills?")
        skill_opts = [
            SENTINEL_SELECT,
            "I have some scripting skills and basic software development experience.",
            "I am an advanced software developer.",
            "I provide techncial management on network and automation projects.",
            "Other (fill in)",
        ]
        _cur_sk = st.session_state.get("my_role_skills", SENTINEL_SELECT)
        _idx_sk = skill_opts.index(_cur_sk) if _cur_sk in skill_opts else 0
        skill_choice = st.radio("Select one", skill_opts, index=_idx_sk, key="dlg_my_role_skills")
        if skill_choice == "Other (fill in)":
            st.text_input("Please describe", key="dlg_my_role_skills_other",
                          value=st.session_state.get("my_role_skills_other", ""))

        # Q3: Who will develop?
        st.subheader("Who will actually develop the network automation?")
        dev_opts = [
            SENTINEL_SELECT,
            "I'll do it myself.",
            "My in-house team and I will build it.",
            "We will have outside experts build it, but I'll provide technical oversight.",
            "Other (fill in)",
        ]
        _cur_dev = st.session_state.get("my_role_dev", SENTINEL_SELECT)
        _idx_dev = dev_opts.index(_cur_dev) if _cur_dev in dev_opts else 0
        dev_choice = st.radio("Select one", dev_opts, index=_idx_dev, key="dlg_my_role_dev")
        if dev_choice == "Other (fill in)":
            st.text_input("Please describe", key="dlg_my_role_dev_other",
                          value=st.session_state.get("my_role_dev_other", ""))

        # ── Stakeholders ─────────────────────────────────────────────
        st.markdown("---")
        st.header("Stakeholders")

        catalog = _load_stakeholders_catalog()
        existing_choices = st.session_state.get("stakeholders_choices", {})
        stakeholder_help = {
            "Technical Stakeholders": "Select which engineering or operations teams are responsible for building, operating, or securing the systems that this automation will affect.",
            "User and Customer Stakeholders": "Select which internal users or external customers will rely on the outcomes of this automation in their day-to-day work.",
            "Governance and Risk Stakeholders": "Select which governance, security, or risk functions must review, approve, or oversee this automation effort.",
            "Business and Leadership Stakeholders": "Select which business owners, executives, or project leaders are sponsoring, funding, or directing this automation effort.",
            "External/Vendor/Partner Stakeholders": "Select which external vendors, consulting partners, or regulatory bodies are materially involved in delivering, integrating, or approving this automation.",
        }
        _dlg_cat_keys = []  # track generated keys for submit sync
        for cat, opts in (catalog or {}).items():
            if not isinstance(cat, str) or not isinstance(opts, list):
                continue
            st.subheader(cat)
            dlg_key = f"dlg_stakeholders_choice_{_sanitize_title(cat)}"
            _dlg_cat_keys.append((cat, dlg_key, _sanitize_title(cat)))
            select_opts = [SENTINEL_SELECT] + [str(o) for o in opts if str(o).strip()]
            cur_val = existing_choices.get(cat, "") or SENTINEL_SELECT
            if cur_val == "":
                cur_val = SENTINEL_SELECT
            idx = select_opts.index(cur_val) if cur_val in select_opts else 0
            st.selectbox("", options=select_opts, index=idx, key=dlg_key,
                         help=stakeholder_help.get(cat, ""))

        st.subheader("Other")
        st.text_input("Other stakeholder(s)", key="dlg_stakeholders_other_text",
                      value=st.session_state.get("stakeholders_other_text", ""))

        # ── Submit ───────────────────────────────────────────────────
        st.divider()
        if st.button("Submit Stakeholders", type="primary", use_container_width=True):
            ss = st.session_state
            # Sync My Role
            ss["my_role_who"] = ss.get("dlg_my_role_who", SENTINEL_SELECT)
            ss["my_role_who_other"] = ss.get("dlg_my_role_who_other", "")
            ss["my_role_skills"] = ss.get("dlg_my_role_skills", SENTINEL_SELECT)
            ss["my_role_skills_other"] = ss.get("dlg_my_role_skills_other", "")
            ss["my_role_dev"] = ss.get("dlg_my_role_dev", SENTINEL_SELECT)
            ss["my_role_dev_other"] = ss.get("dlg_my_role_dev_other", "")
            # Sync stakeholder categories
            new_choices = {}
            for cat, dlg_key, san_key in _dlg_cat_keys:
                val = ss.get(dlg_key, "") or ""
                real_key = f"stakeholders_choice_{san_key}"
                ss[real_key] = val
                new_choices[cat] = "" if val == SENTINEL_SELECT else val
            ss["stakeholders_choices"] = new_choices
            ss["stakeholders_other_text"] = ss.get("dlg_stakeholders_other_text", "")
            st.rerun()

    @st.dialog("Dependencies & External Interfaces", width="large")
    def _dlg_dependencies():
        ss = st.session_state

        st.caption(
            "Select the external systems this automation will interact with and add details where applicable."
        )

        _dep_defs = [
            {"key": "network_infra", "label": "Network Infrastructure", "default": True, "details": False,
             "help": "The automation will act on some or all of the organization's network infrastructure (switches, appliances, routers, etc.)."},
            {"key": "network_controllers", "label": "Network Controllers", "default": False, "details": True},
            {"key": "revision_control", "label": "Revision Control system", "default": True, "details": True,
             "help": "e.g. GitHub, GitLab, Bitbucket"},
            {"key": "itsm", "label": "ITSM/Change Management System", "default": False, "details": True},
            {"key": "authn", "label": "Authentication System", "default": False, "details": True},
            {"key": "ipams", "label": "IPAMS Systems", "default": False, "details": True},
            {"key": "inventory", "label": "Inventory Systems", "default": False, "details": True,
             "help": "Source of truth/CMDB/inventory (e.g., NetBox, InfraHub, ServiceNow CMDB). What data do you read/write?"},
            {"key": "design_intent", "label": "Design Data/Intent Systems", "default": False, "details": True,
             "help": "Systems holding golden intent or design models (InfraHub, Custom DB)."},
            {"key": "observability", "label": "Observability System", "default": False, "details": True,
             "help": "Telemetry/monitoring/logs/traces (e.g., SuzieQ, Prometheus)."},
            {"key": "vendor_mgmt", "label": "Vendor Tool/Management System", "default": False, "details": True,
             "help": "(e.g., Cisco DNAC, Wireless Controllers, Miraki, Arista CVP, Aruba Central, Juniper Apstra)."},
        ]

        for d in _dep_defs:
            dlg_ck = f"dlg_dep_{d['key']}"
            checked = st.checkbox(
                d["label"], key=dlg_ck,
                value=ss.get(f"dep_{d['key']}", d.get("default", False)),
                help=d.get("help"),
            )
            if checked and d.get("details"):
                default_detail = ""
                if d["key"] == "revision_control":
                    default_detail = "GitHub"
                dlg_dk = f"dlg_dep_{d['key']}_details"
                st.text_input(
                    f"Details for {d['label']}", key=dlg_dk,
                    value=ss.get(f"dep_{d['key']}_details", default_detail),
                )

        # ── Submit ───────────────────────────────────────────────────
        st.divider()
        if st.button("Submit Dependencies", type="primary", use_container_width=True):
            for d in _dep_defs:
                ss[f"dep_{d['key']}"] = ss.get(f"dlg_dep_{d['key']}", False)
                if d.get("details"):
                    ss[f"dep_{d['key']}_details"] = ss.get(f"dlg_dep_{d['key']}_details", "")
            st.rerun()

    @st.dialog("Staffing, Timeline, & Milestones", width="large")
    def _dlg_staffing_timeline():
        ss = st.session_state

        st.caption(
            "Capture a high-level plan with durations in business days. Start date drives scheduled dates."
        )
        st.info(
            "Duration should reflect expected staffing. For example, if a step is 10 business days "
            "of work but two people will work in parallel, you may model it as 5–6 days to allow "
            "for coordination overhead."
        )

        # ── Staffing plan ────────────────────────────────────────────
        st.subheader("Staffing plan")

        _bb_opts = [
            "Build In-House",
            "Build with Professional Services or other external resources (Buy)",
            "Hybrid",
        ]
        _cur_bb = ss.get("timeline_build_buy", "Build In-House")
        _bb_idx = _bb_opts.index(_cur_bb) if _cur_bb in _bb_opts else 0
        st.radio(
            "Development approach", options=_bb_opts, index=_bb_idx,
            key="dlg_timeline_build_buy", horizontal=True,
            help="Select whether this solution will be built in-house, purchased, or a combination.",
        )

        _sc1, _sc2, _sc3 = st.columns([1, 1, 2])
        with _sc1:
            st.number_input(
                "Direct staff on project", min_value=0, step=1,
                value=int(ss.get("timeline_staff_count", 1)),
                key="dlg_timeline_staff_count",
                help="Number of direct employees from your team or from another team in your organization.",
            )
        with _sc2:
            st.number_input(
                "Professional services staff", min_value=0, step=1,
                value=int(ss.get("timeline_external_staff_count", 0)),
                key="dlg_timeline_external_staff_count",
                help="Number of external staff working on project.",
            )
        with _sc3:
            st.text_area(
                "Staffing plan (markdown supported)", height=120,
                key="dlg_timeline_staffing_plan",
                value=str(ss.get("timeline_staffing_plan", "")),
            )

        # ── Holiday calendar ─────────────────────────────────────────
        _region_opts = ["None", "United States", "Canada", "United Kingdom", "Germany", "India", "Australia"]
        _cur_reg = ss.get("timeline_holiday_region", "None")
        _reg_idx = _region_opts.index(_cur_reg) if _cur_reg in _region_opts else 0
        dlg_holiday_region = st.selectbox(
            "Holiday calendar", options=_region_opts, index=_reg_idx,
            key="dlg_timeline_holiday_region",
            help="Used to skip public holidays when computing business days.",
        )

        # ── Start date ───────────────────────────────────────────────
        _def_start = ss.get("timeline_start_date")
        dlg_start_date = st.date_input(
            "Project start date",
            value=_def_start or datetime.datetime.today().date(),
            key="dlg_timeline_start_date_input",
        )

        # ── Milestones ───────────────────────────────────────────────
        st.subheader("Milestones")

        # Working copy of milestones for the dialog
        if "_dlg_timeline_milestones" not in ss:
            default_ms = ss.get("timeline_milestones", [
                {"name": "Planning", "duration": 5, "notes": ""},
                {"name": "Design", "duration": 10, "notes": ""},
                {"name": "Build", "duration": 10, "notes": ""},
                {"name": "Test", "duration": 5, "notes": ""},
                {"name": "Pilot", "duration": 5, "notes": ""},
                {"name": "Production Rollout", "duration": 10, "notes": ""},
            ])
            ss["_dlg_timeline_milestones"] = [dict(m) for m in default_ms]

        _mc1, _mc2 = st.columns([1, 1])
        with _mc1:
            if st.button("Add milestone row", key="dlg_timeline_add_row"):
                ss["_dlg_timeline_milestones"].append({"name": "", "duration": 0, "notes": ""})
                st.rerun()
        with _mc2:
            st.caption("Edit milestone name, duration (business days), and notes.")

        _dlg_to_delete = []
        for idx, row in enumerate(list(ss["_dlg_timeline_milestones"])):
            rcols = st.columns([3, 2, 5, 1])
            with rcols[0]:
                row_name = st.text_input(
                    "Milestone", value=str(row.get("name", "")),
                    key=f"dlg_tl_name_{idx}",
                )
            with rcols[1]:
                row_dur = st.number_input(
                    "Duration (bd)", min_value=0, step=1,
                    value=int(row.get("duration", 0)),
                    key=f"dlg_tl_duration_{idx}",
                )
            with rcols[2]:
                row_notes = st.text_input(
                    "Notes", value=str(row.get("notes", "")),
                    key=f"dlg_tl_notes_{idx}",
                )
            with rcols[3]:
                if st.checkbox("Del", key=f"dlg_tl_del_{idx}"):
                    _dlg_to_delete.append(idx)
            ss["_dlg_timeline_milestones"][idx] = {
                "name": row_name, "duration": int(row_dur), "notes": row_notes,
            }

        for i in sorted(_dlg_to_delete, reverse=True):
            if 0 <= i < len(ss["_dlg_timeline_milestones"]):
                ss["_dlg_timeline_milestones"].pop(i)

        # ── Schedule preview ─────────────────────────────────────────
        def _dlg_build_holiday_set(start_year, years_ahead=2):
            if _hol is None or dlg_holiday_region == "None":
                return set()
            years = list(range(start_year, start_year + max(1, years_ahead) + 1))
            cal = None
            try:
                _region_map = {
                    "United States": _hol.UnitedStates,
                    "Canada": _hol.Canada,
                    "United Kingdom": _hol.UnitedKingdom,
                    "Germany": _hol.Germany,
                    "India": _hol.India,
                    "Australia": _hol.Australia,
                }
                cls = _region_map.get(dlg_holiday_region)
                if cls:
                    cal = cls(years=years)
            except Exception:
                cal = None
            return set(cal.keys()) if cal else set()

        _dlg_schedule = []
        _dlg_cursor = dlg_start_date
        _dlg_hol_set = _dlg_build_holiday_set(dlg_start_date.year, years_ahead=3)
        _dlg_total_bd = 0
        for row in ss["_dlg_timeline_milestones"]:
            name = (row.get("name") or "").strip()
            dur = int(row.get("duration") or 0)
            notes = row.get("notes") or ""
            if not name and dur <= 0:
                continue
            s = _dlg_cursor
            e = _add_business_days(s, dur, _dlg_hol_set) if dur > 0 else s
            _dlg_schedule.append({"name": name or "(Unnamed)", "duration_bd": dur, "start": s, "end": e, "notes": notes})
            _dlg_cursor = e
            _dlg_total_bd += max(0, dur)

        if _dlg_schedule:
            st.markdown("**Timeline summary (business days only)**")
            st.write(
                f"Start: {dlg_start_date.strftime('%Y-%m-%d')} • "
                f"Total: {_dlg_total_bd} bd • "
                f"Projected completion: {_dlg_schedule[-1]['end'].strftime('%Y-%m-%d')}"
            )
            st.success(f"Expected delivery date: {_dlg_schedule[-1]['end'].strftime('%Y-%m-%d')}")
            _m_est = _dlg_total_bd / 21.75 if _dlg_total_bd else 0.0
            st.info(f"Approximate duration: {_m_est:.1f} months ({_m_est/12:.2f} years)")

            st.markdown("**Milestones schedule**")
            for item in _dlg_schedule:
                st.write(f"- {item['name']}: {item['start'].strftime('%Y-%m-%d')} → {item['end'].strftime('%Y-%m-%d')} ({item['duration_bd']} bd)")

            # Gantt chart
            show_chart = st.checkbox("Show Gantt chart", value=True, key="dlg_timeline_show_chart")
            if show_chart:
                df = pd.DataFrame([
                    {"Task": it["name"], "Start": it["start"], "Finish": it["end"], "Duration (bd)": it["duration_bd"]}
                    for it in _dlg_schedule
                ])
                if not df.empty:
                    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Task",
                                      color_discrete_sequence=px.colors.qualitative.Set3)
                    fig.update_yaxes(autorange="reversed")
                    fig.update_layout(height=380, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, width="stretch")
        else:
            st.info("Add at least one milestone to build a timeline.")

        # ── Submit ───────────────────────────────────────────────────
        st.divider()
        if st.button("Submit Staffing & Timeline", type="primary", use_container_width=True):
            ss["timeline_build_buy"] = ss.get("dlg_timeline_build_buy", "Build In-House")
            ss["timeline_staff_count"] = int(ss.get("dlg_timeline_staff_count", 1))
            ss["timeline_external_staff_count"] = int(ss.get("dlg_timeline_external_staff_count", 0))
            ss["timeline_staffing_plan"] = ss.get("dlg_timeline_staffing_plan", "")
            ss["timeline_holiday_region"] = ss.get("dlg_timeline_holiday_region", "None")
            ss["timeline_start_date"] = dlg_start_date
            # Sync milestones
            ss["timeline_milestones"] = [dict(m) for m in ss.get("_dlg_timeline_milestones", [])]
            # Clean up working copy
            ss.pop("_dlg_timeline_milestones", None)
            st.rerun()

    _DIALOGS = {
        "presentation": _dlg_presentation,
        "observability": _dlg_observability,
        "orchestration": _dlg_orchestration,
        "intent": _dlg_intent,
        "collector": _dlg_collector,
        "executor": _dlg_executor,
    }

    @st.fragment
    def _puzzle_fragment():
        """Runs as an independent fragment — reruns here don't re-execute the full page."""
        # Merge: piece is complete if EITHER the demo dialog was submitted
        # OR the real expander section has meaningful data
        _real_state = get_completion_state()
        _merged_state = {
            k: st.session_state["_demo_completed"].get(k, False) or _real_state.get(k, False)
            for k in PUZZLE_SECTIONS
        }

        # Frame completion (context + planning sections)
        _real_frame = get_frame_completion_state()
        _merged_frame = {
            k: st.session_state["_demo_completed"].get(k, False) or _real_frame.get(k, False)
            for k in FRAME_SECTIONS
        }

        # Render clickable puzzle with frame
        render_puzzle_progress(_merged_state, frame_completed=_merged_frame, clickable=True)

        # Section buttons (alternative to clicking puzzle pieces)
        _SECTION_ICONS = {
            "presentation":  "🖥️",
            "observability": "🔍",
            "orchestration": "🔀",
            "intent":        "💎",
            "collector":     "📥",
            "executor":      "⚡",
        }
        st.markdown("#### Click a puzzle piece or button to fill out its form:")
        _btn_row1 = st.columns(3)
        for i, key in enumerate(["presentation", "observability", "orchestration"]):
            with _btn_row1[i]:
                _done = _merged_state[key]
                _icon = "✅" if _done else _SECTION_ICONS[key]
                if st.button(
                    f"{_icon} {PUZZLE_SECTIONS[key]['label']}",
                    key=f"open_{key}",
                    use_container_width=True,
                ):
                    _DIALOGS[key]()

        _btn_row2 = st.columns(3)
        for i, key in enumerate(["intent", "collector", "executor"]):
            with _btn_row2[i]:
                _done = _merged_state[key]
                _icon = "✅" if _done else _SECTION_ICONS[key]
                if st.button(
                    f"{_icon} {PUZZLE_SECTIONS[key]['label']}",
                    key=f"open_{key}",
                    use_container_width=True,
                ):
                    _DIALOGS[key]()

    _puzzle_fragment()

    # ── Project Context & Planning button cards ──────────────────────
    # Compute frame completion for button icons
    _real_frame = get_frame_completion_state()
    _demo = st.session_state.get("_demo_completed", {})
    _frame_done = {
        k: _demo.get(k, False) or _real_frame.get(k, False)
        for k in FRAME_SECTIONS
    }

    st.markdown("")  # spacer
    col_ctx, col_plan = st.columns(2)

    with col_ctx:
        st.markdown(
            """<div style="border:1px solid #444; border-radius:8px; padding:12px 16px 8px;">
            <span style="font-size:0.75em; font-weight:600; color:#4CAF50;">● RECOMMENDED</span>
            <h4 style="margin:4px 0 8px;">Project Context</h4>
            <p style="font-size:0.85em; margin:0 0 4px; opacity:0.8;">Define the problem you're solving, who's involved, and why this automation matters. This context shapes every decision downstream.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        _ctx_c1, _ctx_c2 = st.columns(2)
        with _ctx_c1:
            _ic = "✅" if _frame_done["problem_statement"] else "📋"
            if st.button(f"{_ic} Problem Statement", key="btn_problem_stmt", use_container_width=True):
                _dlg_problem_statement()
        with _ctx_c2:
            _ic = "✅" if _frame_done["stakeholders"] else "👥"
            if st.button(f"{_ic} Stakeholders", key="btn_stakeholders", use_container_width=True):
                _dlg_stakeholders()

    with col_plan:
        st.markdown(
            """<div style="border:1px solid #444; border-radius:8px; padding:12px 16px 8px;">
            <span style="font-size:0.75em; font-weight:600; color:#888;">○ OPTIONAL</span>
            <h4 style="margin:4px 0 8px;">Planning</h4>
            <p style="font-size:0.85em; margin:0 0 4px; opacity:0.8;">While the framework helps you think about the technical implementation, for a complete project let's now consider external interfaces, staffing, and timelines.</p>
            </div>""",
            unsafe_allow_html=True,
        )
        _pln_c1, _pln_c2 = st.columns(2)
        with _pln_c1:
            _ic = "✅" if _frame_done["dependencies"] else "🔗"
            if st.button(f"{_ic} Dependencies", key="btn_dependencies", use_container_width=True):
                _dlg_dependencies()
        with _pln_c2:
            _ic = "✅" if _frame_done["staffing_timeline"] else "📅"
            if st.button(f"{_ic} Staffing & Timeline", key="btn_staffing", use_container_width=True):
                _dlg_staffing_timeline()

    # ── Reset All Sections ───────────────────────────────────────────
    _r1, _r2, _r3 = st.columns([2, 1, 2])
    with _r2:
        if st.button("🔄 Reset All Sections", use_container_width=True, key="wizard_reset_defaults_btn"):
            # Set all boolean-prefixed keys to False
            _bool_prefixes = (
                "pres_user_", "pres_tool_", "pres_interact_", "pres_auth_",
                "obs_state_", "obs_tool_",
                "intent_dev_", "intent_prov_",
                "collector_method_", "collector_auth_", "collector_handle_",
                "collector_norm_", "collection_tool_",
                "exec_", "dep_",
                "dlg_pres_", "dlg_obs_", "dlg_intent_", "dlg_collector_",
                "dlg_exec_", "dlg_orch_", "dlg_my_role_", "dlg_stakeholders_",
                "dlg_wizard_", "dlg_no_move_forward", "dlg_dep_",
                "dlg_timeline_", "dlg_tl_",
            )
            for k in list(st.session_state.keys()):
                if k.startswith(_bool_prefixes):
                    # Detail keys are strings, not booleans
                    if "_details" in k or k.endswith("_other") or k.endswith("_text") or k.endswith("_custom"):
                        st.session_state[k] = ""
                    else:
                        st.session_state[k] = False
            # Clear string keys
            _str_keys = (
                "obs_go_no_go", "obs_add_logic_choice", "obs_add_logic_text",
                "orch_details_text",
                "collector_devices", "collector_metrics", "collector_cadence",
                "pres_user_custom", "pres_interact_custom", "pres_tool_custom",
                "pres_auth_other_text",
                "intent_dev_custom", "intent_prov_custom",
                "stakeholders_other_text", "no_move_forward",
                "my_role_who_other", "my_role_skills_other", "my_role_dev_other",
            )
            for k in _str_keys:
                if k in st.session_state:
                    st.session_state[k] = ""
            # Reset sentinels
            st.session_state["orch_choice"] = "— Select one —"
            for k in ("my_role_who", "my_role_skills", "my_role_dev"):
                st.session_state[k] = "— Select one —"
            st.session_state["stakeholders_choices"] = {}
            # Reset puzzle tracking
            st.session_state["_demo_completed"] = {
                **{key: False for key in PUZZLE_SECTIONS},
                **{key: False for key in FRAME_SECTIONS},
            }
            st.session_state.pop("_dlg_timeline_milestones", None)
            # Initiative defaults
            st.session_state["_wizard_automation_title"] = "My new network automation project"
            st.session_state["_wizard_automation_description"] = "Here is a short description of my my new network automation project"
            st.session_state["_wizard_problem_statement"] = ""
            st.session_state["_wizard_expected_use"] = "This automation will be used whenever this task needs to be executed."
            st.session_state["_wizard_error_conditions"] = ""
            st.session_state["_wizard_assumptions"] = ""
            st.session_state["_wizard_deployment_strategy"] = ""
            st.session_state["_wizard_deployment_strategy_other"] = ""
            st.session_state["_wizard_deployment_strategy_description"] = ""
            st.session_state["_wizard_out_of_scope"] = ""
            st.session_state["_wizard_category"] = ""
            st.session_state["_wizard_category_other"] = ""
            st.session_state["no_move_forward_reasons"] = []
            # Reset timeline/staffing
            for k in ("timeline_build_buy", "timeline_staff_count", "timeline_external_staff_count",
                       "timeline_staffing_plan", "timeline_holiday_region", "timeline_start_date",
                       "timeline_milestones"):
                st.session_state.pop(k, None)
            st.rerun()

    st.divider()

    # ──────────────────────────────────────────────────────────────────
    # Session-state defaults (previously inside expanders)
    # ──────────────────────────────────────────────────────────────────
    if "_wizard_author" not in st.session_state:
        try:
            st.session_state["_wizard_author"] = getpass.getuser()
        except Exception:
            st.session_state["_wizard_author"] = os.environ.get("USER", os.environ.get("USERNAME", "System User"))
    if "_wizard_automation_title" not in st.session_state:
        st.session_state["_wizard_automation_title"] = "My new network automation project"
    if "_wizard_automation_description" not in st.session_state:
        st.session_state["_wizard_automation_description"] = "Here is a short description of my my new network automation project"
    if "_wizard_problem_statement" not in st.session_state:
        st.session_state["_wizard_problem_statement"] = ""
    if "_wizard_expected_use" not in st.session_state:
        st.session_state["_wizard_expected_use"] = "This automation will be used whenever this task needs to be executed."
    if "_wizard_error_conditions" not in st.session_state:
        st.session_state["_wizard_error_conditions"] = ""
    if "_wizard_assumptions" not in st.session_state:
        st.session_state["_wizard_assumptions"] = ""
    if "_wizard_deployment_strategy" not in st.session_state:
        st.session_state["_wizard_deployment_strategy"] = ""
    if "_wizard_deployment_strategy_other" not in st.session_state:
        st.session_state["_wizard_deployment_strategy_other"] = ""
    if "_wizard_deployment_strategy_description" not in st.session_state:
        st.session_state["_wizard_deployment_strategy_description"] = ""
    if "_wizard_out_of_scope" not in st.session_state:
        st.session_state["_wizard_out_of_scope"] = ""
    if "_wizard_category" not in st.session_state:
        st.session_state["_wizard_category"] = ""
    if "_wizard_category_other" not in st.session_state:
        st.session_state["_wizard_category_other"] = ""
    if "no_move_forward" not in st.session_state:
        st.session_state["no_move_forward"] = ""
    if "my_role_who" not in st.session_state:
        st.session_state["my_role_who"] = "— Select one —"
    if "my_role_skills" not in st.session_state:
        st.session_state["my_role_skills"] = "— Select one —"
    if "my_role_dev" not in st.session_state:
        st.session_state["my_role_dev"] = "— Select one —"
    if "stakeholders_choices" not in st.session_state or not isinstance(st.session_state.get("stakeholders_choices"), dict):
        st.session_state["stakeholders_choices"] = {}
    if "stakeholders_other_text" not in st.session_state:
        st.session_state["stakeholders_other_text"] = ""
    if "orch_choice" not in st.session_state:
        st.session_state["orch_choice"] = "— Select one —"
    if "timeline_build_buy" not in st.session_state:
        st.session_state["timeline_build_buy"] = "Build In-House"
    if "timeline_milestones" not in st.session_state:
        st.session_state["timeline_milestones"] = [
            {"name": "Planning", "duration": 5, "notes": ""},
            {"name": "Design", "duration": 10, "notes": ""},
            {"name": "Build", "duration": 10, "notes": ""},
            {"name": "Test", "duration": 5, "notes": ""},
            {"name": "Pilot", "duration": 5, "notes": ""},
            {"name": "Production Rollout", "duration": 10, "notes": ""},
        ]

    # ──────────────────────────────────────────────────────────────────
    # Build payload from session state (replaces all expander-embedded payload blocks)
    # ──────────────────────────────────────────────────────────────────
    payload = build_payload_from_state(st.session_state)

    # REMOVED: All form expanders (Problem Statement, Stakeholders, Presentation,
    # Intent, Observability, Orchestration, Collector, Executor, Dependencies,
    # Staffing/Timeline). Forms are now accessed exclusively via dialogs above.
    # Determine if there is meaningful content across sections
    any_content = _has_any_content(payload)
    # Fallback: if the user has selected an orchestration choice (including 'No') via session_state,
    # treat that as meaningful content to enable export even before other narratives populate.
    try:
        _orch_choice_ss = (st.session_state.get("orch_choice") or "").strip()
        if _orch_choice_ss and _orch_choice_ss != "— Select one —":
            any_content = True
    except Exception:
        pass

    # Dependencies: do not render immediately on the main page; include only in the generated summary
    deps = payload.get("dependencies", [])
    if deps:
        deps_slim = [
            {
                "name": (d or {}).get("name"),
                "details": (d or {}).get("details", "").strip(),
            }
            for d in deps
            if (d or {}).get("name")
        ]
        default_deps = [
            {"name": "Network Infrastructure", "details": ""},
            {"name": "Revision Control system", "details": "GitHub"},
        ]

        looks_default_deps = _sorted_deps(deps_slim) == _sorted_deps(default_deps)
        if not looks_default_deps:
            any_content = True

    if not any_content:
        # Use same gate as sidebar to decide whether to show the reminder
        sel = {
            "pres": (payload.get("presentation", {}) or {}).get("selections", {}),
            "intent": (payload.get("intent", {}) or {}).get("selections", {}),
            "obs": (payload.get("observability", {}) or {}).get("selections", {}),
            "orch": (payload.get("orchestration", {}) or {}).get("selections", {}),
            "coll": (payload.get("collector", {}) or {}).get("selections", {}),
            "exec": (payload.get("executor", {}) or {}).get("selections", {}),
        }

        has_any_selection = any(_has_list_selections(v) for v in sel.values())
        role_nonempty = any(
            ((payload.get("my_role", {}) or {}).get(k) or "").strip()
            for k in ("who", "skills", "developer")
        )
        ini = payload.get("initiative", {}) or {}
        default_title = DEFAULT_TITLE
        default_desc = DEFAULT_DESCRIPTION
        _title = (ini.get("title") or "").strip()
        _desc = (ini.get("description") or "").strip()
        ini_nondefault = bool(
            (_title and _title != default_title) or (_desc and _desc != default_desc)
        )
        orch_sel = (payload.get("orchestration", {}) or {}).get("selections", {}) or {}
        orch_choice = (orch_sel.get("choice") or "").strip() or (
            st.session_state.get("orch_choice") or ""
        ).strip()
        orch_details = (orch_sel.get("details") or "").strip()
        # Treat any non-sentinel choice (including 'No') as a meaningful change for gating
        orch_nondefault = bool(orch_choice and orch_choice != "— Select one —")
        if not (
            has_any_selection or ini_nondefault or orch_nondefault or role_nonempty
        ):
            st.info(
                "Start filling in the sections above to see Solution Highlights here. Once you provide inputs, you will also be able to download the Wizard JSON."
            )

    # Markdown summary builder & export — only when there is meaningful content
    if any_content:
        # Build a concise markdown summary from current payload
        summary_parts = []
        # My Role (show if any field present)
        my_role = payload.get("my_role", {}) or {}
        role_lines = []
        if (my_role.get("who") or "").strip():
            role_lines.append(f"- Who: {my_role.get('who')}")
        if (my_role.get("skills") or "").strip():
            role_lines.append(f"- Skills: {my_role.get('skills')}")
        if (my_role.get("developer") or "").strip():
            role_lines.append(f"- Developer: {my_role.get('developer')}")
        summary_parts.append(_section_md("My Role", role_lines))
        # Initiative (suppress known defaults)
        ini = payload.get("initiative", {})
        ini_lines = []
        default_title = DEFAULT_TITLE
        default_desc = DEFAULT_DESCRIPTION
        _title = (ini.get("title") or "").strip()
        _desc = (ini.get("description") or "").strip()
        _out = (ini.get("out_of_scope") or "").strip()
        if _title and _title != default_title:
            ini_lines.append(f"- Title: {_title}")
        if _desc and _desc != default_desc:
            ini_lines.append(f"- Scope: {_desc}")
        if _out:
            ini_lines.append(f"- Out of scope: {_out}")
        # If details_md exists, we keep it for the export doc, but don't render here to avoid duplication
        summary_parts.append(_section_md("Initiative", ini_lines))

        # Presentation
        pres = payload.get("presentation", {})
        pres_lines = []
        for k in ("users", "interaction", "tools", "auth"):
            v = pres.get(k)
            if v and is_meaningful(v):
                pres_lines.append(f"- {v}")
        summary_parts.append(_section_md("Presentation", pres_lines))

        # Intent
        intent = payload.get("intent", {})
        intent_lines = []
        for k in ("development", "provided"):
            v = intent.get(k)
            if v and is_meaningful(v):
                intent_lines.append(f"- {v}")
        summary_parts.append(_section_md("Intent", intent_lines))

        # Observability
        obs = payload.get("observability", {})
        obs_lines = []
        for k in ("methods", "go_no_go", "additional_logic", "tools"):
            v = obs.get(k)
            if v and is_meaningful(v):
                obs_lines.append(f"- {v}")
        summary_parts.append(_section_md("Observability", obs_lines))

        # Orchestration
        orch = payload.get("orchestration", {})
        orch_lines = []
        v = orch.get("summary")
        if v and is_meaningful(v):
            orch_lines.append(f"- {v}")
        summary_parts.append(_section_md("Orchestration", orch_lines))

        # Collector
        collector = payload.get("collector", {})
        col_lines = []
        for k in ("methods", "auth", "handling", "normalization", "scale", "tools"):
            v = collector.get(k)
            if v and is_meaningful(v):
                col_lines.append(f"- {v}")
        summary_parts.append(_section_md("Collector", col_lines))

        # Executor
        executor = payload.get("executor", {})
        exe_lines = []
        v = executor.get("methods")
        if v and is_meaningful(v):
            exe_lines.append(f"- {v}")
        summary_parts.append(_section_md("Executor", exe_lines))

        # Dependencies (suppress default pair)
        deps = payload.get("dependencies", [])
        dep_lines = []
        if deps:
            deps_slim = [
                {
                    "name": (d or {}).get("name"),
                    "details": (d or {}).get("details", "").strip(),
                }
                for d in deps
                if (d or {}).get("name")
            ]
            default_deps = [
                {"name": "Network Infrastructure", "details": ""},
                {"name": "Revision Control system", "details": "GitHub"},
            ]

            if _sorted_deps(deps_slim) != _sorted_deps(default_deps):
                for d in deps_slim:
                    name = d.get("name")
                    details = d.get("details")
                    if name:
                        dep_lines.append(
                            f"- {name}{(': ' + details) if details else ''}"
                        )
        summary_parts.append(
            _section_md("Dependencies & External Interfaces", dep_lines)
        )

        # Timeline (only when there are milestone items or staffing plan text)
        tl = payload.get("timeline", {})
        tl_lines = []
        items = tl.get("items") or []
        tl_staff_md = (tl.get("staffing_plan_md") or "").strip()
        if items:
            staff_ct = tl.get("staff_count")
            start = tl.get("start_date")
            end = tl.get("projected_completion")
            total_bd = tl.get("total_business_days")
            tl_lines.append(
                f"- Staff {staff_ct if staff_ct is not None else 'TBD'} • Start {start or 'TBD'} • Total {total_bd if total_bd is not None else 'TBD'} bd • Completion {end or 'TBD'}"
            )
            for i in items[:15]:
                tl_lines.append(
                    f"  - {i.get('name')}: {i.get('start')} → {i.get('end')} ({i.get('duration_bd')} bd)"
                )
            summary_parts.append(
                _section_md("Staffing, Timeline, & Milestones", tl_lines)
            )
        if tl_staff_md:
            summary_parts.append("\n## Staffing Plan\n")
            summary_parts.append(tl_staff_md + "\n")

        summary_md = ("".join(summary_parts)).strip()
        if summary_md:
            with st.expander("Detailed solution description (Preview)", expanded=False):
                """
                Live preview of the report that will be written into the ZIP (naf_report_*.md).
                """
                st.caption(
                    "Preview of the full report that will be included in the download (images removed for preview)."
                )
                
                # Render the Jinja template for preview
                template_preview = _render_template_preview(payload, summary_md)
                st.markdown(template_preview)

    if any_content:
        # Build a comprehensive payload including defaults for any missing sections
        final_payload = dict(payload)
        final_payload = dict(payload) if isinstance(payload, dict) else {}
        # Ensure initiative exists (without solution_details_md)
        if "initiative" not in final_payload or not isinstance(
            final_payload.get("initiative"), dict
        ):
            final_payload["initiative"] = {}

        # Defaults for sections
        if "my_role" not in final_payload:
            final_payload["my_role"] = {"who": "", "skills": "", "developer": ""}
        if "presentation" not in final_payload:
            final_payload["presentation"] = {
                "users": "",
                "interaction": "",
                "tools": "",
                "auth": "",
                "selections": {
                    "users": [],
                    "interactions": [],
                    "tools": [],
                    "auth": [],
                },
            }

        if "intent" not in final_payload:
            final_payload["intent"] = {
                "development": "",
                "provided": "",
                "selections": {
                    "development": [],
                    "provided": [],
                },
            }

        if "observability" not in final_payload:
            final_payload["observability"] = {
                "methods": "",
                "go_no_go": "",
                "additional_logic": "",
                "tools": "",
                "selections": {
                    "methods": [],
                    "go_no_go_text": "",
                    "additional_logic_enabled": False,
                    "additional_logic_text": "",
                    "tools": [],
                },
            }

        if "orchestration" not in final_payload:
            final_payload["orchestration"] = {
                "summary": "",
                "selections": {
                    "choice": "No",
                    "details": "",
                },
            }

        if "executor" not in final_payload:
            final_payload["executor"] = {
                "methods": "",
                "selections": {"methods": []},
            }

        if "collector" not in final_payload:
            final_payload["collector"] = {
                "methods": "",
                "auth": "",
                "handling": "",
                "normalization": "",
                "scale": "",
                "tools": "",
                "selections": {
                    "methods": [],
                    "auth": [],
                    "handling": [],
                    "normalization": [],
                    "devices": "",
                    "metrics_per_sec": "",
                    "cadence": "",
                    "tools": [],
                },
            }

        if "dependencies" not in final_payload:
            final_payload["dependencies"] = [
                {"name": "Network Infrastructure", "details": ""},
                {"name": "Revision Control system", "details": "GitHub"},
            ]

        if "timeline" not in final_payload:
            # Construct a default timeline with computed dates (weekdays only, no holidays)
            start = datetime.datetime.today().date()
            default_items = [
                {"name": "Planning", "duration_bd": 5, "notes": ""},
                {"name": "Design", "duration_bd": 10, "notes": ""},
                {"name": "Build", "duration_bd": 10, "notes": ""},
                {"name": "Test", "duration_bd": 5, "notes": ""},
                {"name": "Pilot", "duration_bd": 5, "notes": ""},
                {"name": "Production Rollout", "duration_bd": 10, "notes": ""},
            ]
            cursor = start
            schedule = []
            total_bd = 0
            for it in default_items:
                dur = int(it["duration_bd"])
                s = cursor
                e = _add_business_days(s, dur) if dur > 0 else s
                schedule.append(
                    {
                        "name": it["name"],
                        "duration_bd": dur,
                        "start": s.strftime("%Y-%m-%d"),
                        "end": e.strftime("%Y-%m-%d"),
                        "notes": it.get("notes", ""),
                    }
                )
                cursor = e
                total_bd += max(0, dur)

            final_payload["timeline"] = {
                "start_date": start.strftime("%Y-%m-%d"),
                "total_business_days": total_bd,
                "projected_completion": cursor.strftime("%Y-%m-%d"),
                "staff_count": 1,
                "holiday_region": "None",
                "items": schedule,
            }

        sdd_template_env = None
        sdd_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            templates_dir = (Path(__file__).parent.parent / "templates").resolve()
            env = Environment(
                loader=FileSystemLoader(str(templates_dir)),
                autoescape=False,
            )
            tmpl = env.get_template("Solution_Design_Report.j2")
            context = {
                "generated_timestamp": sdd_ts,
                "highlights": summary_md,
                "initiative": final_payload.get("initiative", {}),
                "my_role": final_payload.get("my_role", {}),
                "stakeholders": final_payload.get("stakeholders", {}),
                "presentation": final_payload.get("presentation", {}),
                "intent": final_payload.get("intent", {}),
                "observability": final_payload.get("observability", {}),
                "orchestration": final_payload.get("orchestration", {}),
                "collector": final_payload.get("collector", {}),
                "executor": final_payload.get("executor", {}),
                "dependencies": final_payload.get("dependencies", []),
                "timeline": final_payload.get("timeline", {}),
                "staffing_plan": (final_payload.get("timeline", {}) or {}).get(
                    "staffing_plan_md", ""
                ),
                "gantt_image_path": None,
            }
            sdd_template_env = (env, tmpl, context)
        except Exception:
            # Fallback minimal doc if template can't be loaded
            basic_doc = ["# Solution Design Document", f"Generated: {sdd_ts}"]
            if (summary_md or "").strip():
                basic_doc.append("## Highlights")
                basic_doc.append(summary_md)
            sdd_doc_md = "\n\n".join(basic_doc).encode("utf-8")

        # Rebuild a color Gantt chart from payload timeline
        gantt_png_bytes = None
        gantt_html_bytes = None
        try:
            tl = final_payload.get("timeline", {})
            rows = []
            for it in (tl.get("items") or [])[:100]:
                rows.append(
                    {
                        "Task": it.get("name", "Task"),
                        "Start": it.get("start"),
                        "Finish": it.get("end"),
                    }
                )
            if rows:
                df = pd.DataFrame(rows)
                fig = px.timeline(
                    df,
                    x_start="Start",
                    x_end="Finish",
                    y="Task",
                    color="Task",
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig.update_yaxes(autorange="reversed")
                # Try PNG first (requires kaleido)
                try:
                    gantt_png_bytes = fig.to_image(format="png", scale=2)
                except Exception:
                    gantt_png_bytes = None
                # Always prepare HTML fallback
                gantt_html_bytes = fig.to_html(
                    full_html=True, include_plotlyjs="cdn"
                ).encode("utf-8")
        except Exception:
            pass

        # Inform the user when PNG export failed (typically missing kaleido)
        try:
            has_rows = bool(rows)
        except Exception:
            has_rows = False
        if has_rows and gantt_png_bytes is None:
            st.info(
                "Gantt PNG could not be generated. To include a PNG in the ZIP, install the 'kaleido' package (e.g., pip install -U kaleido) and rerun."
            )

        # Define title for ZIP filenames
        ini = final_payload.get("initiative", {}) or {}
        _title = (ini.get("title") or "").strip()
        title_for_zip = (
            re.sub(r"[^A-Za-z0-9_-]+", "_", (_title or "solution")).strip("_")
            or "solution"
        )
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create JSON bytes for ZIP
        final_json_bytes = json.dumps(final_payload, indent=2).encode("utf-8")

        # Define ZIP filename
        zip_name = f"naf_report_{title_for_zip}_{ts}.zip"

        # Create ZIP in-memory
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            json_name = f"naf_report_{title_for_zip}_{ts}.json"
            md_name = f"naf_report_{title_for_zip}_{ts}.md"
            zf.writestr(json_name, final_json_bytes)
            # Write markdown after potential Gantt generation so template can reference image name
            try:
                env, tmpl, context = sdd_template_env  # type: ignore
                # Update gantt_image_path based on actual artifact (store under images/)
                context["gantt_image_path"] = (
                    "images/Gantt.png" if gantt_png_bytes else None
                )
                rendered = tmpl.render(**context)
                sdd_doc_md = rendered.encode("utf-8")
                # Safety: if render produced empty/whitespace, write a minimal doc
                if not (sdd_doc_md or b"").strip():
                    basic_doc = ["# Solution Design Document", f"Generated: {sdd_ts}"]
                    _hl = (context.get("highlights") or "").strip()
                    if _hl:
                        basic_doc.append("## Highlights")
                        basic_doc.append(_hl)
                    sdd_doc_md = ("\n\n".join(basic_doc)).encode("utf-8")
            except Exception:
                # If earlier fallback created sdd_doc_md, use it; else create a minimal fallback now
                if "sdd_doc_md" not in locals():
                    sdd_doc_md = (
                        "# Solution Design Document\n\n" + f"Generated: {sdd_ts}"
                    ).encode("utf-8")
            zf.writestr(md_name, sdd_doc_md)
            if gantt_png_bytes:
                zf.writestr("images/Gantt.png", gantt_png_bytes)
            elif gantt_html_bytes:
                # Provide an HTML fallback if PNG isn't available (no kaleido)
                zf.writestr("Gantt.html", gantt_html_bytes)

            # Include branding icon if available so Markdown image resolves
            try:
                icon_path = (
                    Path(__file__).parent.parent / "images" / "naf_icon.png"
                ).resolve()
                if icon_path.exists():
                    with open(icon_path, "rb") as f:
                        zf.writestr("images/naf_icon.png", f.read())
            except Exception:
                pass

        zip_bytes = zip_buf.getvalue()
        # Export (single ZIP download) only when summary has meaningful content
        # and at least one selection array is non-empty (to avoid pure-default narratives)
        sel = {
            "pres": (payload.get("presentation", {}) or {}).get("selections", {}),
            "intent": (payload.get("intent", {}) or {}).get("selections", {}),
            "obs": (payload.get("observability", {}) or {}).get("selections", {}),
            "orch": (payload.get("orchestration", {}) or {}).get("selections", {}),
            "coll": (payload.get("collector", {}) or {}).get("selections", {}),
            "exec": (payload.get("executor", {}) or {}).get("selections", {}),
        }
        role_nonempty = any(
            ((payload.get("my_role", {}) or {}).get(k) or "").strip()
            for k in ("who", "skills", "developer")
        )

        has_any_selection = (
            any(_has_list_selections(v) for v in sel.values()) or role_nonempty
        )
        ini = payload.get("initiative", {}) or {}
        default_title = DEFAULT_TITLE
        default_desc = DEFAULT_DESCRIPTION
        _title = (ini.get("title") or "").strip()
        _desc = (ini.get("description") or "").strip()
        ini_nondefault = bool(
            (_title and _title != default_title) or (_desc and _desc != default_desc)
        )
        orch_sel = (payload.get("orchestration", {}) or {}).get("selections", {}) or {}
        orch_choice = (orch_sel.get("choice") or "").strip() or (
            st.session_state.get("orch_choice") or ""
        ).strip()
        orch_details = (orch_sel.get("details") or "").strip()
        # Treat any non-sentinel choice (including 'No') as a meaningful change for gating
        orch_nondefault = bool(orch_choice and orch_choice != "— Select one —")
        if has_any_selection or ini_nondefault or orch_nondefault or role_nonempty:
            with st.expander("Save Solution Artifacts", expanded=True):
                st.caption("Download your current scenario (JSON + Markdown + Gantt)")
                st.download_button(
                    label="📦 Download (JSON + Markdown + Gantt)",
                    data=zip_bytes,
                    file_name=zip_name,
                    mime="application/zip",
                    use_container_width=True,
                    key="wizard_zip_download_btn",
                )
        else:
            with st.expander("Save Solution Artifacts", expanded=False):
                st.info(
                    "Start filling in the sections above to see Solution Highlights here. Once you provide inputs, you will also be able to download the Wizard JSON."
                )
    else:
        # Build a minimal ZIP when a non-sentinel Orchestration choice exists, even if summary is empty
        sel = {
            "pres": (payload.get("presentation", {}) or {}).get("selections", {}),
            "intent": (payload.get("intent", {}) or {}).get("selections", {}),
            "obs": (payload.get("observability", {}) or {}).get("selections", {}),
            "orch": (payload.get("orchestration", {}) or {}).get("selections", {}),
            "coll": (payload.get("collector", {}) or {}).get("selections", {}),
            "exec": (payload.get("executor", {}) or {}).get("selections", {}),
        }

        has_any_selection = any(_has_list_selections(v) for v in sel.values())
        role_nonempty = any(
            ((payload.get("my_role", {}) or {}).get(k) or "").strip()
            for k in ("who", "skills", "developer")
        )
        ini = payload.get("initiative", {}) or {}
        default_title = DEFAULT_TITLE
        default_desc = DEFAULT_DESCRIPTION
        _title = (ini.get("title") or "").strip()
        _desc = (ini.get("description") or "").strip()
        ini_nondefault = bool(
            (_title and _title != default_title) or (_desc and _desc != default_desc)
        )
        orch_sel = (payload.get("orchestration", {}) or {}).get("selections", {}) or {}
        orch_choice = (orch_sel.get("choice") or "").strip() or (
            st.session_state.get("orch_choice") or ""
        ).strip()
        orch_nondefault = bool(orch_choice and orch_choice != "— Select one —")
        if orch_nondefault and not (
            has_any_selection or ini_nondefault or role_nonempty
        ):
            # Minimal payload & ZIP (JSON + minimal MD)
            final_payload = dict(payload) if isinstance(payload, dict) else {}
            if "initiative" not in final_payload or not isinstance(
                final_payload.get("initiative"), dict
            ):
                final_payload["initiative"] = {}
            final_payload_bytes = json.dumps(final_payload, indent=2).encode("utf-8")

            # Define title for ZIP filenames
            ini = final_payload.get("initiative", {}) or {}
            _title = (ini.get("title") or "").strip()
            title_for_zip = (
                re.sub(r"[^A-Za-z0-9_-]+", "_", (_title or "solution")).strip("_")
                or "solution"
            )
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Define ZIP filename for minimal payload path
            zip_name = f"naf_report_{title_for_zip}_{ts}.zip"

            zip_buf = io.BytesIO()
            with zipfile.ZipFile(
                zip_buf, mode="w", compression=zipfile.ZIP_DEFLATED
            ) as zf:
                # Enforce naf_report_ prefix for artifacts
                zf.writestr(
                    f"naf_report_{title_for_zip}_{ts}.json", final_payload_bytes
                )
                zf.writestr(
                    f"naf_report_{title_for_zip}_{ts}.md",
                    ("# Solution Design Document\n\n").encode("utf-8"),
                )
                # Include branding icon if available in minimal ZIP as well
                try:
                    icon_path = (
                        Path(__file__).parent.parent / "images" / "naf_icon.png"
                    ).resolve()
                    if icon_path.exists():
                        with open(icon_path, "rb") as f:
                            zf.writestr("images/naf_icon.png", f.read())
                except Exception:
                    pass
            zip_bytes = zip_buf.getvalue()
            with st.expander("Save Solution Artifacts", expanded=True):
                st.caption("Download your current scenario (JSON + Markdown + Gantt)")
                st.download_button(
                    label="📦 Download (JSON + Markdown + Gantt)",
                    data=zip_bytes,
                    file_name=zip_name,
                    mime="application/zip",
                    use_container_width=True,
                    key="wizard_zip_download_btn",
                )
        else:
            # Reminder when no content yet
            with st.expander("Save Solution Artifacts", expanded=False):
                st.info(
                    "Start filling in the sections above to see Solution Highlights here. Once you provide inputs, you will also be able to download the Wizard JSON."
                )

    # Diagram removed per request; SDD export available above.


# Run the wizard when this page is loaded by Streamlit
solution_wizard_main()
