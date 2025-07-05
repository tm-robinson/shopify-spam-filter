CREATE TABLE IF NOT EXISTS oauth_tokens (
    user_id TEXT PRIMARY KEY,
    token TEXT NOT NULL
);

-- CODEX: Map Gmail addresses to user ids so returning users on new browsers
-- share the same account
CREATE TABLE IF NOT EXISTS gmail_users (
    email TEXT PRIMARY KEY,
    user_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    stage TEXT,
    progress INTEGER,
    total INTEGER,
    emails_json TEXT,
    log_json TEXT
);

CREATE TABLE IF NOT EXISTS senders (
    user_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    status TEXT NOT NULL,
    PRIMARY KEY (user_id, sender)
);

CREATE TABLE IF NOT EXISTS email_status (
    user_id TEXT NOT NULL,
    email_id TEXT NOT NULL,
    status TEXT NOT NULL,
    confirmed INTEGER DEFAULT 0,
    PRIMARY KEY (user_id, email_id)
);
