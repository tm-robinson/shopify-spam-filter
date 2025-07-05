import os
import json
import sqlite3

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
        conn.execute(
            "REPLACE INTO tasks (id, user_id, stage, progress, total, emails_json, log_json) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
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
                    "stage": r["stage"],
                    "progress": r["progress"],
                    "total": r["total"],
                    "emails": json.loads(r["emails_json"] or "[]"),
                    "log": json.loads(r["log_json"] or "[]"),
                }
            )
        return result


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
    user_id: str, email_id: str, status: str, confirmed: bool = False
) -> None:
    with get_connection() as conn:
        conn.execute(
            "REPLACE INTO email_status (user_id, email_id, status, confirmed) VALUES (?, ?, ?, ?)",
            (user_id, email_id, status, int(confirmed)),
        )
        conn.commit()


def confirm_email(user_id: str, email_id: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE email_status SET confirmed = 1 WHERE user_id = ? AND email_id = ?",
            (user_id, email_id),
        )
        conn.commit()


def get_confirmed_emails(user_id: str):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT email_id FROM email_status WHERE user_id = ? AND confirmed = 1",
            (user_id,),
        ).fetchall()
        return [r["email_id"] for r in rows]
