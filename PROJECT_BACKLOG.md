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

#### User Story: Improved UI styling (TODO)

**Description:** As a user, I want chat messages shown as speech bubbles with expandable content and color-coded results, and email rows highlighted based on status for easier review.
**Test Scenarios:**

- Chat bubbles truncate long text with a "read more" link. (TODO)
- Assistant replies show red background for YES and green background for NO. (TODO)
- Email list rows have coloured backgrounds matching their status. (TODO)
- Chat log uses smaller font size for compact display. (TODO)

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

