# Test Documentation

This document describes the test structure and test files for the NAF Solution Wizard application.

## Test Directory Structure

```
naf_framework_solution_wizard/
├── tests/                          # Main test directory
│   ├── README.md                   # Original test documentation
│   ├── TEST_README.md              # This file - updated test documentation
│   ├── conftest.py                 # pytest configuration
│   ├── test_wizard_utils.py        # Tests for wizard utility functions
│   ├── test_data_generator.py      # Data generation tests
│   ├── upload_validator.py         # Upload validation utilities
│   ├── exports/                    # Test export outputs
│   │   ├── sample_author_payload.json      # Sample JSON with author field
│   │   ├── sample_complete_payload.json    # Complete wizard payload sample
│   │   └── lorem_export_*.json             # Generated export test files
│   ├── generated/                  # Generated test data
│   │   └── [Contains dynamically generated test data for testing]
│   ├── results/                    # Test results and outputs
│   │   └── [Contains test execution results and logs]
│   ├── archive/                    # Archived tests (ignored by pytest)
│   │   ├── run_lorem_test.py       # Archived lorem test runner
│   │   ├── test_csat_utils.py      # Archived CSAT utilities tests
│   │   ├── test_data_generator.py  # Archived data generator tests
│   │   ├── test_lorem.py           # Archived lorem tests
│   │   ├── test_streamlit_ui.py    # Archived Streamlit UI tests
│   │   ├── test_streamlit_upload_integration.py # Archived upload tests
│   │   └── upload_validator.py     # Archived upload validator
│   │
│   ├── test_deployment_strategy_other.py  # Deployment Strategy "Other" tests
│   ├── test_specific_fields.py         # Specific field validation tests
│   ├── test_stakeholders_none.py       # Stakeholders "None" selection tests
│   ├── test_stakeholders_widget_init.py # Stakeholders widget initialization tests
│   ├── test_stakeholders_full_flow.py  # Stakeholders complete flow tests
│   ├── test_stakeholders_category_mapping.py # Stakeholders category preservation tests
│   ├── test_title_roundtrip.py         # Title field round-trip tests
│   └── test_wizard_data_complete.py    # Complete wizard payload tests
```

## Test File Organization

### Tests Directory (`tests/`)
The `tests/` directory contains pytest-based tests that:
- Use pytest framework with fixtures and assertions
- Test utility functions and helper modules
- Have complex setup/teardown requirements
- Generate test data and validate exports

**Key files in `tests/` relevant to recent work:**
- `conftest.py` - pytest configuration and shared fixtures
- `test_wizard_utils.py` - Tests for wizard-specific utility functions (fixed import from wizard_utils → utils)
- `test_wizard_data_complete.py` - NEW: Tests for complete wizard payload functionality
- All test files moved from repository root to `tests/` directory for better organization

### Archive Directory (`tests/archive/`)
The `archive/` directory contains legacy tests that:
- Have import issues or outdated dependencies
- Are no longer maintained but kept for reference
- Are automatically ignored by pytest configuration

### Test Output Directories

#### `tests/exports/`
Contains test-generated export files and sample outputs:
- `sample_author_payload.json` - Sample payload demonstrating author field functionality
- `sample_complete_payload.json` - Complete wizard payload with all sections populated
- `lorem_export_*.json` - Generated JSON exports from lorem ipsum tests
- `lorem_export_*.markdown` - Corresponding markdown exports

#### `tests/generated/`
Contains dynamically generated test data:
- Test data files created during test execution
- Sample JSON files for testing various scenarios
- Temporary data used by test generators

#### `tests/results/`
Contains test execution results and logs:
- Test run output files
- Execution logs and trace files
- Test performance metrics
- Error reports and debugging information

### Git Exclusion

The following test output directories are excluded from git via `.gitignore`:
- `tests/exports/` - Generated export files and sample payloads
- `tests/generated/` - Dynamically generated test data
- `tests/results/` - Test execution results and logs

**Why they're excluded:**
- Keeps the git repository clean (no generated files in version control)
- Prevents conflicts when multiple developers run tests
- Reduces repository size
- Generated files can contain dynamic data (timestamps, UUIDs, etc.)

**Automatic Generation:**
These directories are created automatically when tests run. For example:
```python
sample_file = Path(__file__).parent / "exports" / "sample_author_payload.json"
with open(sample_file, "w") as f:
    json.dump(payload, f, indent=2)
```
The above code will create the `exports` directory if it doesn't exist.

### Test Files (Now All in `tests/`)

#### 1. `test_title_roundtrip.py` (MOVED from root)
**Purpose:** Tests the core JSON save/load functionality for the title field.

