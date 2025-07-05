from flask import Flask, request, jsonify, redirect, g
import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests
import threading
import uuid
import base64
from bs4 import BeautifulSoup
import datetime
import re
import time

from dotenv import load_dotenv

import database

load_dotenv()  # take environment variables

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = app.logger
logger.setLevel(logging.DEBUG)

# CODEX: Initialize database and manage user identity cookie
database.init_db()


@app.before_request
def assign_user():
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        g.new_user = True
    else:
        g.new_user = False
    g.user_id = user_id


@app.after_request
def set_user_cookie(resp):
    if getattr(g, "new_user", False):
        resp.set_cookie("user_id", g.user_id)
    return resp


# CODEX: Initialize database and manage user identity cookie
database.init_db()


@app.before_request
def assign_user():
    user_id = request.cookies.get("user_id")
    if not user_id:
        user_id = str(uuid.uuid4())
        g.new_user = True
    else:
        g.new_user = False
    g.user_id = user_id


@app.after_request
def set_user_cookie(resp):
    if getattr(g, "new_user", False):
        resp.set_cookie("user_id", g.user_id)
    return resp


# Paths for token and OpenRouter key
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token.json")
OPENROUTER_KEY_FILE = os.path.join(os.path.dirname(__file__), "openrouter.key")
# CODEX: Added constant for storing last used prompt
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "last_prompt.json")

# in-memory store for background scan tasks
tasks = {}


def update_task_email_status(msg_id: str, status: str) -> None:
    """Update status of a message within any running scan task."""
    for info in tasks.values():
        for email in info.get("emails", []):
            if email.get("id") == msg_id:
                # CODEX: Persist manual status updates during a scan
                email["status"] = status


# Google OAuth client credentials
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.settings.basic",
]


@app.route("/")
def root():
    return "hi"


@app.route("/auth")
def auth():
    frontend = os.environ.get("FRONTEND_URL", "http://localhost:5173/")
    print(f"frontend is {frontend}")
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=(f"{frontend}/oauth2callback"),
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
    frontend = os.environ.get("FRONTEND_URL", "http://localhost:5173/")
    print(f"frontend is {frontend}")
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=(f"{frontend}/oauth2callback"),
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    # CODEX: Save token in the database linked to the user id
    database.save_token(g.user_id, creds.to_json())
    return redirect(frontend)


@app.route("/last-prompt")
def last_prompt():
    """Return the most recently used prompt"""
    return jsonify({"prompt": load_last_prompt()})


def get_credentials():
    """Load OAuth credentials for the current user."""
    token_json = database.load_token(g.user_id)
    if not token_json:
        return None
    try:
        info = json.loads(token_json)
        if "refresh_token" not in info:
            logger.warning("token missing refresh_token")
            return None
        creds = Credentials.from_authorized_user_info(info, SCOPES)
        return creds
    except Exception as e:
        logger.error("Failed to load credentials: %s", e)
        return None


# CODEX: Persist last used prompt between sessions
def load_last_prompt():
    if os.path.exists(PROMPT_FILE):
        try:
            with open(PROMPT_FILE) as f:
                data = json.load(f)
                return data.get("prompt", "")
        except Exception as e:
            logger.error("Failed to load prompt: %s", e)
    return ""


def save_last_prompt(prompt: str) -> None:
    try:
        with open(PROMPT_FILE, "w") as f:
            json.dump({"prompt": prompt}, f)
    except Exception as e:
        logger.error("Failed to save prompt: %s", e)


def get_label_id(service, name):
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    for lbl in labels:
        if lbl["name"].lower() == name.lower():
            return lbl["id"]
    # create label if not exists
    label = service.users().labels().create(userId="me", body={"name": name}).execute()
    return label["id"]


