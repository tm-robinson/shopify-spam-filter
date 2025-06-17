# Shopify Spam Filter

This project contains a simple Flask backend and React frontend to scan your Gmail inbox for Shopify spam emails. Emails are classified using the DeepSeek R1 model via OpenRouter.

## Setup

1. Set the Google OAuth client credentials as environment variables before running the backend:
   ```bash
   export GOOGLE_CLIENT_ID=your_client_id
   export GOOGLE_CLIENT_SECRET=your_client_secret
   ```
   The app will redirect you to sign in with Google and grant Gmail access.
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
5. Open the URL shown by the dev server in your browser. Link your Gmail account, enter your OpenRouter API key and scan emails.

To create a production build of the frontend, run `npm run build` inside `frontend/` and serve the generated `dist` directory.

Spam results are stored using the `shopify-spam` label in Gmail. Confirming choices will block senders and mark messages as spam in Gmail.