**Key Tests:**
- `test_title_field_roundtrip()` - Verifies only the title field changes when modified
- `test_json_serialization_roundtrip()` - Tests JSON serialization integrity
- `test_multiple_field_changes()` - Validates multiple field updates

**Dependencies:**
- `wizard_data.py` - Uses `build_wizard_payload()` and `restore_session_state_from_data()`

#### 2. `test_deployment_strategy_other.py` (MOVED from root)
**Purpose:** Tests the "Other" option functionality for deployment strategy field.

**Key Tests:**
- `test_deployment_strategy_other_roundtrip()` - Custom strategy preservation
- `test_standard_deployment_strategy()` - Standard strategy handling
- `test_unknown_deployment_strategy()` - Unknown strategy moved to "Other"

**Dependencies:**
- `wizard_data.py` - Tests payload building and session state restoration
- `deployment_strategies.yml` - Validates against predefined strategies

#### 3. `test_specific_fields.py` (MOVED from root)
**Purpose:** Tests specific field scenarios as requested by users.

**Key Tests:**
- `test_category_device_onboarding()` - Category "Device Onboarding" save/load
- `test_deployment_strategy_other_my_own()` - Custom strategy "My own Strategy"
- `test_json_roundtrip_combined()` - Both fields together

**Dependencies:**
- `wizard_data.py` - Core data transformation functions
- `use_case_categories.yml` - Validates category names

#### 4. `test_stakeholders_none.py` (MOVED from root)
**Purpose:** Tests stakeholders field handling with "None" selections.

**Key Tests:**
- `test_stakeholders_with_none_selections()` - Verifies "None" selections are preserved
- `test_stakeholders_empty_and_none()` - Tests empty and None stakeholder data
- `test_stakeholders_all_none()` - Validates all stakeholders set to "None"

**Dependencies:**
- `wizard_data.py` - Tests restore_session_state_from_data() for stakeholders

#### 5. `test_stakeholders_widget_init.py` (MOVED from root)
**Purpose:** Tests that stakeholders widgets are properly initialized from uploaded JSON.

**Key Tests:**
- `test_stakeholders_widget_initialization()` - Verifies widget keys get uploaded values
- `test_stakeholders_widget_with_empty_data()` - Tests empty data handling

**Dependencies:**
- `wizard_data.py` - Tests session state restoration for widget initialization

#### 6. `test_stakeholders_full_flow.py` (MOVED from root)
**Purpose:** Tests complete stakeholders flow including selectbox index calculation.

**Key Tests:**
- `test_stakeholders_selectbox_index_calculation()` - Verifies correct index calculation
- `test_stakeholders_full_roundtrip()` - Tests complete save/load cycle
- `test_stakeholders_edge_cases()` - Tests edge cases and error handling

**Dependencies:**
- `wizard_data.py` - Tests payload building and restoration

#### 7. `test_stakeholders_category_mapping.py` (MOVED from root)
**Purpose:** Tests stakeholder category preservation (updated from mapping to preservation).

**Key Tests:**
- `test_stakeholders_category_mapping()` - Tests category preservation as-is
- `test_stakeholders_mapping_with_actual_values()` - Tests with user's JSON
- `test_stakeholders_mapping_edge_cases()` - Tests edge cases

**Note:** Updated to reflect that categories are now preserved exactly as provided, not mapped.

#### 8. `test_wizard_data_complete.py` (NEW)
**Purpose:** Tests the complete implementation of wizard_data.py functionality.

**Key Tests:**
- `test_complete_payload()` - Tests all wizard sections are built correctly
- Verifies round-trip functionality for all sections
- Tests payload building and session state restoration for complete wizard

**Dependencies:**
- `wizard_data.py` - Tests all helper functions and complete payload building

#### 9. `test_lorem.py` (MOVED to archive)
**Purpose:** Lorem ipsum text generation test.
**Status:** Moved to `tests/archive/` due to import issues

## Core Test Dependencies

### `wizard_data.py` (UPDATED)
The central module for data transformation that most tests depend on:

**Complete Implementation Now Includes:**
- `build_wizard_payload(session_state)` - Converts session state to JSON payload (ALL sections)
- `restore_session_state_from_data(data)` - Converts JSON back to session state updates (ALL sections)
- `get_title_only_session_state(title)` - Creates minimal test session state

**New Helper Functions:**
- `_collect_checkbox_values()` - Extracts checked values for a given prefix
- `_build_sentence_from_list()` - Creates human-readable sentences from lists
- `_get_custom_value()` - Gets custom values when enable toggles are active
- `_build_presentation_data()` - Builds presentation section data
- `_build_intent_data()` - Builds intent section data
- `_build_observability_data()` - Builds observability section data
- `_build_orchestration_data()` - Builds orchestration section data
- `_build_collector_data()` - Builds collector section data
- `_build_executor_data()` - Builds executor section data
- `_build_dependencies_data()` - Builds dependencies list
- `_build_timeline_data()` - Builds timeline with business day calculations

