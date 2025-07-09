import os
import json
import sqlite3
import datetime
import re
from email.utils import parsedate_to_datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    if not os.path.exists(DB_PATH):
        open(DB_PATH, "a").close()
    with get_connection() as conn, open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
        conn.commit()


def save_token(user_id: str, token: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "REPLACE INTO oauth_tokens (user_id, token) VALUES (?, ?)",
            (user_id, token),
        )
        conn.commit()


def load_token(user_id: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT token FROM oauth_tokens WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return row["token"] if row else None


def save_user_email(user_id: str, email: str) -> None:
    """Store mapping of Gmail address to user id."""
    with get_connection() as conn:
        conn.execute(
            "REPLACE INTO gmail_users (email, user_id) VALUES (?, ?)",
            (email, user_id),
        )
        conn.commit()


def get_user_id_for_email(email: str):
    """Return user id associated with the given Gmail address."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT user_id FROM gmail_users WHERE email = ?",
            (email,),
        ).fetchone()
        return row["user_id"] if row else None


def save_task(task: dict) -> None:
    with get_connection() as conn:
        # CODEX: Use UPSERT to avoid creating extra rows during updates
        conn.execute(
            """
            INSERT INTO tasks (
                id, user_id, stage, progress, total, emails_json, log_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                user_id=excluded.user_id,
                stage=excluded.stage,
                progress=excluded.progress,
                total=excluded.total,
                emails_json=excluded.emails_json,
                log_json=excluded.log_json
            """,
            (
                task.get("id"),
                task.get("user_id"),
                task.get("stage"),
                task.get("progress"),
                task.get("total"),
                json.dumps(task.get("emails", [])),
                json.dumps(task.get("log", [])),
            ),
        )
        conn.commit()


def load_tasks(user_id: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        result = []
        for r in rows:
            result.append(
                {
                    "id": r["id"],
                    "user_id": r["user_id"],
                    "stage": r["stage"],
                    "progress": r["progress"],
                    "total": r["total"],
                    "emails": json.loads(r["emails_json"] or "[]"),
                    "log": json.loads(r["log_json"] or "[]"),
                }
            )
        return result


def load_latest_task(user_id: str):
    """Return the most recent task that is not closed."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND stage != 'closed' ORDER BY rowid DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if not row:
            return None
        task = {
            "id": row["id"],
            "user_id": row["user_id"],
            "stage": row["stage"],
            "progress": row["progress"],
            "total": row["total"],
            "emails": json.loads(row["emails_json"] or "[]"),
            "log": json.loads(row["log_json"] or "[]"),
        }
        if re.search(r"whitelist|spam emails|ignore emails", task["stage"], re.I):
            task["kind"] = "refresh"
        else:
            task["kind"] = "scan"
        return task


def delete_task(task_id: str) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()


def save_sender(user_id: str, sender: str, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "REPLACE INTO senders (user_id, sender, status) VALUES (?, ?, ?)",
            (user_id, sender, status),
        )
        conn.commit()


def get_senders(user_id: str, status: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT sender FROM senders WHERE user_id = ? AND status = ?",
            (user_id, status),
        ).fetchall()
        return [r["sender"] for r in rows]


def save_email_status(
    user_id: str,
    email_id: str,
    status: str,
    *,
    confirmed: bool = False,
    subject: str | None = None,
    sender: str | None = None,
    date: str | None = None,
    filter_created: bool | None = None,
) -> None:
    """Insert or update email status details."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT subject, sender, date, filter_created FROM email_status WHERE user_id = ? AND email_id = ?",
            (user_id, email_id),
        ).fetchone()
        if row:
            subject = subject if subject is not None else row["subject"]
            sender = sender if sender is not None else row["sender"]
            date = date if date is not None else row["date"]
            if filter_created is None:
                filter_created = row["filter_created"]
        conn.execute(
            (
                "REPLACE INTO email_status (user_id, email_id, status, confirmed, "
                "subject, sender, date, filter_created) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            (
                user_id,
                email_id,
                status,
                int(confirmed),
                subject,
                sender,
                date,
                int(filter_created or 0),
            ),
        )
        conn.commit()


def confirm_email(user_id: str, email_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE email_status SET confirmed = 1 WHERE user_id = ? AND email_id = ?",
            (user_id, email_id),
        )
        conn.commit()


def set_filter_created(user_id: str, email_id: str) -> None:
    """Mark an email's filter as created."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE email_status SET filter_created = 1 WHERE user_id = ? AND email_id = ?",
            (user_id, email_id),
        )
        conn.commit()


def has_filter_for_sender(user_id: str, sender: str) -> bool:
    """Return True if any email from this sender has a filter created."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM email_status WHERE user_id = ? AND sender = ? AND filter_created = 1 LIMIT 1",
            (user_id, sender),
        ).fetchone()
        return bool(row)


def get_confirmed_emails(user_id: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT email_id FROM email_status WHERE user_id = ? AND confirmed = 1",
            (user_id,),
        ).fetchall()
        return [r["email_id"] for r in rows]


def get_unconfirmed_emails(user_id: str, after: datetime.datetime):
    """Return emails not yet confirmed that were received on or after the given date."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM email_status WHERE user_id = ? AND confirmed = 0",
            (user_id,),
        ).fetchall()
    if after.tzinfo is not None:
        after_cmp = after.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    else:
        after_cmp = after

    emails = []
    for r in rows:
        try:
            r_dt = parsedate_to_datetime(r["date"])
            if r_dt and r_dt.tzinfo is not None:
                r_dt = r_dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
        except Exception:
            r_dt = None

        if r_dt and r_dt >= after_cmp:
            emails.append(
                {
                    "id": r["email_id"],
                    "subject": r["subject"] or "",
                    "sender": r["sender"] or "",
                    "date": r["date"] or "",
                    "status": r["status"],
                    "request": "",
                    "response": "",
                    "llm_sent": False,
                    "filter_created": bool(r["filter_created"]),
                }
            )
    return emails


def get_email_status(user_id: str, email_id: str):
    """Return stored status for a specific email id."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT status FROM email_status WHERE user_id = ? AND email_id = ?",
            (user_id, email_id),
        ).fetchone()
        return row["status"] if row else None


def get_all_email_ids(user_id: str):
    """Return all email ids stored for this user."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT email_id FROM email_status WHERE user_id = ?",
            (user_id,),
        ).fetchall()
        return [r["email_id"] for r in rows]
