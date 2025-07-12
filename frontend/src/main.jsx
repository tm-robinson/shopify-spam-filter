import React, { useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom/client";
import "./App.css";

const DEFAULT_POLL_INTERVAL = Number(import.meta.env.VITE_POLL_INTERVAL || 1);

const DEFAULT_PROMPT =
  "Identify shopify abandoned basket emails, or emails from US companies that mention dollar prices or a US postal address.";

function formatDate(str) {
  const d = new Date(str);
  if (Number.isNaN(d.getTime())) return str;
  const diff = Date.now() - d.getTime();
  if (diff < 24 * 60 * 60 * 1000) {
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString([], { day: "2-digit", month: "short" });
}

function EmailRow({ email, onStatus }) {
  const [open, setOpen] = useState(false);
  const toggle = () => setOpen(!open);
  // CODEX: open Gmail message in web client for all platforms
  const gmailUrl = `https://mail.google.com/mail/u/0/#inbox/${email.id}`;
  const truncatedSubject =
    email.subject.length > 50
      ? `${email.subject.slice(0, 50)}...`
      : email.subject; // CODEX: limit long subjects

  return (
    <>
      <tr className={`status-${email.status}`}>
        <td className="email-cell">
          <a
            href={gmailUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="gmail-link"
          >
            <strong>{email.sender}</strong>
            <br />
            {truncatedSubject}
          </a>
        </td>
        <td className="date-col">{formatDate(email.date)}</td>
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
          <td colSpan="3">
            <pre className="llm-request">{email.request}</pre>
            <pre className="llm-response">{email.response}</pre>
          </td>
        </tr>
      )}
    </>
  );
}

function ManageSenders({ onClose }) {
  const [senders, setSenders] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetch("/senders")
      .then((r) => r.json())
      .then((d) => setSenders(d.senders || []))
      .catch(() => {});
  }, []);

  const reset = (sender) => {
    fetch("/reset-sender", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sender }),
    })
      .then((r) => {
        if (r.ok) {
          setSenders((prev) => prev.filter((s) => s.sender !== sender));
        } else {
          alert("Failed to reset sender");
        }
      })
      .catch(() => {});
  };

  const filtered =
    filter === "all" ? senders : senders.filter((s) => s.status === filter);

  return (
    <div className="container">
      <header className="header">
        <button onClick={onClose}>Close</button>
        <button
          className={filter === "all" ? "active" : ""}
          onClick={() => setFilter("all")}
        >
          All
        </button>
        <button
          className={filter === "whitelist" ? "active" : ""}
          onClick={() => setFilter("whitelist")}
        >
          Whitelist
        </button>
        <button
          className={filter === "spam" ? "active" : ""}
          onClick={() => setFilter("spam")}
        >
          Spam
        </button>
        <button
          className={filter === "ignore" ? "active" : ""}
          onClick={() => setFilter("ignore")}
        >
          Ignore
        </button>
      </header>
      <div className="email-list">
        <table>
          <thead>
            <tr>
              <th>Sender</th>
              <th>Status</th>
              <th className="actions"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.sender}>
                <td className="email-cell">{s.sender}</td>
                <td>{s.status}</td>
                <td className="actions">
                  <button className="trash-btn" onClick={() => reset(s.sender)}>
                    🗑
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function App() {
  const [prompt, setPrompt] = useState("");
  const [emails, setEmails] = useState([]);
  const [days, setDays] = useState(3); // CODEX: default scan range reduced
  const [task, setTask] = useState(null);
  const [managing, setManaging] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [pendingStatuses, setPendingStatuses] = useState({});
  // CODEX: track ids recently updated by the user to ignore incoming status
  const pendingRef = useRef(pendingStatuses);
  const ignoreStatusRef = useRef(new Set());
  const [showSpam, setShowSpam] = useState(true);
  const [logLines, setLogLines] = useState([]);
  const [showLogs, setShowLogs] = useState(false);
  useEffect(() => {
    pendingRef.current = pendingStatuses;
  }, [pendingStatuses]);
  const [showNotSpam, setShowNotSpam] = useState(true);
  const [showWhitelist, setShowWhitelist] = useState(true);
  const [showIgnore, setShowIgnore] = useState(true);
  // CODEX: open Gmail whitelist search in the web client
  const openWhitelist = () => {
    const query = encodeURIComponent("label:whitelist");
    const webUrl = `https://mail.google.com/mail/u/0/#search/${query}`;
    window.location = webUrl;
  };

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
      .then((r) => {
        if (!r.ok) {
          alert("Failed to load scan tasks");
          throw new Error("scan tasks");
        }
        return r.json();
      })
      .then((d) => {
        if (d.tasks && d.tasks.length > 0) {
          const t = d.tasks[0];
          setTask({ id: t.id, ...t });
          setEmails(t.emails || []);
        }
      })
      .catch(() => {});
    // no continuous polling here; status polling starts once a task is active
  }, []);

  const linkGmail = () => {
    window.location.href = "/auth";
  };

  const openManage = () => {
    setManaging(true);
  };

  const closeManage = () => {
    setManaging(false);
  };

  const viewLogs = () => {
    fetch("/logs")
      .then((r) => r.json())
      .then((d) => {
        setLogLines(d.logs || []);
        setShowLogs(true);
      })
      .catch(() => {});
  };

  const clearTask = () => {
    if (!task) return;
    fetch("/clear-task", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: task.id }),
    })
      .then((r) => {
        if (r.ok) {
          setTask(null);
          setEmails([]);
        } else {
          alert("Failed to clear task");
        }
      })
      .catch(() => {});
  };

  const scan = () => {
    fetch("/scan-emails", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, days }),
    })
      .then((r) => {
        if (r.status === 401) {
          alert("Please link Gmail before scanning");
          return null;
        }
        if (!r.ok) {
          alert("Failed to start scan");
          throw new Error("scan");
        }
        return r.json();
      })
      .then((data) => {
        if (data) {
          setTask({ id: data.task_id });
        }
      });
  };

  const refreshLists = () => {
    fetch("/refresh-senders", { method: "POST" })
      .then((r) => {
        if (r.status === 401) {
          alert("Please link Gmail before refreshing");
          return null;
        }
        if (!r.ok) {
          alert("Failed to refresh lists");
          throw new Error("refresh");
        }
        return r.json();
      })
      .then((data) => {
        if (data) {
          setTask({ id: data.task_id });
        }
      });
  };

  useEffect(() => {
    if (!task || !task.id) return;
    if (task.stage === "done" || task.stage === "closed") return;
    const intervalMs = DEFAULT_POLL_INTERVAL * 1000;
    let interval;
    const fetchStatus = () => {
      fetch(`/scan-status/${task.id}`)
        .then((r) => {
          if (r.status === 404) {
            // CODEX: stop polling when the task no longer exists
            clearInterval(interval);
            setTask(null);
            setEmails([]);
            return null;
          }
          if (!r.ok) {
            alert("Failed to fetch scan status");
            throw new Error("status");
          }
          return r.json();
        })
        .then((d) => {
          if (!d) return;
          if (d.summary) {
            alert(d.summary.message || "Task complete");
            setTask(null);
            setEmails([]);
            return;
          }
          // CODEX: Preserve task id so polling continues
          setTask((prev) => ({ ...prev, ...d }));
          const incoming = d.emails || [];
          setEmails((prev) =>
            incoming.map((e) => {
              const prevEmail = prev.find((p) => p.id === e.id) || e;
              const locked = ignoreStatusRef.current.has(e.id);
              const status = locked
                ? prevEmail.status
                : pendingRef.current[e.id] || e.status;
              return { ...e, status };
            }),
          );
          setPendingStatuses((prev) => {
            const remaining = { ...prev };
            incoming.forEach((e) => {
              if (prev[e.id] && prev[e.id] === e.status) {
                delete remaining[e.id];
              }
            });
            return remaining;
          });
          if (d.stage === "done" || d.stage === "closed") {
            clearInterval(interval);
            if (d.stage === "closed") {
              setTask(null);
              setEmails([]);
            }
          }
        })
        .catch(() => {});
    };
    // CODEX: immediately check status on load
    fetchStatus();
    interval = setInterval(fetchStatus, intervalMs);
    return () => clearInterval(interval);
  }, [task?.id, task?.stage]);

  const updateStatus = (id, status) => {
    setPendingStatuses((prev) => ({ ...prev, [id]: status }));
    ignoreStatusRef.current.add(id); // CODEX: prevent flicker on next poll
    setTimeout(() => {
      ignoreStatusRef.current.delete(id);
    }, 5000);
    fetch("/update-status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, status }),
    })
      .then((r) => {
        if (!r.ok) {
          alert("Failed to update status");
        }
      })
      .catch(() => {});
    setEmails((prev) => prev.map((e) => (e.id === id ? { ...e, status } : e)));
  };

  const confirm = () => {
    const ids = emails.map((e) => e.id);
    setConfirming(true);
    if (task) {
      // CODEX: optimistic confirming stage
      setTask({ ...task, stage: "confirming", progress: 0, total: ids.length });
    }
    fetch("/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ids, task_id: task?.id }),
    })
      .then((r) => {
        if (!r.ok) {
          alert("Failed to confirm spam");
          throw new Error("confirm");
        }
      })
      .catch(() => {})
      .finally(() => {
        setConfirming(false);
      });
  };

  const isRefreshTask =
    task && /whitelist|spam emails|ignore emails/i.test(task.stage || "");
  const isScanningTask = task && !isRefreshTask;
  const noActiveTask = !task || task.stage === "closed";

  if (managing) {
    return <ManageSenders onClose={closeManage} />;
  }

  return (
    <div className="container">
      <header className="header">
        <button onClick={linkGmail}>Link Gmail</button>
        <a href="#" onClick={openWhitelist} className="gmail-link">
          View Whitelist
        </a>
        <div>
          <textarea
            className="prompt-input"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows="3"
            cols="45"
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
        {noActiveTask && <button onClick={scan}>Scan Emails</button>}
        {noActiveTask && <button onClick={refreshLists}>Refresh Lists</button>}
        <button onClick={openManage}>Manage</button>
        <button onClick={viewLogs}>View Logs</button>
        {task && <button onClick={clearTask}>Clear Task</button>}
        {task && task.stage !== "done" && (
          <div className="progress">
            <div>
              {task.stage} ({task.progress}/{task.total})
            </div>
            <progress value={task.progress} max={task.total || 1}></progress>
          </div>
        )}
        {task && task.stage === "done" && !isRefreshTask && (
          <button onClick={confirm} disabled={confirming}>
            {confirming ? "Confirming..." : "Confirm"}
          </button>
        )}
      </header>
      <div className="filters">
        <button
          className={showSpam ? "active" : ""}
          onClick={() => setShowSpam(!showSpam)}
        >
          Spam
        </button>
        <button
          className={showNotSpam ? "active" : ""}
          onClick={() => setShowNotSpam(!showNotSpam)}
        >
          Not Spam
        </button>
        <button
          className={showWhitelist ? "active" : ""}
          onClick={() => setShowWhitelist(!showWhitelist)}
        >
          Whitelist
        </button>
        <button
          className={showIgnore ? "active" : ""}
          onClick={() => setShowIgnore(!showIgnore)}
        >
          Ignore
        </button>
      </div>
      <div className="email-list">
        <table>
          <thead>
            <tr>
              <th>Email</th>
              <th className="date-col">Date</th>
              <th className="actions">Action</th>
            </tr>
          </thead>
          <tbody>
            {emails
              .filter(
                (e) =>
                  (showSpam || e.status !== "spam") &&
                  (showNotSpam || e.status !== "not_spam") &&
                  (showWhitelist || e.status !== "whitelist") &&
                  (showIgnore || e.status !== "ignore"),
              )
              .map((e) => (
                <EmailRow key={e.id} email={e} onStatus={updateStatus} />
              ))}
          </tbody>
        </table>
      </div>
      {showLogs && (
        <div className="logs-dialog">
          <pre>{logLines.join("\n")}</pre>
          <button onClick={() => setShowLogs(false)}>Close</button>
        </div>
      )}
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
