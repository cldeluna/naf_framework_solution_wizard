"""
payload_builder.py
==================
Standalone module that reconstructs the full NAF Solution Wizard payload dict
from a Streamlit session_state (or any dict-like object).

Usage::

    from payload_builder import build_payload_from_state
    payload = build_payload_from_state(st.session_state)

This replaces all the inline ``payload[...]`` blocks that were previously
embedded inside expander sections of the wizard page.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, Optional, Set

import utils  # provides utils.join_human

# Optional holidays library — gracefully absent
try:
    import holidays as _hol
except ImportError:
    _hol = None


# ---------------------------------------------------------------------------
# Private helpers (mirrors of the functions defined in the wizard page)
# ---------------------------------------------------------------------------

SENTINEL_SELECT = "— Select one —"


def _norm_role_choice(choice: str, other: str, sentinel: str = SENTINEL_SELECT) -> str:
    """Normalize a role radio choice, handling 'Other' and sentinel values."""
    if choice == "Other (fill in)":
        return (other or "").strip()
    if choice == sentinel:
        return ""
    return choice or ""


def _add_business_days(
    d: datetime.date, n: int, holiday_set: Optional[Set[datetime.date]] = None
) -> datetime.date:
    """Add *n* business days (Mon-Fri) to date *d*, optionally skipping holidays."""
    days = int(n or 0)
    cur = d
    while days > 0:
        cur = cur + datetime.timedelta(days=1)
        if cur.weekday() < 5 and (holiday_set is None or cur not in holiday_set):
            days -= 1
    return cur


def _build_holiday_set(
    holiday_region: str, start_year: int, years_ahead: int = 2
) -> Set[datetime.date]:
    """Build a set of holiday dates for the given region and year range."""
    if _hol is None or holiday_region == "None":
        return set()
    years = list(range(start_year, start_year + max(1, years_ahead) + 1))
    cal = None
    try:
        if holiday_region == "United States":
            cal = _hol.UnitedStates(years=years)
        elif holiday_region == "Canada":
            cal = _hol.Canada(years=years)
        elif holiday_region == "United Kingdom":
            cal = _hol.UnitedKingdom(years=years)
        elif holiday_region == "Germany":
            cal = _hol.Germany(years=years)
        elif holiday_region == "India":
            cal = _hol.India(years=years)
        elif holiday_region == "Australia":
            cal = _hol.Australia(years=years)
    except Exception:
        cal = None
    return set(cal.keys()) if cal else set()


# Alias for internal use — matches the wizard page's import alias
_join = utils.join_human


# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def build_payload_from_state(ss: Dict[str, Any]) -> dict:
    """Reconstruct the full wizard payload from session_state.

    Parameters
    ----------
    ss:
        A dict-like object (e.g. ``st.session_state``) containing all wizard
        keys.

    Returns
    -------
    dict
        Complete payload with keys: initiative, my_role, stakeholders,
        presentation, intent, observability, orchestration, collector,
        executor, dependencies, timeline.
    """
    payload: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # initiative
    # ------------------------------------------------------------------
    _wizard_category = ss.get("_wizard_category", "")
    _wizard_category_other = ss.get("_wizard_category_other", "")
    if _wizard_category == "Other":
        initiative_category = _wizard_category_other
    elif not _wizard_category:
        initiative_category = ""
    else:
        initiative_category = _wizard_category

    _wizard_deployment_strategy = ss.get("_wizard_deployment_strategy", "")
    _wizard_deployment_strategy_other = ss.get("_wizard_deployment_strategy_other", "")
    if _wizard_deployment_strategy == "Other":
        actual_deployment_strategy = _wizard_deployment_strategy_other
    else:
        actual_deployment_strategy = _wizard_deployment_strategy

    payload["initiative"] = {
        "author": ss.get("_wizard_author", ""),
        "title": ss.get("_wizard_automation_title", ""),
        "description": ss.get("_wizard_automation_description", ""),
        "category": initiative_category,
        "problem_statement": ss.get("_wizard_problem_statement", ""),
        "expected_use": ss.get("_wizard_expected_use", ""),
        "error_conditions": ss.get("_wizard_error_conditions", ""),
        "assumptions": ss.get("_wizard_assumptions", ""),
        "deployment_strategy": actual_deployment_strategy if actual_deployment_strategy != "" else "",
        "deployment_strategy_description": ss.get("_wizard_deployment_strategy_description", ""),
        "out_of_scope": ss.get("_wizard_out_of_scope", ""),
        "no_move_forward": ss.get("no_move_forward", ""),
        "no_move_forward_reasons": ss.get("no_move_forward_reasons", []),
    }

    # ------------------------------------------------------------------
    # my_role
    # ------------------------------------------------------------------
    payload["my_role"] = {
        "who": _norm_role_choice(
            ss.get("my_role_who", SENTINEL_SELECT),
            ss.get("my_role_who_other", ""),
            SENTINEL_SELECT,
        ),
        "skills": _norm_role_choice(
            ss.get("my_role_skills", SENTINEL_SELECT),
            ss.get("my_role_skills_other", ""),
            SENTINEL_SELECT,
        ),
        "developer": _norm_role_choice(
            ss.get("my_role_dev", SENTINEL_SELECT),
            ss.get("my_role_dev_other", ""),
            SENTINEL_SELECT,
        ),
    }

    # ------------------------------------------------------------------
    # stakeholders
    # ------------------------------------------------------------------
    payload["stakeholders"] = {
        "choices": ss.get("stakeholders_choices") or {},
        "other": (ss.get("stakeholders_other_text") or "").strip(),
    }

    # ------------------------------------------------------------------
    # presentation
    # ------------------------------------------------------------------
    user_opts = [
        "Network Engineers",
        "IT",
        "Operations",
        "Help Desk",
        "Other IT Organizations",
        "Any User",
        "Authorized Users",
        "Automation Pipeline",
    ]
    interact_opts = [
        "CLI",
        "Purpose-built Web GUI",
        "Other GUI",
        "API",
        "Commercial Product/GUI",
        "Open Source Product/GUI",
    ]
    tool_opts = [
        "Python",
        "Python Web Framework (Streamlit, Flask, etc.)",
        "General Web Framework",
        "Automation Framework",
        "REST API",
        "GraphQL API",
        "Custom API",
    ]
    auth_opts_pres = [
        "No Authentication (suitable only for demos and very specific use cases)",
        "Repository authorization/sharing",
        "Built-in (to the automation) Authentication via Username/Password or TOKEN",
        "Custom Authentication to external system (AD, SSH Keys, OAUTH2)",
    ]

    selected_users = [opt for opt in user_opts if ss.get(f"pres_user_{opt}", False)]
    if ss.get("pres_user_custom_enable", False):
        custom_user = (ss.get("pres_user_custom") or "").strip()
        if custom_user:
            selected_users.append(custom_user)

    selected_interactions = [opt for opt in interact_opts if ss.get(f"pres_interact_{opt}", False)]
    if ss.get("pres_interact_custom_enable", False):
        custom_interact = (ss.get("pres_interact_custom") or "").strip()
        if custom_interact:
            selected_interactions.append(custom_interact)

    selected_tools = [opt for opt in tool_opts if ss.get(f"pres_tool_{opt}", False)]
    if ss.get("pres_tool_custom_enable", False):
        custom_tool = (ss.get("pres_tool_custom") or "").strip()
        if custom_tool:
            selected_tools.append(custom_tool)

    selected_auth_pres = [opt for opt in auth_opts_pres if ss.get(f"pres_auth_{opt}", False)]
    if ss.get("pres_auth_other_enable", False):
        custom_auth = (ss.get("pres_auth_other_text") or "").strip()
        if custom_auth:
            selected_auth_pres.append(custom_auth)

    users_sentence = f"This solution targets {_join(selected_users)}."
    interaction_sentence = (
        f"Users will interact with the solution via {_join(selected_interactions)}."
    )
    tools_sentence = (
        f"The presentation layer will be built using {_join(selected_tools)}."
    )
    auth_sentence_pres = (
        f"Presentation authentication will use {_join(selected_auth_pres)}."
    )

    payload["presentation"] = {
        "users": users_sentence,
        "interaction": interaction_sentence,
        "tools": tools_sentence,
        "auth": auth_sentence_pres,
        "selections": {
            "users": selected_users,
            "interactions": selected_interactions,
            "tools": selected_tools,
            "auth": selected_auth_pres,
        },
    }

    # ------------------------------------------------------------------
    # intent
    # ------------------------------------------------------------------
    intent_dev_opts = [
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
    ]
    intent_prov_opts = [
        "Text file",
        "Serialized format (JSON, YAML)",
        "CSV",
        "Excel",
        "API",
    ]

    selected_intent_devs = [opt for opt in intent_dev_opts if ss.get(f"intent_dev_{opt}", False)]
    if ss.get("intent_dev_custom_enable", False):
        custom_intent_dev = (ss.get("intent_dev_custom") or "").strip()
        if custom_intent_dev:
            selected_intent_devs.append(custom_intent_dev)

    selected_intent_prov = [opt for opt in intent_prov_opts if ss.get(f"intent_prov_{opt}", False)]
    if ss.get("intent_prov_custom_enable", False):
        custom_intent_prov = (ss.get("intent_prov_custom") or "").strip()
        if custom_intent_prov:
            selected_intent_prov.append(custom_intent_prov)

    intent_sentence = f"Intent will be developed using {_join(selected_intent_devs)}."
    intent_provided_sentence = f"Intent will be provided via {_join(selected_intent_prov)}."

    payload["intent"] = {
        "development": intent_sentence,
        "provided": intent_provided_sentence,
        "selections": {
            "development": selected_intent_devs,
            "provided": selected_intent_prov,
        },
    }

    # ------------------------------------------------------------------
    # observability
    # ------------------------------------------------------------------
    state_methods_opts = ["Manual", "Purpose-built Python Script", "API call"]
    obs_tools_opts = [
        "Open Source Software",
        "Commercial/Enterprise Product",
        "Network Vendor Product (Cisco Catalyst Center, Arista CVP, etc.)",
        "Custom Python Scripts",
    ]

    selected_methods = [opt for opt in state_methods_opts if ss.get(f"obs_state_{opt}", False)]

    selected_tools_obs = [opt for opt in obs_tools_opts if ss.get(f"obs_tool_{opt}", False)]
    if ss.get("obs_tool_other_enable", False):
        custom_obs_tool = (ss.get("obs_tool_other_text") or "").strip()
        if custom_obs_tool:
            selected_tools_obs.append(custom_obs_tool)

    go_no_go_text = ss.get("obs_go_no_go", "")
    add_logic_choice = ss.get("obs_add_logic_choice", "No")
    add_logic_text = ss.get("obs_add_logic_text", "")

    methods_sentence = f"Network state will be determined via {_join(selected_methods)}."
    go_no_go_sentence = f"Go/No-Go criteria: {(go_no_go_text or '').strip() or 'TBD'}."

    if add_logic_choice == "Yes":
        additional_logic_sentence = (
            f"Additional gating logic will be applied: {(add_logic_text or '').strip() or 'TBD'}."
        )
    else:
        additional_logic_sentence = (
            "No additional gating logic beyond the defined go/no-go criteria."
        )

    tools_sentence_obs = f"Observability will be supported by {_join(selected_tools_obs)}."

    payload["observability"] = {
        "methods": methods_sentence,
        "go_no_go": go_no_go_sentence,
        "additional_logic": additional_logic_sentence,
        "tools": tools_sentence_obs,
        "selections": {
            "methods": selected_methods,
            "go_no_go_text": go_no_go_text,
            "additional_logic_enabled": add_logic_choice == "Yes",
            "additional_logic_text": add_logic_text,
            "tools": selected_tools_obs,
        },
    }

    # ------------------------------------------------------------------
    # orchestration
    # ------------------------------------------------------------------
    ORCH_SENTINEL = "— Select one —"
    orch_choice = ss.get("orch_choice", ORCH_SENTINEL)
    orch_details = ss.get("orch_details_text", "")

    if orch_choice == ORCH_SENTINEL:
        orch_sentence = ""
    elif orch_choice == "No":
        orch_sentence = "No Orchestration will be used in this project."
    elif orch_choice == "Yes – internal via custom scripts and logic":
        orch_sentence = (
            "Orchestration will be implemented internally using custom scripts and logic"
            " to coordinate end-to-end workflows."
        )
    elif orch_choice == "Yes – provide details":
        orch_sentence = f"Orchestration will be utilized: {(orch_details or '').strip() or 'TBD'}."
    else:
        orch_sentence = ""

    payload["orchestration"] = {
        "summary": orch_sentence,
        "selections": {
            "choice": orch_choice,
            "details": orch_details,
        },
    }

    # ------------------------------------------------------------------
    # collector
    # ------------------------------------------------------------------
    collect_method_opts = [
        "SNMP",
        "CLI/SSH",
        "NETCONF",
        "gNMI",
        "REST API",
        "Webhooks",
        "Syslog",
        "Streaming Telemetry",
    ]
    coll_auth_opts = ["Username/Password", "SSH Keys", "OAuth2", "API Token", "mTLS"]
    handling_opts = ["None", "Rate limiting", "Retries", "Exponential backoff", "Buffering/Queue"]
    norm_opts = ["None", "Timestamping", "Tagging/labels", "Topology enrichment", "Schema mapping"]
    coll_tool_opts = [
        "None",
        "Open Source Software",
        "Commercial/Enterprise Product",
        "In-house Software",
    ]

    selected_coll_methods = [
        opt for opt in collect_method_opts if ss.get(f"collector_method_{opt}", False)
    ]
    if ss.get("collector_methods_other_enable", False):
        custom_coll_method = (ss.get("collector_methods_other") or "").strip()
        if custom_coll_method:
            selected_coll_methods.append(custom_coll_method)

    selected_coll_auth = [
        opt for opt in coll_auth_opts if ss.get(f"collector_auth_{opt}", False)
    ]
    if ss.get("collector_auth_other_enable", False):
        custom_coll_auth = (ss.get("collector_auth_other") or "").strip()
        if custom_coll_auth:
            selected_coll_auth.append(custom_coll_auth)

    selected_handling = [
        opt for opt in handling_opts if ss.get(f"collector_handle_{opt}", False)
    ]
    if ss.get("collector_handling_other_enable", False):
        custom_handling = (ss.get("collector_handling_other") or "").strip()
        if custom_handling:
            selected_handling.append(custom_handling)

    selected_norm = [opt for opt in norm_opts if ss.get(f"collector_norm_{opt}", False)]
    if ss.get("collector_norm_other_enable", False):
        custom_norm = (ss.get("collector_norm_other") or "").strip()
        if custom_norm:
            selected_norm.append(custom_norm)

    selected_coll_tools = [
        opt for opt in coll_tool_opts if ss.get(f"collection_tool_{opt}", False)
    ]
    if ss.get("collection_tools_other_enable", False):
        custom_coll_tool = (ss.get("collection_tools_other") or "").strip()
        if custom_coll_tool:
            selected_coll_tools.append(custom_coll_tool)

    devices = ss.get("collector_devices", "")
    metrics = ss.get("collector_metrics", "")
    cadence = ss.get("collector_cadence", "")

    coll_methods_sentence = f"Collection will use {_join(selected_coll_methods)}."
    coll_auth_sentence = f"Authentication will leverage {_join(selected_coll_auth)}."
    handling_sentence = f"Traffic handling will include {_join(selected_handling)}."
    norm_sentence = f"Collected data will be normalized via {_join(selected_norm)}."
    scale_sentence = (
        f"Expected scale: ~{devices or 'TBD'} devices, "
        f"~{metrics or 'TBD'} metrics/sec, cadence {cadence or 'TBD'}."
    )
    tools_sentence_coll = f"Collection tools will include {_join(selected_coll_tools)}."

    payload["collector"] = {
        "methods": coll_methods_sentence,
        "auth": coll_auth_sentence,
        "handling": handling_sentence,
        "normalization": norm_sentence,
        "scale": scale_sentence,
        "tools": tools_sentence_coll,
        "selections": {
            "methods": selected_coll_methods,
            "auth": selected_coll_auth,
            "handling": selected_handling,
            "normalization": selected_norm,
            "devices": devices,
            "metrics_per_sec": metrics,
            "cadence": cadence,
            "tools": selected_coll_tools,
        },
    }

    # ------------------------------------------------------------------
    # executor
    # ------------------------------------------------------------------
    exec_opts = [
        "Automating CLI interaction with Python automation frameworks (Netmiko, Napalm, Nornir, PyATS)",
        "Using Open Source Software (Ansible, Terraform, etc.)",
        "Using Custom Python scripts",
        "Using Network Vendor Product (Cisco DNA Center, Arista CVP)",
        "Using a Commercial/Enterprise Product",
    ]

    selected_exec = [
        exec_opts[i] for i in range(len(exec_opts)) if ss.get(f"exec_{i}", False)
    ]
    if ss.get("exec_custom_enable", False):
        custom_exec = (ss.get("exec_custom_text") or "").strip()
        if custom_exec:
            selected_exec.append(custom_exec)

    exec_sentence = f"Execution will be performed using {_join(selected_exec)}."

    payload["executor"] = {
        "methods": exec_sentence,
        "selections": {
            "methods": selected_exec,
        },
    }

    # ------------------------------------------------------------------
    # dependencies
    # ------------------------------------------------------------------
    dep_defs = [
        {"key": "network_infra",    "label": "Network Infrastructure",                  "details": False},
        {"key": "network_controllers", "label": "Network Controllers",                   "details": True},
        {"key": "revision_control", "label": "Revision Control system",                 "details": True},
        {"key": "itsm",             "label": "ITSM/Change Management System",           "details": True},
        {"key": "authn",            "label": "Authentication System",                   "details": True},
        {"key": "ipams",            "label": "IPAMS Systems",                           "details": True},
        {"key": "inventory",        "label": "Inventory Systems",                       "details": True},
        {"key": "design_intent",    "label": "Design Data/Intent Systems",              "details": True},
        {"key": "observability",    "label": "Observability System",                    "details": True},
        {"key": "vendor_mgmt",      "label": "Vendor Tool/Management System",           "details": True},
    ]

    deps_selected = []
    for d in dep_defs:
        if ss.get(f"dep_{d['key']}", False):
            detail = ss.get(f"dep_{d['key']}_details", "") if d["details"] else ""
            deps_selected.append({"name": d["label"], "details": (detail or "").strip()})

    payload["dependencies"] = deps_selected

    # ------------------------------------------------------------------
    # timeline
    # ------------------------------------------------------------------
    start_date = ss.get("timeline_start_date") or datetime.datetime.today().date()
    holiday_region = ss.get("timeline_holiday_region", "None")

    holiday_set = _build_holiday_set(holiday_region, start_date.year, years_ahead=3)

    schedule = []
    cursor = start_date
    total_bd = 0

    for row in ss.get("timeline_milestones", []):
        name = (row.get("name") or "").strip()
        dur = int(row.get("duration") or 0)
        notes = row.get("notes") or ""
        if not name and dur <= 0:
            continue
        item_start = cursor
        item_end = _add_business_days(item_start, dur, holiday_set) if dur > 0 else item_start
        schedule.append(
            {
                "name": name or "(Unnamed)",
                "duration_bd": dur,
                "start": item_start,
                "end": item_end,
                "notes": notes,
            }
        )
        cursor = item_end
        total_bd += max(0, dur)

    payload["timeline"] = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "total_business_days": total_bd,
        "projected_completion": schedule[-1]["end"].strftime("%Y-%m-%d") if schedule else None,
        "build_buy": ss.get("timeline_build_buy", "Build In-House"),
        "staff_count": int(ss.get("timeline_staff_count", 0) or 0),
        "external_staff_count": int(ss.get("timeline_external_staff_count", 0) or 0),
        "staffing_plan_md": ss.get("timeline_staffing_plan", ""),
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

    return payload
