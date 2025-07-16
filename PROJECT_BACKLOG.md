### Project Backlog

#### User Story: Configure Gmail account (DONE)

**Description:** As a user, I want to configure my Gmail and Outlook email accounts with the application so that I can process emails from these accounts.
**Test Scenarios:**

- Successfully configure a Gmail account. (TODO)
- Receive error messages for invalid credentials. (TODO)
- Ensure that account configuration is persistent. (TODO)

#### User Story: Process emails to extract key information (DONE)

**Description:** As a user, I want the application to process my emails to extract key information such as sender, recipient, subject, and body content.
**Test Scenarios:**

- Verify extracted text contains correct sender information. (TODO)
- Verify extracted text contains correct recipient information. (TODO)
- Verify extracted text contains correct subject information. (TODO)
- Verify body content for various formats (plain text, HTML) is appropriately converted into clean text to send to the LLM (TODO)
- Verify attachments are not extracted (TODO)

#### User Story: Send email information to LLM to identify emails to label (DONE)

**Description:** As a user, I want the application to utilize an LLM to perform deeper analysis on the email content, based on a prompt provided by the user, so emails can be correctly labelled.
**Test Scenarios:**

- Verify successful application of user provided prompt to the email text. (TODO)
- Verify that the LLM correctly flags emails as YES or NO. (TODO)
- Verify that the LLM response can be parsed correctly. (TODO)

#### User Story: View processed email data in a user interface (DONE)

**Description:** As a user, I want to view the processed email data and the results of the AI analysis in a clear and intuitive user interface.
**Test Scenarios:**

- Verify that the UI displays a list of processed emails. (TODO)
- Verify that the UI displays the extracted information and analysis results. (TODO)

#### User Story: Ignore emails by sender using Gmail label (DONE)

**Description:** As a user, I want to mark emails as "ignore" so that future emails from the same sender are skipped and not sent to the LLM.
**Test Scenarios:**

- Mark an email as ignore and verify the "spam-filter-ignore" label is added. (TODO)
- New emails from the ignored sender are automatically marked as ignored. (TODO)

#### User Story: Confirm spam emails without SPAM label (DONE)

**Description:** As a user, I want confirming spam emails to label them `shopify-spam` and remove them from the inbox because Gmail's API does not allow adding the `SPAM` label directly.

**Test Scenarios:**

- Confirming a spam email adds the `shopify-spam` label and removes the `INBOX` label. (TODO)
- A filter is created to automatically label future emails from the sender with `shopify-spam`. (TODO)

#### User Story: Improved UI styling (DONE)

**Description:** As a user, I want a modern, mobile friendly interface with fixed controls at the top, compact email rows with sender and subject together, circular action buttons and expandable LLM details for each email.
**Test Scenarios:**

- Confirm button is fixed at the top with other controls. (DONE)
- Email list scrolls beneath the header on mobile screens. (DONE)
- "i" buttons toggle the LLM request and response for each email. (DONE)
- Action buttons use circular icons and keep their colours. (DONE)
- Email rows show a short date format and avoid horizontal scrolling on mobile. (DONE)
- Page width fits on mobile screens. (DONE)
- Layout expands on desktop screens for better readability. (DONE)
- Default scan range is 3 days. (DONE)
- Date and action columns use minimal width so the email column expands. (DONE)

#### User Story: Backend config for API key and polling (TODO)

**Description:** As a user, I want the OpenRouter API key and polling interval stored in configuration files instead of the UI so the interface stays uncluttered.

**Test Scenarios:**

- Backend loads the API key from environment variables or `openrouter.key`. (TODO)
- Poll interval comes from an environment variable. (TODO)

#### User Story: Filter email list by status (TODO)

**Description:** As a user, I want to quickly show or hide emails in each status category so I can focus on the ones that matter.

**Test Scenarios:**

- Clicking a filter button toggles visibility of that status. (TODO)

#### User Story: Open Gmail messages from list (DONE)

**Description:** As a user, I want to open the original Gmail message by clicking the sender or subject in the email list so that I can review it quickly.

**Test Scenarios:**

- Clicking the sender or subject opens the Gmail message in a new tab. (TODO)

#### User Story: Truncate long subject lines (TODO)

**Description:** As a user, I want long subject text shortened in the email list so that it fits neatly on mobile screens.

**Test Scenarios:**

- Subjects longer than 50 characters display only the first 50 characters followed by `...`. (TODO)
- Subjects 50 characters or shorter display in full. (TODO)

#### User Story: Open Gmail app on mobile (TODO)

**Description:** As a mobile user, I want clicking the sender or subject to launch the Gmail app if installed so viewing messages is smoother.

