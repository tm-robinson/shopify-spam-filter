## 23rd June 2025

- Initial version of UI and Backend implemented.
- Email body processing improvements.

## 25th June 2025

- Fixed polling in React frontend so scan status updates continuously.
- Updated user story status in PROJECT_BACKLOG.md.
- Reformatted backend with Black and frontend with Prettier.
- Restored TODO status for UI test scenarios.
- Added ignore feature with new Gmail label and UI button.
- Updated PROJECT_BACKLOG with ignore user story.
- Implemented chat bubbles with expandable text and colour-coded results.
- Styled email list rows based on status.
- Added new UI styling user story to PROJECT_BACKLOG.

## 26th June 2025

- Reduced chat log text size to 75% for compact bubbles.
- Documented new test scenario for smaller chat text.
- Added backend support for saving scan prompt to last_prompt.json.
- Added endpoint /last-prompt and frontend hook to load it on start.
- Updated PROJECT_BACKLOG with persistent prompt user story.
- Fixed prompt loading by proxying /last-prompt through Vite config.
- Hid system prompts and stripped <RESULT> tags in chat log.
- Added new user story for clean chat display.
- Adjusted confirm endpoint to label spam using `shopify-spam` and remove `INBOX` label.
- Updated README and added user story for confirmation workflow.

- Refactored Gmail listing to handle pagination with list_all_messages helper.
- Added pagination user story to PROJECT_BACKLOG.

## 27th June 2025

- Added backend endpoint `/scan-tasks` to list running scan tasks.
- Frontend now checks for active tasks on load and resumes polling every second.
- Proxied new endpoint through Vite config.
- Documented new user story for resuming tasks in PROJECT_BACKLOG.

## 28th June 2025

- Fixed issue where email status changes during a running scan were lost on refresh.
- Added `update_task_email_status` helper to persist manual updates.
- Updated `/update-status` and `/confirm` endpoints to modify running task data.
- Documented new user story about persisting status updates in PROJECT_BACKLOG.

## 29th June 2025

- Changed scan task lifecycle so completed results remain active until confirmed.
- `/scan-tasks` now returns finished tasks and confirm request closes them.
- Frontend sends task id on confirmation and clears task state.
- Added new user story for keeping completed results visible.
- Closed tasks are removed from server memory once confirmed.
- Confirm action now clears email list in the UI.

- Display progress while fetching whitelist and ignore lists.
- Confirm button disables and shows progress during API call.
- Refactored message fetching to use Gmail batch requests for faster scans.
- Documented new user story about batched fetching in PROJECT_BACKLOG.
- Implemented retry logic for Gmail batch requests to handle 429 errors.
