# Shopify Spam Filter

This project contains a simple Flask backend and React frontend to scan your Gmail inbox for Shopify spam emails. Emails are classified using the DeepSeek R1 model via OpenRouter.

## Setup

1. Create Google API credentials for Gmail and place the `credentials.json` file in `backend/` (this file is ignored by git).
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install frontend dependencies (optional if using a simple web server):
   Open `frontend/index.html` in a browser or serve the `frontend` folder with any web server.
4. Run the backend:
   ```bash
   python backend/app.py
   ```
5. Open `frontend/index.html` in your browser. Link your Gmail account, enter your OpenRouter API key and scan emails.

Spam results are stored using the `shopify-spam` label in Gmail. Confirming choices will block senders and mark messages as spam in Gmail.
