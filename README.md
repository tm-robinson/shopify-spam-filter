# Shopify Spam Filter

This project contains a simple Flask backend and React frontend to scan your Gmail inbox for Shopify spam emails. Emails are classified using the DeepSeek R1 model via OpenRouter.

## Setup

1. Obtain Google OAuth credentials and set them as environment variables:

   1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
   2. Create a project and enable the **Gmail API**.
   3. Configure the OAuth consent screen (External user type is sufficient).
   4. Create **OAuth client ID** credentials of type **Web application** and add
      `http://localhost:5000/oauth2callback` as an authorised redirect URI.
   5. Copy the generated _Client ID_ and _Client Secret_ and export them before
      running the backend:
      ```bash
      export GOOGLE_CLIENT_ID=<client-id>
      export GOOGLE_CLIENT_SECRET=<client-secret>
      ```
   6. Add your gmail account to the list of "test users" within the OAuth Client settings in the Audience tab.

   When you start the app it will redirect you to Google to grant Gmail access.

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install frontend dependencies and run the dev server:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
4. In a separate terminal, run the backend:
   ```bash
   python backend/app.py
   ```
   Set `FRONTEND_URL` if your React dev server runs on a different URL (default `http://localhost:5173/`).
5. Open the URL shown by the dev server in your browser. Link your Gmail account and scan emails. The backend reads the OpenRouter API key from `OPENROUTER_API_KEY` or `backend/openrouter.key`. If you reload the page while a scan is running, the app will reconnect and keep showing progress.

To create a production build of the frontend, run `npm run build` inside `frontend/` and serve the generated `dist` directory.

Spam results are stored using the `shopify-spam` label in Gmail. Confirming choices will label messages as `shopify-spam` and remove them from the inbox.

## Resetting the Database

Run `./reset_db.sh` to delete `backend/data.db` and recreate an empty database using `schema.sql`. This is helpful when testing changes from a clean state.
