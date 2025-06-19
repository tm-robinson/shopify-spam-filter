from flask import Flask, request, jsonify, redirect, url_for
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import requests

from dotenv import load_dotenv
load_dotenv()  # take environment variables

app = Flask(__name__)

# Paths for token and OpenRouter key
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')
OPENROUTER_KEY_FILE = os.path.join(os.path.dirname(__file__), 'openrouter.key')

# Google OAuth client credentials
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
CLIENT_CONFIG = {
    'web': {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
    }
}

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

@app.route('/auth')
def auth():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True),
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
    return redirect('/')

@app.route('/openrouter-key', methods=['POST'])
def save_openrouter_key():
    key = request.json.get('key')
    with open(OPENROUTER_KEY_FILE, 'w') as f:
        f.write(key)
    return ('', 204)

def get_credentials():
    if not os.path.exists(TOKEN_FILE):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return creds

@app.route('/scan-emails', methods=['POST'])
def scan_emails():
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    service = build('gmail', 'v1', credentials=creds)

    query = 'label:inbox -label:shopify-spam newer_than:30d'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    openrouter_key = ''
    if os.path.exists(OPENROUTER_KEY_FILE):
        with open(OPENROUTER_KEY_FILE) as f:
            openrouter_key = f.read().strip()

    processed = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_detail.get('payload', {})
        headers = payload.get('headers', [])
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

        parts = payload.get('parts', [])
        body = ''
        if 'body' in payload and 'data' in payload['body']:
            body = payload['body']['data']
        elif parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body = part['body'].get('data', '')
                    break
        if body:
            import base64
            body = base64.urlsafe_b64decode(body).decode('utf-8', errors='ignore')
        text_md = f"Subject: {subject}\nFrom: {sender}\n\n{body}"

        spam = False
        if openrouter_key:
            prompt = request.json.get('prompt', 'Identify shopify abandoned basket spam emails. Return yes or no.')
            data = {
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': text_md}
                ]
            }
            headers = {'Authorization': f'Bearer {openrouter_key}'}
            try:
                resp = requests.post('https://openrouter.ai/api/v1/chat/completions', json=data, headers=headers)
                if resp.status_code == 200:
                    content = resp.json()['choices'][0]['message']['content'].lower()
                    spam = 'yes' in content
            except Exception:
                pass

        if spam:
            service.users().messages().modify(userId='me', id=msg['id'], body={'addLabelIds': ['Label_1']}).execute()
        processed.append({'id': msg['id'], 'subject': subject, 'sender': sender, 'date': date, 'spam': spam})

    return jsonify(processed)

@app.route('/toggle-label', methods=['POST'])
def toggle_label():
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    service = build('gmail', 'v1', credentials=creds)
    msg_id = request.json['id']
    spam = request.json['spam']
    if spam:
        service.users().messages().modify(userId='me', id=msg_id, body={'addLabelIds': ['Label_1']}).execute()
    else:
        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['Label_1']}).execute()
    return ('', 204)

@app.route('/confirm', methods=['POST'])
def confirm():
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    service = build('gmail', 'v1', credentials=creds)
    ids = request.json.get('ids', [])
    for msg_id in ids:
        msg = service.users().messages().get(userId='me', id=msg_id, format='metadata', metadataHeaders=['From']).execute()
        sender = next((h['value'] for h in msg['payload']['headers'] if h['name'].lower() == 'from'), '')
        # Add to block list
        service.users().settings().filters().create(userId='me', body={
            'criteria': {'from': sender},
            'action': {'addLabelIds': ['SPAM'], 'removeLabelIds': []}
        }).execute()
        service.users().messages().modify(userId='me', id=msg_id, body={'addLabelIds': ['SPAM']}).execute()
    return ('', 204)

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc')