**All Sections Now Handled:**
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

### Configuration Files
- `deployment_strategies.yml` - Predefined deployment strategies
- `use_case_categories.yml` - Predefined categories for validation
- `pyproject.toml` - Updated with pytest configuration

## Running Tests

### Pytest Configuration (UPDATED)
The `pyproject.toml` now includes:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
norecursedirs = ["tests/archive", ".*", "build", "dist", "CVS", "_darcs", "{arch}", "*.egg"]
```

### Running All Tests
```bash
# Run all tests (excludes archive directory automatically)
uv run pytest -v

# Run all tests with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_title_roundtrip.py -v
```

### Running Tests with Specific Exclusions
```bash
# Exclude archive directory and specific files
uv run pytest tests/ --ignore=tests/archive --ignore=tests/test_lorem.py -v
```

## Test Relationships (UPDATED)

```
wizard_data.py (Complete Core Module)
├── test_title_roundtrip.py ──┐
├── test_deployment_strategy_other.py ──┐
├── test_specific_fields.py ──┐
├── test_stakeholders_none.py ──┐
├── test_stakeholders_widget_init.py ──┐
├── test_stakeholders_full_flow.py ──┐
├── test_stakeholders_category_mapping.py ──┐ (updated for preservation)
├── test_wizard_data_complete.py ──┐ (NEW)
    └── All test JSON save/load functionality for ALL wizard sections

pages/20_NAF_Solution_Wizard.py (Main UI)
├── test_stakeholders_widget_init.py
├── test_stakeholders_full_flow.py
    └── Tests widget initialization and index calculation

utils.py
├── tests/test_wizard_utils.py (FIXED import)
    └── Test utility functions
```

## Test Coverage Areas (UPDATED)

1. **Data Transformation**
   - JSON serialization/deserialization (ALL sections)
   - Session state management (complete)
   - Field validation and transformation (all wizard fields)

2. **Field-Specific Behavior**
   - Category field (standard vs "Other")
   - Deployment strategy field (standard vs "Other")
   - Title field round-trip preservation
   - ALL wizard sections now tested

3. **Upload/Download**
   - JSON upload validation
   - Field population from uploaded data
   - Export format validation

4. **Business Logic**
   - Field value preservation
   - Custom strategy handling
   - Round-trip data integrity
   - Stakeholder category preservation (not mapping)

5. **Complete Wizard Flow** (NEW)
   - End-to-end payload building
   - Complete session state restoration
   - All sections integration testing

## Recent Updates (December 2024)

### Major Changes:
1. **wizard_data.py Complete Implementation**
   - All wizard sections now handled
   - Added 9 new helper functions
   - Complete payload building and restoration

2. **Test Organization**
   - All test files moved from root to `tests/` directory
   - Archive directory created for legacy tests
   - Pytest configuration updated

3. **Test Fixes**
   - Fixed import in `test_wizard_utils.py` (wizard_utils → utils)
   - Updated stakeholders tests to reflect preservation behavior
   - Fixed deployment strategy test expectations

4. **Configuration**
   - Added pytest configuration to `pyproject.toml`
   - Configured `norecursedirs` to exclude archive
   - All 26 tests now pass successfully

## Best Practices (UPDATED)

1. **All tests** should:
   - Be located in `tests/` directory
   - Use pytest framework
   - Include clear assertions with helpful error messages
   - Test both success and failure cases
   - Document the purpose of each test function

2. **Test organization**:
   - Business logic tests: `tests/` directory with pytest
   - Utility function tests: `tests/test_wizard_utils.py`
   - Integration tests: `tests/test_wizard_data_complete.py`
   - Legacy tests: `tests/archive/` (ignored)

3. **When adding new tests**:
   - Add to `tests/` directory
   - Follow pytest naming conventions (`test_*.py`)
   - Use the complete wizard_data.py functionality
   - Test all relevant sections
   - Save test outputs to appropriate subdirectories:
     - `tests/exports/` for sample payloads and export files
     - `tests/generated/` for generated test data
     - `tests/results/` for test execution results

## Future Test Additions

When adding new tests:
- For field-specific logic: Add to `tests/` directory
- For utility functions: Add to `tests/test_wizard_utils.py`
- For complete wizard scenarios: Add to `tests/test_wizard_data_complete.py`
- For complex scenarios: Create new test file in `tests/` directory
- All tests should leverage the complete wizard_data.py implementation
