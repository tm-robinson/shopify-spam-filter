# AGENTS.md

## Overview

This project consists of a **Python Flask backend** and a **React frontend**. This file provides coding and collaboration guidelines specifically for AI agents and human collaborators assisting with development tasks.

---

## General Guidelines

- All changes should be minimal, readable, and consistent with the current codebase.
- When in doubt, prefer clarity over cleverness.
- Do not add new dependencies without a documented justification.
- The functionality should be documented as user stories within PROJECT_BACKLOG.md.  Always keep this up to date, adding or updating any user stories as needed.
- Test scenarios are also held in PROJECT_BACKLOG.md within each user story.
- Each user story and test scenario has a status of TODO or DONE to show whether it has been implemented.
- If new functionality is implemented that is not in PROJECT_BACKLOG.md, add a new user story for it in there.
- If tests are implemented, the test scenarios within PROJECT_BACKLOG.md should be updated to replace TODO with DONE.  This represents the status of the automated test, rather than the status of the functionality within the user story itself.
- Whenever the code is changed, leave a comment that begins with CODEX: to explain the change.
- All changes should be added to WORK_LOG.md.
- Mention user stories in commit messages
- Maintain a WORK_LOG.md showing what has been built when and what files/folders it affects.  Always add to the bottom of the WORK_LOG.md for any changes, but ensure that today's date is used as the section heading.  If there is already a section for today's date, don't create a new section, just add extra items to it.
- Create/maintain a test suite and run it pre commit
---

## Code Style

### Python
- Format all code using **Black**.
- Lint with **flake8** before submitting code.
- Avoid single-letter or ambiguous variable names.
- Use explicit imports and avoid `import *`.

### JavaScript/React
- Use **ESLint** with default React rules.
- Use **Prettier** for formatting.
- Prefer functional components and hooks (`useState`, `useEffect`).
- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript) where practical.

---

## Directory Structure

- Backend: `backend/` (Flask app)
- Frontend: `frontend/` (React app)
- Shared assets/configs: `shared/` (if present)

Agents should respect this structure and place new files accordingly.

---

## Git and PR Instructions

- Use descriptive branch names: `feature/<summary>`, `fix/<summary>`, etc.
- PR title format: `CODEX: [Feature] Summary of change`
- Each PR must include:
  - A one-line summary of the change
  - A list of user stories the change implements
  - A list of modified files or major components affected
  - Any known side effects or caveats
  - A description of any testing performed
- Commit message format: `CODEX: Summary of change`

---

## Testing

> Note: Automated tests are **not yet implemented** in this project.

- Manual testing instructions should be provided in the PR when applicable.
- If you add any test files or test scaffolding, place them in `backend/tests/` or `frontend/__tests__/`.
- Document the test scenarios underneath the relevant user story in PROJECT_BACKLOG.md

---

## Dependencies

- Use `requirements.txt` for Python dependencies.
- Use `package.json` and `yarn.lock` or `package-lock.json` for frontend dependencies.
- Document any new dependencies and their purpose in the PR description.

---

## AI Agent Tasks

If you are an AI agent making modifications:
- Do not refactor unrelated code unless explicitly requested.
- Leave comments marking your changes using the format:
  ```python
  # CODEX: Changed X to Y to achieve Z
  ```
- Avoid speculative changes — prioritize instructions and commit messages over assumptions.