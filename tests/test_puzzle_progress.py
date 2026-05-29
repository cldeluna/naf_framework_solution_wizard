"""
Tests for puzzle_progress module.

Covers:
- PUZZLE_SECTIONS structure
- check_section_completion logic for each section
- get_completion_state aggregation
- Orchestration sentinel handling (the bug we fixed)
"""

import pytest
from unittest.mock import patch, MagicMock

# Mock streamlit before importing puzzle_progress
import sys
st_mock = MagicMock()
sys.modules["streamlit"] = st_mock
sys.modules["streamlit.components"] = MagicMock()
sys.modules["streamlit.components.v1"] = MagicMock()

from puzzle_progress import (
    PUZZLE_SECTIONS,
    check_section_completion,
    get_completion_state,
)


# ── PUZZLE_SECTIONS structure ──────────────────────────────────────


def test_puzzle_sections_has_all_six():
    expected = {"presentation", "observability", "orchestration", "intent", "collector", "executor"}
    assert set(PUZZLE_SECTIONS.keys()) == expected


def test_puzzle_sections_have_required_fields():
    for key, info in PUZZLE_SECTIONS.items():
        assert "label" in info, f"{key} missing label"
        assert "color" in info, f"{key} missing color"
        assert "row" in info, f"{key} missing row"
        assert "col" in info, f"{key} missing col"


def test_puzzle_sections_grid_layout():
    """Pieces should form a 2x3 grid (rows 0-1, cols 0-2)."""
    positions = {(info["row"], info["col"]) for info in PUZZLE_SECTIONS.values()}
    assert positions == {(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)}


# ── check_section_completion ───────────────────────────────────────


class TestCheckSectionCompletion:
    """Test completion checks for each section."""

    def _mock_session_state(self, data: dict):
        """Patch st.session_state with a dict."""
        st_mock.session_state = data

    def test_presentation_incomplete_when_empty(self):
        self._mock_session_state({})
        assert check_section_completion("presentation") is False

    def test_presentation_complete_with_user_check(self):
        self._mock_session_state({"pres_user_IT": True})
        assert check_section_completion("presentation") is True

    def test_presentation_complete_with_tool_check(self):
        self._mock_session_state({"pres_tool_Python": True})
        assert check_section_completion("presentation") is True

    def test_presentation_incomplete_with_false_checks(self):
        self._mock_session_state({"pres_user_IT": False, "pres_tool_Python": False})
        assert check_section_completion("presentation") is False

    def test_observability_incomplete_when_empty(self):
        self._mock_session_state({})
        assert check_section_completion("observability") is False

    def test_observability_complete_with_state_check(self):
        self._mock_session_state({"obs_state_Manual": True})
        assert check_section_completion("observability") is True

    def test_observability_complete_with_tool_check(self):
        self._mock_session_state({"obs_tool_Custom Python Scripts": True})
        assert check_section_completion("observability") is True

    def test_observability_complete_with_go_no_go(self):
        self._mock_session_state({"obs_go_no_go": "All pre-checks must pass"})
        assert check_section_completion("observability") is True

    def test_orchestration_incomplete_when_empty(self):
        self._mock_session_state({})
        assert check_section_completion("orchestration") is False

    def test_orchestration_incomplete_with_select_sentinel(self):
        """Regression test: '— Select one —' should NOT count as complete."""
        self._mock_session_state({"orch_choice": "— Select one —"})
        assert check_section_completion("orchestration") is False

    def test_orchestration_incomplete_with_old_sentinel(self):
        """The original sentinel 'Select...' should also not count."""
        self._mock_session_state({"orch_choice": "Select..."})
        assert check_section_completion("orchestration") is False

    def test_orchestration_incomplete_with_empty_string(self):
        self._mock_session_state({"orch_choice": ""})
        assert check_section_completion("orchestration") is False

    def test_orchestration_complete_with_no(self):
        self._mock_session_state({"orch_choice": "No"})
        assert check_section_completion("orchestration") is True

    def test_orchestration_complete_with_yes(self):
        self._mock_session_state({"orch_choice": "Yes – internal via custom scripts and logic"})
        assert check_section_completion("orchestration") is True

    def test_intent_incomplete_when_empty(self):
        self._mock_session_state({})
        assert check_section_completion("intent") is False

    def test_intent_complete_with_dev_check(self):
        self._mock_session_state({"intent_dev_Templates": True})
        assert check_section_completion("intent") is True

    def test_intent_complete_with_prov_check(self):
        self._mock_session_state({"intent_prov_API": True})
        assert check_section_completion("intent") is True

    def test_collector_incomplete_when_empty(self):
        self._mock_session_state({})
        assert check_section_completion("collector") is False

    def test_collector_complete_with_method_check(self):
        self._mock_session_state({"collector_method_SNMP": True})
        assert check_section_completion("collector") is True

    def test_collector_complete_with_auth_check(self):
        self._mock_session_state({"collector_auth_SSH Keys": True})
        assert check_section_completion("collector") is True

    def test_executor_incomplete_when_empty(self):
        self._mock_session_state({})
        assert check_section_completion("executor") is False

    def test_executor_complete_with_exec_check(self):
        self._mock_session_state({"exec_0": True})
        assert check_section_completion("executor") is True

    def test_executor_incomplete_with_false_exec(self):
        self._mock_session_state({"exec_0": False, "exec_1": False})
        assert check_section_completion("executor") is False

    def test_unknown_section_returns_false(self):
        self._mock_session_state({})
        assert check_section_completion("nonexistent") is False


# ── get_completion_state ───────────────────────────────────────────


class TestGetCompletionState:

    def _mock_session_state(self, data: dict):
        st_mock.session_state = data

    def test_all_incomplete(self):
        self._mock_session_state({})
        state = get_completion_state()
        assert all(v is False for v in state.values())
        assert set(state.keys()) == set(PUZZLE_SECTIONS.keys())

    def test_mixed_completion(self):
        self._mock_session_state({
            "pres_user_IT": True,
            "orch_choice": "No",
            "exec_0": True,
        })
        state = get_completion_state()
        assert state["presentation"] is True
        assert state["orchestration"] is True
        assert state["executor"] is True
        assert state["observability"] is False
        assert state["intent"] is False
        assert state["collector"] is False

    def test_all_complete(self):
        self._mock_session_state({
            "pres_user_IT": True,
            "obs_state_Manual": True,
            "orch_choice": "No",
            "intent_dev_Templates": True,
            "collector_method_SNMP": True,
            "exec_0": True,
        })
        state = get_completion_state()
        assert all(v is True for v in state.values())
