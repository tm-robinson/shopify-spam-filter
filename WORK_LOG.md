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
- Processed messages in smaller batches during scans to reduce wait times.

- Improved `batch_get_messages` to retry failed ids with exponential backoff
  and return a mapping keyed by message id.
- Updated scan workflow to look up message details by id so missing responses
  no longer corrupt results.
- Added user story about retrying failed batch requests.

- Added shadcn-style mobile friendly layout.
- Moved confirm button and controls to sticky header.
- Removed chat window and added expandable LLM info per email.
- Updated PROJECT_BACKLOG and stylesheets.

## 1st July 2025

- Configured backend to load OpenRouter key from env or file and removed save key endpoint.
- Removed API key and poll interval inputs from UI.
- Added status filter buttons and tightened header spacing.
- Updated README and backlog.
- Combined sender and subject columns, shortened date display and reduced email font size for better mobile layout.
- Limited max UI width for mobile screens and narrowed prompt input.
- Changed default scan range to 3 days.

## 2nd July 2025

- Made page width responsive: wider on desktop screens while keeping mobile width narrow.

## 3rd July 2025

- Removed container margins so layout spans full width
- Made date column narrow and fixed action column width
- Email list padding removed to save space
- Updated backlog for completed UI scenarios

## 5th July 2025

- Added Gmail deeplink to sender and subject text in email list.
- Adjusted action column layout on mobile so buttons wrap into two rows.
- Documented new user story and updated backlog status.
- Narrowed mobile action column so buttons show in 3x2 layout
- Subject text over 50 characters now truncates with an ellipsis.
- Gmail links open the Gmail app on mobile devices when available.
- Added backlog entries for subject truncation and mobile Gmail app links.
- Implemented multi-user support using cookie-based IDs and SQLite database.
- Added database module and schema for tokens, tasks, senders and email statuses.
- Persist scan tasks and email classifications to SQLite.
- Gmail labels updated with scan-persist once stored.
- Fixed database import path and persist_label variable errors.
- Alert users to link Gmail if scanning without authentication.
- Fixed background worker to avoid using Flask context outside requests.
- Fixed /scan-status to retrieve tasks from the database if missing in memory.
- Frontend now alerts on backend errors and handles missing task data gracefully.
- Updated backlog status for resuming active scan tasks.
- Created reset_db.sh script to wipe and reinitialize SQLite database.
- Added detailed debug logging for task stages and Gmail API calls. Updated task progress in the database during scans.

### Additional 5th July 2025

- Added gmail_users table to map email addresses to user IDs.
- OAuth callback now checks for existing gmail_users entry and reuses the user ID if found.
- Updated database module with helpers to save and lookup Gmail addresses.
- Documented new user story for recognising Gmail accounts across browsers.
- Frontend now polls /scan-tasks every second to detect tasks started on other devices.
- Marked Gmail account recognition user story as DONE and documented new user story for cross-browser task detection.
- Updated confirm endpoint to run in a background thread and track progress while confirming.
- Frontend now polls /scan-status only when a task is active and resumes during confirmation.
- Marked active task detection user story as DONE and added story for confirmation progress tracking.
- Updated save_task to use UPSERT so tasks table keeps a single row per task.
- Frontend now merges pending status updates to stop flicker when clicking buttons.
- Updated backlog scenarios for Gmail account reuse and confirmation progress.
- Confirm endpoint now confirms all emails and only labels spam.
- Scan task worker skips emails already confirmed.
- /scan-tasks no longer returns closed tasks.
- Updated backlog scenarios for closed task filtering and confirmed email handling.
- Fixed confirm worker to store user_id before starting thread.

## 6th July 2025

- Extended `email_status` table to store subject, sender, date and whether a spam filter exists.
- Scan worker now loads unconfirmed emails from the database for the chosen date range and skips rescanning them.
- Confirm process checks for existing filters, handles "already exists" errors and updates the new `filter_created` flag.
- Added new user story about reusing unconfirmed email data.
- Removed `scan-persist` Gmail label and store scanned IDs in database.
- Fixed timezone handling in `get_unconfirmed_emails` to prevent runtime errors.
## 7th July 2025

- Fixed tasks table to update existing rows by storing task id in memory.
- Added database helper to load the latest active task and updated /scan-tasks to return only that task.
- Updated backlog with scenario for latest active task filtering.
- Frontend now continues polling when an active task is found on load and stops cleanly when tasks are closed.
- Status polling now kicks off immediately when an active task is loaded.

## 8th July 2025

- Added `refresh-senders` endpoint to fetch whitelist, spam and ignore senders in a separate task.
- Scan task now uses stored sender lists without re-downloading.
- Frontend gained a "Refresh Lists" button to trigger the new task.
- Documented new user story for refreshing sender lists.
- Added database helper to list all email IDs and skipped them when refreshing sender lists.

## 9th July 2025

- Added kind field for tasks in memory to distinguish scan and refresh operations.
- Frontend buttons now hide or show based on task state.
- Backend loads latest task kind by inspecting stage text.
- Documented new user story for task-based button visibility.
- Fixed refresh button visibility so no buttons show during a refresh task.
- Marked the action button visibility user story as done.
- Added Gmail whitelist search link in the header.
- Documented new user story for whitelist search.
- Simplified whitelist search URL for better mobile compatibility and marked the user story as done.
- Updated whitelist link to open the Gmail app on mobile using the googlegmail protocol.
