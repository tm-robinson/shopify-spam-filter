### Project Backlog

#### User Story: Configure Gmail account (DONE)
**Description:** As a user, I want to configure my Gmail and Outlook email accounts with the application so that I can process emails from these accounts.
**Test Scenarios:**
*   Successfully configure a Gmail account. (TODO)
*   Receive error messages for invalid credentials. (TODO)
*   Ensure that account configuration is persistent. (TODO)

#### User Story: Process emails to extract key information (DONE)
**Description:** As a user, I want the application to process my emails to extract key information such as sender, recipient, subject, and body content.
**Test Scenarios:**
*   Verify extracted text contains correct sender information. (TODO)
*   Verify extracted text contains correct recipient information. (TODO)
*   Verify extracted text contains correct subject information. (TODO)
*   Verify body content for various formats (plain text, HTML) is appropriately converted into clean text to send to the LLM (TODO)
*   Verify attachments are not extracted (TODO)

#### User Story: Send email information to LLM to identify emails to label (DONE)
**Description:** As a user, I want the application to utilize an LLM to perform deeper analysis on the email content, based on a prompt provided by the user, so emails can be correctly labelled.
**Test Scenarios:**
*   Verify successful application of user provided prompt to the email text. (TODO)
*   Verify that the LLM correctly flags emails as YES or NO. (TODO)
*   Verify that the LLM response can be parsed correctly. (TODO)

#### User Story: View processed email data in a user interface (DONE)
**Description:** As a user, I want to view the processed email data and the results of the AI analysis in a clear and intuitive user interface.
**Test Scenarios:**
*   Verify that the UI displays a list of processed emails. (TODO)
*   Verify that the UI displays the extracted information and analysis results. (TODO)

