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

#### User Story: Resume active scan tasks (TODO)

**Description:** As a user, I want the app to detect any running scan tasks when I reload the page so that I can continue watching progress without starting a new scan.

**Test Scenarios:**

- Reloading the page during a scan resumes polling and shows current progress. (TODO)

#### User Story: Keep results after scan completes (TODO)

**Description:** As a user, I want completed scan tasks to remain visible until I confirm my choices so that I can review the emails even after reloading the page.

**Test Scenarios:**

- Reloading the page after a scan finishes still shows the results until I click confirm. (TODO)
- Closed tasks are not returned when fetching active tasks. (TODO)

#### User Story: Persist manual status updates during scans (DONE)

**Description:** As a user, I want any status changes I make while a scan is running to remain saved so that the emails do not revert on the next refresh.

**Test Scenarios:**

- Changing an email status while a scan is running persists when the task status is fetched. (TODO)

#### User Story: Detailed scan progress (TODO)

**Description:** As a user, I want to see progress while the whitelist and ignore lists are fetched so I know the scan is still running.

**Test Scenarios:**

- Progress text updates while fetching whitelist emails. (TODO)
- Progress text updates while fetching ignore emails. (TODO)
- Confirm button shows a "confirming" state until the server responds. (TODO)