# CODEX: Added helper to fetch all messages across pages
def list_all_messages(service, user_id="me", q=None):
    """Return all messages for the given query handling pagination."""
    messages = []
    page_token = None
    logger.info(f"Fetching messages from gmail for query {q}")
    while True:
        params = {"userId": user_id, "q": q}
        if page_token:
            params["pageToken"] = page_token
        logger.debug("Gmail request: list messages %s", params)
        resp = service.users().messages().list(**params).execute()
        logger.debug("Gmail response: %s", resp)
        messages.extend(resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    logger.info("Retrieved %d messages from gmail", len(messages))
    return messages


# CODEX: Added helper to fetch message details using Gmail batch requests
def batch_get_messages(
    service,
    ids,
    *,
    fmt="full",
    metadata_headers=None,
    batch_size=20,
    max_attempts=20,
):
    """Return message details for given ids using batch requests with retries."""
    headers = metadata_headers or []
    remaining = list(ids)
    results = {}
    attempt = 1

    while remaining and attempt < max_attempts:
        failed = []
        for i in range(0, len(remaining), batch_size):
            chunk = remaining[i : i + batch_size]  # noqa: E203
            failed_chunk = []

            def callback(request_id, response, exception, fc=failed_chunk):
                if exception:
                    logger.warning(
                        "Batch fetch error for %s: %s", request_id, exception
                    )
                    fc.append(request_id)
                else:
                    results[request_id] = response

            batch = service.new_batch_http_request()
            for msg_id in chunk:
                req = (
                    service.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg_id,
                        format=fmt,
                        metadataHeaders=headers,
                    )
                )
                batch.add(req, request_id=msg_id, callback=callback)
            try:
                batch.execute()
            except HttpError as e:
                if e.resp.status == 429:
                    logger.warning("Batch execution rate limited: %s", e)
                    failed_chunk.extend(chunk)
                else:
                    logger.error("Failed to execute batch: %s", e)
            failed.extend(failed_chunk)

        remaining = failed
        if remaining:
            sleep = 2**attempt  # exponential backoff
            logger.info(
                "Retrying %d failed message fetches in %d seconds",
                len(remaining),
                sleep,
            )
            time.sleep(sleep)
        attempt += 1

    if remaining:
        logger.error(
            "Failed to fetch %d messages after %d attempts",
            len(remaining),
            attempt,
        )

    return results


# Recursively extract the text or html body from a message payload.
def extract_email_body(payload):
    """Return decoded plain text body prioritising HTML."""

    def collect_parts(part, results):
        if (
            part.get("mimeType") in ("text/plain", "text/html")
            and not part.get("filename")
            and "body" in part
        ):
            data = part["body"].get("data")
            if data:
                text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                results.append((text, part.get("mimeType")))
        for sub in part.get("parts", []):
            collect_parts(sub, results)

    def html_to_plain_text(html: str) -> str:
        """Convert HTML to plain text stripping formatting and links."""
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a"):
            a.replace_with(a.get_text())
        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    parts = []
    collect_parts(payload, parts)

    html_part = next((t for t, m in parts if m == "text/html"), None)
    if html_part:
        body = html_to_plain_text(html_part)
        logger.debug(f"body is html: {body}")
        return body, "text/html"

    text_part = next((t for t, m in parts if m == "text/plain"), None)
    if text_part:
        text_part = re.sub(r"https?://\S+", "", text_part)
        text_part = re.sub(r"\s+", " ", text_part).strip()
        logger.debug(f"body is plaintext: {text_part}")
        return text_part, "text/plain"

    return "", ""


