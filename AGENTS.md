# AGENTS.md

## Overview

This project consists of a **Python Flask backend** and a **React frontend**. This file provides coding and collaboration guidelines specifically for AI agents and human collaborators assisting with development tasks.

---

## General Guidelines

- All changes should be minimal, readable, and consistent with the current codebase.
- When in doubt, prefer clarity over cleverness.
- Do not add new dependencies without a documented justification.

---

## Code Style

### Python (Flask)
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
- PR title format: `[Feature] Summary of change`
- Each PR must include:
  - A one-line summary of the change
  - A list of modified files or major components affected
  - Any known side effects or caveats

---

## Testing

> Note: Automated tests are **not yet implemented** in this project.

- Manual testing instructions should be provided in the PR when applicable.
- If you add any test files or test scaffolding, place them in `backend/tests/` or `frontend/__tests__/`.

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
  # [AI] Changed X to Y to achieve Z
  ```
- Avoid speculative changes — prioritize instructions and commit messages over assumptions.