**Test Scenarios:**

- On phones, links open the Gmail app when available. (TODO)
- On desktop browsers the link opens in a new tab. (TODO)

#### User Story: Persist last used scan prompt (DONE)

**Description:** As a user, I want the application to remember the last prompt I used when scanning emails so that it is pre-filled the next time I open the app.

**Test Scenarios:**

- Save the prompt on the backend when scanning emails. (TODO)
- Retrieve the saved prompt from the backend and display it in the textarea on load. (TODO)

#### User Story: Clean chat log display (TODO)

**Description:** As a user, I want the chat log to hide system prompts and strip
result tags from assistant replies so that the conversation is easier to read.

**Test Scenarios:**

- System messages are not displayed in the chat log. (TODO)
- <RESULT> tags are removed from assistant replies. (TODO)

#### User Story: Retrieve all Gmail messages (DONE)

**Description:** As a user, I want the application to fetch all matching Gmail messages using pagination so that no results are missed.

**Test Scenarios:**

- More than 100 results are returned when querying messages and all are processed. (TODO)
- Whitelist and ignore lists are fully retrieved across pages. (TODO)

#### User Story: Fetch Gmail messages in batches (DONE)

**Description:** As a user, I want message details retrieved using Gmail batch requests so that scans run faster.

**Test Scenarios:**

- Metadata for whitelist and ignore lists is fetched via batch calls. (TODO)
- Message bodies are retrieved in batches during scanning. (TODO)

#### User Story: Retry failed batch fetches (DONE)

**Description:** As a user, I want batch requests to retry with exponential
backoff when Gmail returns rate limit errors so that message details are
reliably fetched.

**Test Scenarios:**

- When some batch items fail with 429 errors, the helper retries until all
  messages are retrieved. (TODO)

#### User Story: Resume active scan tasks (DONE)

**Description:** As a user, I want the app to detect any running scan tasks when I reload the page so that I can continue watching progress without starting a new scan.

**Test Scenarios:**

- Reloading the page during a scan resumes polling and shows current progress. (DONE)

#### User Story: Keep results after scan completes (TODO)

**Description:** As a user, I want completed scan tasks to remain visible until I confirm my choices so that I can review the emails even after reloading the page.

**Test Scenarios:**

- Reloading the page after a scan finishes still shows the results until I click confirm. (TODO)
- Closed tasks are not returned when fetching active tasks. (DONE)
- Only the most recent active task is returned when fetching active tasks. (DONE)

#### User Story: Persist manual status updates during scans (DONE)

**Description:** As a user, I want any status changes I make while a scan is running to remain saved so that the emails do not revert on the next refresh.

**Test Scenarios:**

- Changing an email status while a scan is running persists when the task status is fetched. (DONE)

#### User Story: Detailed scan progress (TODO)

**Description:** As a user, I want to see progress while the whitelist and ignore lists are fetched so I know the scan is still running.

**Test Scenarios:**

- Progress text updates while fetching whitelist emails. (TODO)
- Progress text updates while fetching ignore emails. (TODO)
- Confirm button shows a "confirming" state until the server responds. (TODO)

#### User Story: Multi-user support with persistent storage (DONE)

**Description:** As a user I want my Gmail token, scan tasks and results stored separately so multiple users can use the app.

**Test Scenarios:**

- Returning to the site preserves my Gmail link via cookie. (TODO)
- Scan tasks are loaded from the database on refresh. (DONE)
- Confirmed emails are not scanned again. (DONE)

#### User Story: Recognise Gmail account across browsers (DONE)

**Description:** As a user, I want linking Gmail from a new browser to restore
my existing account by matching the Gmail address so that my saved tasks and
labels remain accessible.

**Test Scenarios:**

- Linking Gmail with an address that already exists reuses the previous
  `user_id` cookie. (DONE)

#### User Story: Detect active tasks across browsers (DONE)

**Description:** As a user, I want the UI to automatically show progress for any running scan task started on another device or tab so that I don't have to start a new scan.

**Test Scenarios:**

- Opening the app on a second device while a scan is running begins polling automatically. (DONE)

#### User Story: Confirmation progress tracking (TODO)

**Description:** As a user, I want the task to show a confirming stage with progress so I know how many emails are finalised when I click confirm.

**Test Scenarios:**

- Task stage switches to "confirming" when the confirm button is pressed. (DONE)
- Progress increases as each email is confirmed. (DONE)

#### User Story: Hide confirmed emails during confirmation (DONE)

**Description:** As a user, I want emails to disappear from the list as they are confirmed so that I can't change their status once processing has finished.