@app.route("/scan-emails", methods=["POST"])
def scan_emails():
    """Start a background scan task and return its id"""
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authenticated"}), 401

    data = request.get_json() or {}
    prompt = data.get("prompt", "Describe what emails to identify")
    # CODEX: Save the prompt for future sessions
    save_last_prompt(prompt)
    days = int(data.get("days", 3))  # CODEX: scan 3 days by default
    date_after = datetime.datetime.now() - datetime.timedelta(days=days)

    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "user_id": g.user_id,
        "stage": "queued",
        "progress": 0,
        "total": 0,
        "emails": [],
        "log": [],
    }
    database.save_task(
        {
            "id": task_id,
            "user_id": g.user_id,
            "stage": "queued",
            "progress": 0,
            "total": 0,
            "emails": [],
            "log": [],
        }
    )
    logger.info("Starting scan task %s for last %s days", task_id, days)

    user_id = g.user_id

    def worker():
        try:
            whitelist = set(database.get_senders(user_id, "whitelist"))
            ignorelist = set(database.get_senders(user_id, "ignore"))
            spamlist = set(database.get_senders(user_id, "spam"))
            confirmed_ids = set(database.get_confirmed_emails(user_id))
            service = build("gmail", "v1", credentials=creds)
            spam_label = get_label_id(service, "shopify-spam")
            whitelist_label = get_label_id(service, "whitelist")
            ignore_label = get_label_id(service, "spam-filter-ignore")
            persist_label = get_label_id(service, "scan-persist")
            # gather whitelisted senders
            logger.debug("Gmail request: list whitelist emails")
            tasks[task_id]["stage"] = "listing whitelist emails"
            wmsgs = list_all_messages(service, q="label:whitelist -label:scan-persist")
            tasks[task_id]["stage"] = "fetching whitelist emails"
            tasks[task_id]["progress"] = 0
            tasks[task_id]["total"] = len(wmsgs)
            if wmsgs:
                ids = [m["id"] for m in wmsgs]
                details = batch_get_messages(
                    service,
                    ids,
                    fmt="metadata",
                    metadata_headers=["From"],
                )
                for idx, msg_id in enumerate(ids):
                    tasks[task_id]["progress"] = idx + 1
                    md = details.get(msg_id)
                    if not md:
                        continue
                    sender = next(
                        (
                            h["value"]
                            for h in md["payload"]["headers"]
                            if h["name"].lower() == "from"
                        ),
                        "",
                    )
                    whitelist.add(sender)
                    database.save_sender(user_id, sender, "whitelist")
                    service.users().messages().modify(
                        userId="me",
                        id=msg_id,
                        body={"addLabelIds": [persist_label]},
                    ).execute()

            # gather ignored senders
            logger.debug("Gmail request: list ignore emails")
            tasks[task_id]["stage"] = "listing ignore emails"
            imsgs = list_all_messages(
                service, q="label:spam-filter-ignore -label:scan-persist"
            )
            tasks[task_id]["stage"] = "fetching ignore emails"
            tasks[task_id]["progress"] = 0
            tasks[task_id]["total"] = len(imsgs)
            if imsgs:
                ids = [m["id"] for m in imsgs]
                details = batch_get_messages(
                    service,
                    ids,
                    fmt="metadata",
                    metadata_headers=["From"],
                )
                for idx, msg_id in enumerate(ids):
                    tasks[task_id]["progress"] = idx + 1
                    md = details.get(msg_id)
                    if not md:
                        continue
                    sender = next(
                        (
                            h["value"]
                            for h in md["payload"]["headers"]
                            if h["name"].lower() == "from"
                        ),
                        "",
                    )
                    ignorelist.add(sender)
                    database.save_sender(user_id, sender, "ignore")
                    service.users().messages().modify(
                        userId="me",
                        id=msg_id,
                        body={"addLabelIds": [persist_label]},
                    ).execute()

            # gather previously labelled spam senders
            s_msgs = list_all_messages(
                service, q="label:shopify-spam -label:scan-persist"
            )
            if s_msgs:
                ids = [m["id"] for m in s_msgs]
                details = batch_get_messages(
                    service,
                    ids,
                    fmt="metadata",
                    metadata_headers=["From"],
                )
                for msg_id in ids:
                    md = details.get(msg_id)
                    if not md:
                        continue
                    sender = next(
                        (
                            h["value"]
                            for h in md["payload"]["headers"]
                            if h["name"].lower() == "from"
                        ),
                        "",
                    )
                    spamlist.add(sender)
                    database.save_sender(user_id, sender, "spam")
                    service.users().messages().modify(
                        userId="me",
                        id=msg_id,
                        body={"addLabelIds": [persist_label]},
                    ).execute()

            tasks[task_id]["stage"] = "fetching"

            query = f"after:{date_after.strftime('%Y-%m-%d')} in:inbox is:unread label:inbox"

            messages = list_all_messages(service, q=query)

            tasks[task_id]["total"] = len(messages)
            logger.info("messages length is currently %d ", tasks[task_id]["total"])
            openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
            if not openrouter_key and os.path.exists(OPENROUTER_KEY_FILE):
                with open(OPENROUTER_KEY_FILE) as f:
                    openrouter_key = f.read().strip()

            # CODEX: Fetch and process messages in batches to minimize waiting
            BATCH_SIZE = 25
            for start in range(0, len(messages), BATCH_SIZE):
                msg_batch = messages[start : start + BATCH_SIZE]  # noqa: E203
                ids = [m["id"] for m in msg_batch]
                msg_details = batch_get_messages(
                    service,
                    ids,
                    fmt="full",
                )

                for offset, msg in enumerate(msg_batch):
                    idx = start + offset
                    tasks[task_id]["stage"] = "processing"
                    tasks[task_id]["progress"] = idx
                    msg_detail = msg_details.get(msg["id"])
                    if not msg_detail:
                        logger.error("No details returned for %s", msg["id"])
                        continue
                    payload = msg_detail.get("payload", {})
                    headers = payload.get("headers", [])
                    subject = next(
                        (h["value"] for h in headers if h["name"].lower() == "subject"),
                        "",
                    )
                    sender = next(
                        (h["value"] for h in headers if h["name"].lower() == "from"),
                        "",
                    )
                    date = next(
                        (h["value"] for h in headers if h["name"].lower() == "date"),
                        "",
                    )
                    label_ids = msg_detail.get("labelIds", [])

                    body, _ = extract_email_body(payload)
                    words = body.split()
                    body_preview = " ".join(words[:500])
                    text_md = f"Subject: {subject}\nFrom: {sender}\n\n{body_preview}"

                    status = "not_spam"
                    llm_sent = False
                    answer = ""
                    if (
                        msg["id"] in confirmed_ids
                        or sender in spamlist
                        or spam_label in label_ids
                    ):
                        status = "spam"
                    elif ignore_label in label_ids or sender in ignorelist:
                        status = "ignore"
                    elif whitelist_label in label_ids or sender in whitelist:
                        status = "whitelist"
                    else:
                        if openrouter_key:
                            data = {
                                "model": "deepseek/deepseek-chat-v3-0324:free",
                                "messages": [
                                    {
                                        "role": "system",
                                        "content": (
                                            prompt
                                            + (
                                                " Start your response with "
                                                "<RESULT>YES</RESULT> or "
                                                "<RESULT>NO</RESULT> followed by "
                                                "the justification for "
                                                "your answer."
                                            )
                                        ),
                                    },
                                    {"role": "user", "content": text_md},
                                ],
                            }
                            headers_req = {"Authorization": f"Bearer {openrouter_key}"}
                            try:
                                logger.debug("OpenRouter request: %s", data)
                                start_time = time.time()
                                resp = requests.post(
                                    "https://openrouter.ai/api/v1/" "chat/completions",
                                    json=data,
                                    headers=headers_req,
                                )
                                logger.debug(
                                    "OpenRouter response %s: %s",
                                    resp.status_code,
                                    resp.text,
                                )
                                logger.info(
                                    "OpenRouter response %s received %d characters after %.2f seconds",
                                    resp.status_code,
                                    len(resp.text),
                                    time.time() - start_time,
                                )
                                if resp.status_code == 200:
                                    answer = resp.json()["choices"][0]["message"][
                                        "content"
                                    ]
                                    tasks[task_id]["log"].append(
                                        {"role": "system", "content": prompt}
                                    )
                                    tasks[task_id]["log"].append(
                                        {"role": "user", "content": text_md}
                                    )
                                    tasks[task_id]["log"].append(
                                        {
                                            "role": "assistant",
                                            "content": answer,
                                        }
                                    )
                                    if "yes" in answer.lower():
                                        status = "spam"
                                    llm_sent = True
                                else:
                                    logger.error(
                                        "OpenRouter error: %s - %s",
                                        resp.status_code,
                                        resp.text,
                                    )
                            except Exception:
                                pass

                    if status == "spam":
                        logger.debug("Gmail request: add spam label to %s", msg["id"])
                        service.users().messages().modify(
                            userId="me",
                            id=msg["id"],
                            body={
                                "addLabelIds": [spam_label],
                                "removeLabelIds": [whitelist_label],
                            },
                        ).execute()
                    elif status == "whitelist":
                        logger.debug(
                            "Gmail request: add whitelist label to %s",
                            msg["id"],
                        )
                        service.users().messages().modify(
                            userId="me",
                            id=msg["id"],
                            body={
                                "addLabelIds": [whitelist_label],
                                "removeLabelIds": [spam_label],
                            },
                        ).execute()
                    elif status == "ignore":
                        logger.debug("Gmail request: add ignore label to %s", msg["id"])
                        service.users().messages().modify(
                            userId="me",
                            id=msg["id"],
                            body={
                                "addLabelIds": [ignore_label],
                                "removeLabelIds": [
                                    spam_label,
                                    whitelist_label,
                                ],
                            },
                        ).execute()

                    tasks[task_id]["emails"].append(
                        {
                            "id": msg["id"],
                            "subject": subject,
                            "sender": sender,
                            "date": date,
                            "status": status,
                            "request": text_md if llm_sent else "",
                            "response": answer if llm_sent else "",
                            "llm_sent": llm_sent,
                        }
                    )
                    database.save_email_status(user_id, msg["id"], status)
                    database.save_task(tasks[task_id])

            tasks[task_id]["progress"] = tasks[task_id]["total"]
            tasks[task_id]["stage"] = "done"
            database.save_task(tasks[task_id])
        except Exception:
            import traceback

            print(traceback.format_exc())

    threading.Thread(target=worker).start()
    return jsonify({"task_id": task_id})


