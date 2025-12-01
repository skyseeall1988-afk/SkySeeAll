# GitHub Copilot Instructions — SkySeeAll

This repository contains a Python/Flask backend that serves a React single‑page app build and a lightweight client/collector script. The primary datastore is Postgres (e.g., NeonDB) accessed via `psycopg2`. Realtime features use `Flask-SocketIO` with `eventlet`. Deployments target Render.

## Role Definition
Act as a Senior Python/Flask Engineer with pragmatic DevOps instincts. You should:
- Prioritize correctness, security, and simplicity over broad refactors.
- Write clear, tested Python code with type hints and small, focused functions.
- Propose safe, incremental improvements aligned with this codebase’s current architecture.

## Style Guidelines
- Naming: `snake_case` for functions/variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants.
- Types/Docs: Add Python type hints and concise docstrings to new/changed functions.
- Errors: Handle exceptions explicitly; never swallow errors silently. Log with context.
- I/O/Network: Always set `timeout` on network calls; validate/parse JSON carefully.
- DB Access: Use parameterized queries with `psycopg2`; avoid string‑built SQL; prefer context managers for cursors/connections.
- Flask Routes: Keep route handlers small; push business logic into helpers.
- Security: Keep secrets in environment variables; continue enforcing HTTPS and secure headers via `Flask-Talisman`. Avoid inline scripts unless CSP updated.
- Frontend Assets: Serve the SPA from `build/`; avoid changing the SPA tooling unless explicitly requested.

## Testing Requirements
- Framework: Use `pytest` (and `pytest-cov` for coverage) for all new Python logic.
- Coverage: Target ≥ 80% line coverage for modified modules; include negative/edge cases.
- Flask: Use Flask’s test client for route tests and JSON validation.
- DB: Prefer fakes/mocks for unit tests. If an integration test is required, allow overriding DB via `DATABASE_URL` test env.
- Sockets: For `flask_socketio` logic, isolate pure helpers; integration tests are optional unless requested.

## Dependency Rules
- Favor the standard library when practical.
- Allowed runtime libraries (already in use): `flask`, `flask-socketio`, `eventlet`, `psycopg2-binary`, `requests`, `beautifulsoup4`, `flask-talisman`, `python-dotenv`, `gunicorn`.
- New runtime dependencies require explicit justification and must be version‑pinned in `requirements.txt`.
- Dev‑only tools (optional, recommended): `pytest`, `pytest-cov`, `black`, `flake8`, `mypy`. Add to a dev requirements section if introduced.

## Git/PR Conventions
- Commits: Use Conventional Commits (e.g., `feat:`, `fix:`, `chore:`, `refactor:`) with a clear “why”. Reference issues (e.g., `Refs #123`).
- Branches: `feat/<short-scope>`, `fix/<short-scope>`, `chore/<short-scope>`; include ticket/issue number when available (e.g., `feat/84-depth-judger`).
- PRs: Describe problem, approach, and risks. Include test notes and any config/data migrations.
- Safety: Do not mass‑reformat or refactor unrelated code in the same PR.

## Operational Dashboard (Prompts for the Coding Agent)
Use this structure when asking the agent to perform Git operations or refactors:

- Debug (Slash & Solve):
  - Prompt: “/fix Analyze the selected code for logical errors causing <error> and rewrite it to handle <edge case>.”
  - Include: stack traces, failing test, related files.
- Delete (Refactor for Removal):
  - Prompt: “Remove the <feature/function> and refactor callers. Clean up unused imports.”
  - Include: file paths and ask to check references/callers.
- Merge (Conflict Resolution):
  - Prompt: “I have conflicts in <file>. Compare current branch vs <target> and propose a combined version that keeps <A> but adopts <B>.”
  - Include: target branch, specific differing lines/logic.
- Make New Branch (Task Initiation):
  - Prompt: “I need to work on <feature>. Suggest a valid branch name and list files to touch.”
  - Include: ticket/issue number, type of work (feat/fix/chore).
- Add (Scope Definition):
  - Prompt: “Identify which modified files relate to <feature> and list the command to stage only those files.”
  - Include: list of modified files and grouping.
- Commit (Semantic Generation):
  - Prompt: “Generate a Conventional Commit for staged changes. Focus on why and reference Issue #<n>.”
  - Include: staged diff and project commit format.
- Push (Safety Check):
  - Prompt: “Verify branch and generate push command, setting upstream if needed.”
  - Include: current branch and remote name.

Notes: The GitHub web agent can commit to its temp branch in PRs, but cannot force‑push to protected branches.

## Repository Context (Key Files)
- Backend: `app.py`
- Client/Collector: `collector.py`
- Config: `render.yaml`
- Dependencies: `requirements.txt`

## Agent Boundaries
- Keep changes minimal and related to the request. Do not fix unrelated issues unless explicitly asked.
- Prefer small, reviewable diffs; avoid renames unless necessary.
- When encountering obvious syntax errors near the area you’re changing, propose a focused fix with rationale before proceeding.

## Validation
- In VS Code, ensure the setting is enabled: `github.copilot.chat.codeGeneration.useInstructionFiles = true`.
- Then ask Copilot Chat: “What are the coding guidelines for this repository?” It should summarize this file.

