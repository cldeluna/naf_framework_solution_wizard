"""
Puzzle Progress Demo Page

TODO: EARMARKED FOR REMOVAL — puzzle functionality has been moved into
      20_NAF_Solution_Wizard.py. Keep this file only until testing is
      complete, then delete it.

Demonstrates the puzzle progress component with clickable dialogs.
Click a puzzle piece button to open its form dialog.
Submitting the form snaps the piece into place.
"""

import streamlit as st
from puzzle_progress import render_puzzle_progress, PUZZLE_SECTIONS


st.set_page_config(page_title="Puzzle Demo", layout="wide")
st.title("🧩 NAF Puzzle Progress Demo")
st.markdown("Click a section button below the puzzle to fill out its form. Submitting snaps the piece into place!")

# Initialize completion state
if "_demo_completed" not in st.session_state:
    st.session_state["_demo_completed"] = {key: False for key in PUZZLE_SECTIONS}


# ── Dialog definitions ──────────────────────────────────────────────


@st.dialog("Presentation", width="large")
def presentation_dialog():
    st.markdown(
        """
**Presentation Layer Characteristics**
- Provides robust, flexible authentication and authorization.
- Can take many forms: GUIs, ITSM/change systems, chat/messaging, portals, reports.
- May support read and write: view data, initiate tasks, approve changes.
- Interfaces with other framework blocks as needed; it is the primary human touchpoint.
        """
    )

    st.subheader("Intended users")
    cols = st.columns(3)
    user_opts = [
        "Network Engineers", "IT", "Operations", "Help Desk",
        "Other IT Organizations", "Any User", "Authorized Users", "Automation Pipeline",
    ]
    for i, opt in enumerate(user_opts):
        with cols[i % 3]:
            st.checkbox(opt, key=f"pres_user_{opt}")
    with cols[0]:
        if st.checkbox("Custom (fill in)", key="pres_user_custom_enable"):
            st.text_input("Custom users", key="pres_user_custom")

    st.subheader("How will your users interact with your solution?")
    cols2 = st.columns(3)
    interact_opts = [
        "CLI", "Purpose-built Web GUI", "Other GUI",
        "API", "Commercial Product/GUI", "Open Source Product/GUI",
    ]
    for i, opt in enumerate(interact_opts):
        with cols2[i % 3]:
            st.checkbox(opt, key=f"pres_interact_{opt}")
    with cols2[0]:
        if st.checkbox("Custom (fill in)", key="pres_interact_custom_enable"):
            st.text_input("Custom interaction", key="pres_interact_custom")

    st.subheader("What tools will the Presentation layer use?")
    cols3 = st.columns(3)
    tool_opts = [
        "Python", "Python Web Framework (Streamlit, Flask, etc.)",
        "General Web Framework", "Automation Framework",
        "REST API", "GraphQL API", "Custom API",
    ]
    for i, opt in enumerate(tool_opts):
        with cols3[i % 3]:
            st.checkbox(opt, key=f"pres_tool_{opt}")
    with cols3[0]:
        if st.checkbox("Custom (fill in)", key="pres_tool_custom_enable"):
            st.text_input("Custom tool(s)", key="pres_tool_custom")

    st.subheader("How will your users authenticate?")
    cols4 = st.columns(2)
    auth_opts = [
        "No Authentication (demos/specific use cases only)",
        "Repository authorization/sharing",
        "Built-in Authentication (Username/Password or TOKEN)",
        "Custom Authentication (AD, SSH Keys, OAUTH2)",
    ]
    for i, opt in enumerate(auth_opts):
        with cols4[i % 2]:
            st.checkbox(opt, key=f"pres_auth_{opt}")
    with cols4[0]:
        if st.checkbox("Other (fill in details)", key="pres_auth_other_enable"):
            st.text_input("Other authentication details", key="pres_auth_other_text")

    # Preview
    st.divider()
    any_users = any(v for k, v in st.session_state.items() if k.startswith("pres_user_") and v is True)
    any_tools = any(v for k, v in st.session_state.items() if k.startswith("pres_tool_") and v is True)
    if any_users or any_tools:
        st.success("You have selections — click Submit to complete this section.")
    else:
        st.info("Make selections above, then click Submit.")

    # Submit button
    if st.button("Submit Presentation", type="primary", use_container_width=True):
        st.session_state["_demo_completed"]["presentation"] = True
        st.rerun()


@st.dialog("Observability", width="large")
def observability_dialog():
    st.info("Observability form coming soon — this is a placeholder.")
    if st.button("Submit Observability", type="primary", use_container_width=True):
        st.session_state["_demo_completed"]["observability"] = True
        st.rerun()


@st.dialog("Orchestration", width="large")
def orchestration_dialog():
    st.info("Orchestration form coming soon — this is a placeholder.")
    if st.button("Submit Orchestration", type="primary", use_container_width=True):
        st.session_state["_demo_completed"]["orchestration"] = True
        st.rerun()


@st.dialog("Intent", width="large")
def intent_dialog():
    st.info("Intent form coming soon — this is a placeholder.")
    if st.button("Submit Intent", type="primary", use_container_width=True):
        st.session_state["_demo_completed"]["intent"] = True
        st.rerun()


@st.dialog("Collector", width="large")
def collector_dialog():
    st.info("Collector form coming soon — this is a placeholder.")
    if st.button("Submit Collector", type="primary", use_container_width=True):
        st.session_state["_demo_completed"]["collector"] = True
        st.rerun()


@st.dialog("Executor", width="large")
def executor_dialog():
    st.info("Executor form coming soon — this is a placeholder.")
    if st.button("Submit Executor", type="primary", use_container_width=True):
        st.session_state["_demo_completed"]["executor"] = True
        st.rerun()


DIALOGS = {
    "presentation": presentation_dialog,
    "observability": observability_dialog,
    "orchestration": orchestration_dialog,
    "intent": intent_dialog,
    "collector": collector_dialog,
    "executor": executor_dialog,
}

# Section colors for button styling
COLORS = {
    "presentation": "#E8B817",
    "observability": "#2ECC40",
    "orchestration": "#00BFFF",
    "intent": "#FF6B35",
    "collector": "#DC143C",
    "executor": "#7B68EE",
}


# ── Main page ───────────────────────────────────────────────────────

# Render the puzzle progress
render_puzzle_progress(st.session_state["_demo_completed"])

# Section buttons — also clickable from the puzzle pieces directly
st.markdown("#### Click a puzzle piece or button to fill out its form:")
row1 = st.columns(3)
row1_keys = ["presentation", "observability", "orchestration"]
for i, key in enumerate(row1_keys):
    with row1[i]:
        done = st.session_state["_demo_completed"][key]
        icon = "✅" if done else "🧩"
        if st.button(
            f"{icon} {PUZZLE_SECTIONS[key]['label']}",
            key=f"open_{key}",
            use_container_width=True,
        ):
            DIALOGS[key]()

row2 = st.columns(3)
row2_keys = ["intent", "collector", "executor"]
for i, key in enumerate(row2_keys):
    with row2[i]:
        done = st.session_state["_demo_completed"][key]
        icon = "✅" if done else "🧩"
        if st.button(
            f"{icon} {PUZZLE_SECTIONS[key]['label']}",
            key=f"open_{key}",
            use_container_width=True,
        ):
            DIALOGS[key]()

st.divider()

# Reset button
if st.button("🔄 Reset All", use_container_width=True):
    # Clear all pres_ keys and completion state
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("pres_")]
    for k in keys_to_clear:
        del st.session_state[k]
    st.session_state["_demo_completed"] = {key: False for key in PUZZLE_SECTIONS}
    st.rerun()