@app.route("/scan-status/<task_id>")
def scan_status(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "not found"}), 404
    return jsonify(task)


# CODEX: Endpoint to list active scan tasks
@app.route("/scan-tasks")
def scan_tasks():
    db_tasks = {t["id"]: t for t in database.load_tasks(g.user_id)}
    for tid, info in tasks.items():
        if info.get("user_id") == g.user_id:
            db_tasks[tid] = info
    active = [t for t in db_tasks.values() if t.get("stage") != "closed"]
    return jsonify({"tasks": active})


@app.route("/update-status", methods=["POST"])
def update_status():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authenticated"}), 401
    service = build("gmail", "v1", credentials=creds)
    msg_id = request.json["id"]
    status = request.json["status"]
    spam_label = get_label_id(service, "shopify-spam")
    persist_label = get_label_id(service, "scan-persist")
    whitelist_label = get_label_id(service, "whitelist")
    ignore_label = get_label_id(service, "spam-filter-ignore")
    logger.info("Update status request for %s -> %s", msg_id, status)
    if status == "spam":
        logger.debug("Gmail request: add spam label to %s", msg_id)
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={
                "addLabelIds": [spam_label, persist_label],
                "removeLabelIds": [whitelist_label, ignore_label],
            },
        ).execute()
        sender = next(
            (
                e["sender"]
                for t in tasks.values()
                for e in t.get("emails", [])
                if e["id"] == msg_id
            ),
            "",
        )
        if sender:
            database.save_sender(g.user_id, sender, "spam")
        database.save_email_status(g.user_id, msg_id, "spam")
    elif status == "whitelist":
        logger.debug("Gmail request: add whitelist label to %s", msg_id)
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={
                "addLabelIds": [whitelist_label, persist_label],
                "removeLabelIds": [spam_label, ignore_label],
            },
        ).execute()
        sender = next(
            (
                e["sender"]
                for t in tasks.values()
                for e in t.get("emails", [])
                if e["id"] == msg_id
            ),
            "",
        )
        if sender:
            database.save_sender(g.user_id, sender, "whitelist")
        database.save_email_status(g.user_id, msg_id, "whitelist")
    elif status == "ignore":
        logger.debug("Gmail request: add ignore label to %s", msg_id)
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={
                "addLabelIds": [ignore_label, persist_label],
                "removeLabelIds": [spam_label, whitelist_label],
            },
        ).execute()
        sender = next(
            (
                e["sender"]
                for t in tasks.values()
                for e in t.get("emails", [])
                if e["id"] == msg_id
            ),
            "",
        )
        if sender:
            database.save_sender(g.user_id, sender, "ignore")
        database.save_email_status(g.user_id, msg_id, "ignore")
    else:
        logger.debug(
            "Gmail request: clear spam/whitelist/ignore labels from %s", msg_id
        )
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": [spam_label, whitelist_label, ignore_label]},
        ).execute()
        database.save_email_status(g.user_id, msg_id, status)
    update_task_email_status(msg_id, status)
    return ("", 204)


