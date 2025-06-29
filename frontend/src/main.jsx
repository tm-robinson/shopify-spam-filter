import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom/client";
import "./App.css";

const DEFAULT_PROMPT =
  "Identify shopify abandoned basket emails, or emails from US companies that mention dollar prices or a US postal address.";

function EmailRow({ email, onStatus }) {
  const [open, setOpen] = useState(false);
  const toggle = () => setOpen(!open);

  return (
    <>
      <tr className={`status-${email.status}`}>
        <td>{email.sender}</td>
        <td>{email.subject}</td>
        <td>{email.date}</td>
        <td className="actions">
          <button
            className="info-btn"
            disabled={!email.llm_sent}
            onClick={toggle}
          >
            i
          </button>
          <button
            className={`whitelist ${email.status === "whitelist" ? "active" : ""}`}
            onClick={() => onStatus(email.id, "whitelist")}
          >
            W
          </button>
          <button
            className={`ignore ${email.status === "ignore" ? "active" : ""}`}
            onClick={() => onStatus(email.id, "ignore")}
          >
            I
          </button>
          <button
            className={`spam ${email.status === "spam" ? "active" : ""}`}
            onClick={() => onStatus(email.id, "spam")}
          >
            !
          </button>
          <button
            className={`not-spam ${email.status === "not_spam" ? "active" : ""}`}
            onClick={() => onStatus(email.id, "not_spam")}
          >
            ✓
          </button>
        </td>
      </tr>
      {open && (
        <tr className="llm-details">
          <td colSpan="4">
            <pre className="llm-request">{email.request}</pre>
            <pre className="llm-response">{email.response}</pre>
          </td>
        </tr>
      )}
    </>
  );
}

function App() {
  const [apiKey, setApiKey] = useState("");
  const [prompt, setPrompt] = useState("");
  const [emails, setEmails] = useState([]);
  const [days, setDays] = useState(10);
  const [task, setTask] = useState(null);
  const [pollInterval, setPollInterval] = useState(1); // seconds
  const [confirming, setConfirming] = useState(false);

  useEffect(() => {
    fetch("/last-prompt")
      .then((r) => r.json())
      .then((d) => {
        setPrompt(d.prompt || DEFAULT_PROMPT);
      })
      .catch(() => {
        setPrompt(DEFAULT_PROMPT);
      });

    // CODEX: Check for any running tasks when the page loads
    fetch("/scan-tasks")
      .then((r) => r.json())
      .then((d) => {
        if (d.tasks && d.tasks.length > 0) {
          const t = d.tasks[0];
          setTask({ id: t.id, ...t });
          setEmails(t.emails || []);
          setPollInterval(1);
        }
      })
      .catch(() => {});
  }, []);

  const linkGmail = () => {
    window.location.href = "/auth";
  };

  const saveKey = () => {
    fetch("/openrouter-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: apiKey }),
    });
  };

  const scan = () => {
    fetch("/scan-emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, days }),
    })
      .then((r) => r.json())
      .then((data) => {
        setTask({ id: data.task_id });
      });
  };

  useEffect(() => {
    if (!task || !task.id) return;
    const intervalMs = pollInterval * 1000;
    const interval = setInterval(() => {
      fetch(`/scan-status/${task.id}`)
        .then((r) => r.json())
        .then((d) => {
          // CODEX: Preserve task id so polling continues
          setTask((prev) => ({ ...prev, ...d }));
          setEmails(d.emails);
          if (d.stage === "done") {
            clearInterval(interval);
          }
        });
    }, intervalMs);
    return () => clearInterval(interval);
  }, [task?.id, pollInterval]);

  const updateStatus = (id, status) => {
    fetch("/update-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, status }),
    });
    setEmails(emails.map((e) => (e.id === id ? { ...e, status } : e)));
  };

  const confirm = () => {
    const ids = emails.filter((e) => e.status === "spam").map((e) => e.id);
    setConfirming(true);
    fetch("/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids, task_id: task?.id }),
    })
      .then(() => {
        // CODEX: Clear task data once confirmation closes it
        setTask(null);
        setEmails([]);
      })
      .finally(() => {
        setConfirming(false);
      });
  };

  return (
    <div className="container">
      <header className="header">
        <h1>Shopify Spam Filter</h1>
        <button onClick={linkGmail}>Link Gmail</button>
        <div>
          <input
            placeholder="OpenRouter API Key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <button onClick={saveKey}>Save Key</button>
        </div>
        <div>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows="3"
            cols="60"
          />
        </div>
        <div>
          <label>Days: {days}</label>
          <input
            type="range"
            min="1"
            max="60"
            value={days}
            onChange={(e) => setDays(e.target.value)}
          />
        </div>
        <div>
          <label>Poll Interval (s): </label>
          <input
            type="number"
            min="1"
            value={pollInterval}
            onChange={(e) => setPollInterval(parseInt(e.target.value, 10) || 1)}
          />
        </div>
        <button onClick={scan}>Scan Emails</button>
        {task && task.stage !== "done" && (
          <div className="progress">
            <div>
              {task.stage} ({task.progress}/{task.total})
            </div>
            <progress value={task.progress} max={task.total || 1}></progress>
          </div>
        )}
        <button onClick={confirm} disabled={confirming}>
          {confirming ? "Confirming..." : "Confirm"}
        </button>
      </header>
      <div className="email-list">
        <table>
          <thead>
            <tr>
              <th>Sender</th>
              <th>Subject</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {emails.map((e) => (
              <EmailRow key={e.id} email={e} onStatus={updateStatus} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
