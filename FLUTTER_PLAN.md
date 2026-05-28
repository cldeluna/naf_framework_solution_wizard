Plan: Flutter Puzzle-based NAF Solution Wizard
TL;DR: Build a new Flutter app for desktop and mobile paired with the existing Python/FastAPI backend. The frontend will use animated puzzle-piece cards for each NAF section, starting scattered and assembling as users complete sections.

Steps

Audit existing repository assets and reuse points.
Review main.py, wizard_data.py, Solution_Design_Report.j2, wizard_payload.schema.json, and config files (deployment_strategies.yml, use_case_categories.yml, stakeholders.json).
Confirm which backend functionality already exists and what needs to be exposed for Flutter.
Define the backend contract exactly.
Use main.py as the backend starting point.
Add or verify the following REST endpoints:
GET /api/v1/config/categories — return use case categories from use_case_categories.yml.
GET /api/v1/config/deployment-strategies — return strategies from deployment_strategies.yml.
GET /api/v1/config/stakeholders — return stakeholder categories from stakeholders.json.
POST /api/v1/solutions — create a new solution payload and return solution_id plus stored JSON.
GET /api/v1/solutions/{solution_id} — retrieve a saved solution payload.
PUT /api/v1/solutions/{solution_id} — update a saved solution payload.
DELETE /api/v1/solutions/{solution_id} — delete a saved payload.
POST /api/v1/solutions/{solution_id}/export?format=json|markdown — export the payload as JSON or Markdown report.
optional POST /api/v1/solutions/{solution_id}/preview — generate live preview markdown without saving, if needed for the app.
Implement the backend integration layer.
Reuse wizard_data.py and Solution_Design_Report.j2 for Markdown generation.
Keep in-memory solution storage for MVP inside main.py.
Add helper functions to load YAML/JSON config data from the repository and return it as API payloads.
Ensure the backend response payload matches wizard_payload.schema.json.
Scaffold the Flutter frontend.
Create a new flutter/ folder at repository root.
Use Flutter stable SDK and Dart.
Use http or dio for REST communication with the backend.
Use a state solution such as riverpod or simple ChangeNotifier/Provider to manage app state across pieces.
Generate Dart models from wizard_payload.schema.json if possible, or define models manually for the schema.
Implement the puzzle-based UI.
Use a responsive layout so the app adapts for desktop, tablet, and phone.
Create a PuzzleBoard screen with one card per section: Initiative, My Role, Stakeholders, Presentation, Intent, Observability, Orchestration, Collector, Executor, Dependencies, Timeline.
Show pieces initially scattered in a loose layout with randomized offsets or rotations.
Animate sections into their final grid positions as the user completes required fields.
Display completion state per piece using color, icons, or badges.
On mobile, use a vertical scroll/accordion layout, while desktop shows a larger board and a side detail panel.
Connect frontend and backend.
Fetch config data (categories, deployment strategies, stakeholders) during app startup.
Support solution create, retrieve, and update workflows.
Use the backend export endpoint to download or preview JSON/Markdown.
Keep the puzzle board state synchronized with saved payloads and local UI state.
Add validation and completion logic.
Define per-piece rules from the existing wizard logic, e.g. key fields for each section.
Mark a piece completed when required fields are filled and no validation errors remain.
Show inline validation messages, plus a “puzzle complete” celebration when all sections are done.
Test and document.
Add backend tests in test_api.py for the new REST endpoints.
Add Flutter integration tests for puzzle completion and section navigation.
Add setup instructions in README.md and flutter/README.md.
Relevant files

main.py — extend this FastAPI app to support the Flutter frontend.
wizard_data.py — reuse payload construction and existing NAF field logic.
Solution_Design_Report.j2 — use the existing markdown report template.
wizard_payload.schema.json — authoritative payload schema for backend and Flutter data models.
deployment_strategies.yml, use_case_categories.yml, stakeholders.json — config sources for frontend dropdowns and selection lists.
20_NAF_Solution_Wizard.py — reference for current field labels, section structure, and completion behavior.
Verification

Backend: run uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 and verify:
config endpoints return the expected lists,
solution create/update/retrieve works,
export endpoint returns JSON and Markdown.
Flutter app: run the Flutter app on desktop and mobile emulator/device.
Confirm the puzzle board renders,
pieces animate from scattered to assembled,
section completion changes the UI state.
Integration: create a solution in Flutter, save it, reload it, and export JSON/Markdown.
Tests: run backend tests and Flutter widget/integration tests.
Decisions

Use Flutter for the new frontend to support desktop and mobile from a single codebase.
Keep Python/FastAPI backend for API, validation, and report generation.
Reuse the existing Jinja template and wizard payload schema to minimize duplication.
Further Considerations

Decide if POST /api/v1/solutions/{solution_id}/preview is needed or if exports are enough.
Determine whether solution persistence should remain in-memory for MVP or use a small file-based store for durability.
Consider whether the existing Streamlit app should stay as a fallback or be deprecated once the Flutter app is complete.