@app.route("/confirm", methods=["POST"])
def confirm():
    creds = get_credentials()
    if not creds:
        return jsonify({"error": "Not authenticated"}), 401
    service = build("gmail", "v1", credentials=creds)
    logger.info("Confirming %s messages as spam", len(request.json.get("ids", [])))
    spam_label = get_label_id(service, "shopify-spam")
    persist_label = get_label_id(service, "scan-persist")
    ids = request.json.get("ids", [])
    task_id = request.json.get("task_id")
    for msg_id in ids:
        logger.debug("Gmail request: get message %s for confirmation", msg_id)
        msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["From"],
            )
            .execute()
        )
        logger.debug("Gmail response: %s", msg)
        sender = next(
            (
                h["value"]
                for h in msg["payload"]["headers"]
                if h["name"].lower() == "from"
            ),
            "",
        )
        # Add to block list
        try:
            logger.debug("Gmail request: create filter for %s", sender)
            service.users().settings().filters().create(
                userId="me",
                body={
                    "criteria": {"from": sender},
                    "action": {
                        "addLabelIds": [spam_label],
                        "removeLabelIds": ["INBOX"],
                    },
                },
            ).execute()
            logger.debug("Gmail request: label %s as shopify-spam", msg_id)
            service.users().messages().modify(
                userId="me",
                id=msg_id,
                body={
                    "addLabelIds": [spam_label, persist_label],
                    "removeLabelIds": ["INBOX"],
                },
            ).execute()
            update_task_email_status(msg_id, "spam")
            database.save_sender(g.user_id, sender, "spam")
            database.confirm_email(g.user_id, msg_id)
        except Exception:
            import traceback

            logger.error(traceback.format_exc())
    if task_id and task_id in tasks:
        # CODEX: Remove task so it no longer appears in active list
        tasks.pop(task_id, None)
        database.delete_task(task_id)
    return ("", 204)


if __name__ == "__main__":
    app.run(debug=True, ssl_context="adhoc")