**Test Scenarios:**

- Polling `/scan-status/<id>` excludes emails that have already been confirmed. (DONE)

#### User Story: Reset the database (TODO)

**Description:** As a developer, I want a simple script to clear the SQLite database so I can start fresh during testing.

**Test Scenarios:**

- Running `reset_db.sh` removes any existing data and recreates the schema. (TODO)

#### User Story: Enhanced debug logging (DONE)

**Description:** As a developer, I want detailed debug logs and real-time task status updates so that troubleshooting is easier.

**Test Scenarios:**

- Stage transitions are logged with task id. (TODO)
- Gmail API requests are logged at debug level. (TODO)
- Task stage in the database updates as progress occurs. (TODO)

#### User Story: Reuse unconfirmed email data (DONE)

**Description:** As a user, I want emails that were scanned previously but not confirmed to appear in new scans so I can update their status without rescanning them. The system should also record when a spam filter has been created for a sender.

**Test Scenarios:**

- Scanning with a date range that overlaps previous scans lists those unconfirmed emails. (DONE)
- Creating a filter that already exists marks the email as having the filter created. (DONE)

#### User Story: Sort scan results by date (DONE)

**Description:** As a user, I want emails from previous scans mixed with new ones in chronological order so older entries don't appear first.

**Test Scenarios:**

- Emails returned from `/scan-status/<id>` are ordered by their received date regardless of when they were scanned. (DONE)

#### User Story: Prevent duplicate scan results (DONE)

**Description:** As a user, I want each email to appear only once in the list even when data comes from both the current scan and the database.

**Test Scenarios:**

- `/scan-status/<id>` never returns the same email id twice. (DONE)

#### User Story: Track scanned emails in the database (DONE)

**Description:** As a developer, I want scanned email IDs stored in the database instead of applying the `scan-persist` Gmail label so the inbox view remains clean.

**Test Scenarios:**

- Scanning emails does not add the `scan-persist` label. (TODO)
- Emails already stored in `email_status` are skipped on subsequent scans. (TODO)

#### User Story: Refresh sender lists on demand (DONE)

**Description:** As a user, I want to refresh my whitelist, spam and ignore sender lists manually so regular scans are faster.

**Test Scenarios:**

- Clicking the "Refresh Lists" button starts a background task. (DONE)
- Scanning emails no longer re-fetches these lists from Gmail. (DONE)

#### User Story: Skip duplicate sender fetches (DONE)

**Description:** As a developer, I want the refresh process to ignore emails that are already stored in the database so updating sender lists is faster.

**Test Scenarios:**

- Email IDs already in `email_status` are not fetched again from Gmail. (TODO)
- New emails with labels are stored in `email_status` with `confirmed = 0`. (TODO)

#### User Story: Action buttons depend on task state (DONE)

**Description:** As a user, I want the scan, confirm and refresh buttons to appear only when it makes sense so I don't start conflicting tasks.

**Test Scenarios:**

- Confirm button only shows when the latest task is done. (TODO)
- Scan Emails button hides if any task is running. (TODO)
- Refresh Lists button hides during a scan task. (TODO)
- Scan Emails and Confirm hide during a refresh task. (TODO)
- Refresh Lists button hides during a refresh task. (TODO)

#### User Story: Link to whitelist search (DONE)

**Description:** As a user, I want a direct link in the app header that opens Gmail with all whitelisted emails so I can review them quickly.

**Test Scenarios:**

- Clicking the link opens Gmail showing `label:whitelist` results in the web client on any platform. (TODO)

#### User Story: Manage sender list (TODO)

**Description:** As a user, I want to view and remove senders flagged as whitelist, spam or ignore so I can correct mistakes.

**Test Scenarios:**

- Manage page lists senders for each status. (TODO)
- Filter buttons show only whitelist, spam or ignore senders. (TODO)
- Clicking the trashcan removes the sender and unconfirms related emails. (TODO)

#### User Story: View task logs and clear tasks (DONE)

**Description:** As a user, I want to see backend logs for my account and remove stuck tasks so I can troubleshoot issues.

**Test Scenarios:**

- Clicking "View Logs" shows log lines since the last restart. (TODO)
- Clicking "Clear Task" removes the current task from the UI and database. (TODO)
- `/scan-status/<id>` returns a summary when a task completes so the UI can alert me. (TODO)
- Log lines wrap without horizontal scrolling. (TODO)
- Logs update every second while the dialog is open. (TODO)
- Logs auto-scroll to the bottom when already scrolled to the bottom. (TODO)
- /logs endpoint omits its own request and response logs. (TODO)
