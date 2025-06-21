from flask import Flask, request, jsonify, redirect
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import requests
import threading
import uuid

from dotenv import load_dotenv
load_dotenv()  # take environment variables

app = Flask(__name__)

# Paths for token and OpenRouter key
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token.json')
OPENROUTER_KEY_FILE = os.path.join(os.path.dirname(__file__), 'openrouter.key')

# in-memory store for background scan tasks
tasks = {}

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

@app.route('/')
def root():
    return "hi"

@app.route('/auth')
def auth():
    frontend = os.environ.get('FRONTEND_URL', 'http://localhost:5173/')
    print(f"frontend is {frontend}")
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=(f"{frontend}/oauth2callback"),
    )
    auth_url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(auth_url)

@app.route('/oauth2callback')
def oauth2callback():
    frontend = os.environ.get('FRONTEND_URL', 'http://localhost:5173/')
    print(f"frontend is {frontend}")
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=(f"{frontend}/oauth2callback"),
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())
    return redirect(frontend)

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

def get_label_id(service, name):
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    for lbl in labels:
        if lbl['name'].lower() == name.lower():
            return lbl['id']
    # create label if not exists
    label = service.users().labels().create(userId='me', body={'name': name}).execute()
    return label['id']

@app.route('/scan-emails', methods=['POST'])
def scan_emails():
    """Start a background scan task and return its id"""
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.get_json() or {}
    prompt = data.get('prompt', 'Identify shopify abandoned basket spam emails. Return yes or no.')
    days = int(data.get('days', 10))

    task_id = str(uuid.uuid4())
    tasks[task_id] = {'stage': 'queued', 'progress': 0, 'total': 0, 'emails': [], 'log': []}

    def worker():
        service = build('gmail', 'v1', credentials=creds)
        spam_label = get_label_id(service, 'shopify-spam')
        whitelist_label = get_label_id(service, 'whitelist')
        # gather whitelisted senders
        result = service.users().messages().list(userId='me', q='label:whitelist').execute()
        wmsgs = result.get('messages', [])
        whitelist = set()
        for m in wmsgs:
            md = service.users().messages().get(userId='me', id=m['id'], format='metadata', metadataHeaders=['From']).execute()
            sender = next((h['value'] for h in md['payload']['headers'] if h['name'].lower() == 'from'), '')
            whitelist.add(sender)

        tasks[task_id]['stage'] = 'fetching'
        query = f'label:inbox newer_than:{days}d'
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        tasks[task_id]['total'] = len(messages)
        openrouter_key = ''
        if os.path.exists(OPENROUTER_KEY_FILE):
            with open(OPENROUTER_KEY_FILE) as f:
                openrouter_key = f.read().strip()

        for idx, msg in enumerate(messages):
            tasks[task_id]['stage'] = 'processing'
            tasks[task_id]['progress'] = idx
            msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            label_ids = msg_detail.get('labelIds', [])

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

            status = 'not_spam'
            if whitelist_label in label_ids or sender in whitelist:
                status = 'whitelist'
            else:
                if openrouter_key:
                    data = {
                        'model': 'deepseek-chat',
                        'messages': [
                            {'role': 'system', 'content': prompt},
                            {'role': 'user', 'content': text_md}
                        ]
                    }
                    headers_req = {'Authorization': f'Bearer {openrouter_key}'}
                    try:
                        resp = requests.post('https://openrouter.ai/api/v1/chat/completions', json=data, headers=headers_req)
                        if resp.status_code == 200:
                            answer = resp.json()['choices'][0]['message']['content']
                            tasks[task_id]['log'].append({'role': 'system', 'content': prompt})
                            tasks[task_id]['log'].append({'role': 'user', 'content': text_md})
                            tasks[task_id]['log'].append({'role': 'assistant', 'content': answer})
                            if 'yes' in answer.lower():
                                status = 'spam'
                    except Exception:
                        pass

            if status == 'spam':
                service.users().messages().modify(userId='me', id=msg['id'], body={'addLabelIds': [spam_label], 'removeLabelIds': [whitelist_label]}).execute()
            elif status == 'whitelist':
                service.users().messages().modify(userId='me', id=msg['id'], body={'addLabelIds': [whitelist_label], 'removeLabelIds': [spam_label]}).execute()

            tasks[task_id]['emails'].append({'id': msg['id'], 'subject': subject, 'sender': sender, 'date': date, 'status': status})

        tasks[task_id]['progress'] = tasks[task_id]['total']
        tasks[task_id]['stage'] = 'done'

    threading.Thread(target=worker).start()
    return jsonify({'task_id': task_id})

@app.route('/scan-status/<task_id>')
def scan_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': 'not found'}), 404
    return jsonify(task)

@app.route('/update-status', methods=['POST'])
def update_status():
    creds = get_credentials()
    if not creds:
        return jsonify({'error': 'Not authenticated'}), 401
    service = build('gmail', 'v1', credentials=creds)
    msg_id = request.json['id']
    status = request.json['status']
    spam_label = get_label_id(service, 'shopify-spam')
    whitelist_label = get_label_id(service, 'whitelist')
    if status == 'spam':
        service.users().messages().modify(userId='me', id=msg_id, body={'addLabelIds': [spam_label], 'removeLabelIds': [whitelist_label]}).execute()
    elif status == 'whitelist':
        service.users().messages().modify(userId='me', id=msg_id, body={'addLabelIds': [whitelist_label], 'removeLabelIds': [spam_label]}).execute()
    else:
        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': [spam_label, whitelist_label]}).execute()
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
