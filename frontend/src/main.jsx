import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';

function App() {
  const [apiKey, setApiKey] = useState('');
  const [prompt, setPrompt] = useState('Identify shopify abandoned basket spam emails. Return yes or no.');
  const [emails, setEmails] = useState([]);
  const [chatLog, setChatLog] = useState([]);
  const [days, setDays] = useState(10);
  const [task, setTask] = useState(null);

  const linkGmail = () => {
    window.location.href = '/auth';
  };

  const saveKey = () => {
    fetch('/openrouter-key', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: apiKey})});
  };

  const scan = () => {
    fetch('/scan-emails', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt, days})})
      .then(r => r.json())
      .then(data => {
        setTask({id: data.task_id});
      });
  };

  useEffect(() => {
    if (!task || !task.id) return;
    const interval = setInterval(() => {
      fetch(`/scan-status/${task.id}`)
        .then(r => r.json())
        .then(d => {
          setTask(d);
          if (d.stage === 'done') {
            setEmails(d.emails);
            setChatLog(d.log);
            clearInterval(interval);
          }
        });
    }, 1000);
    return () => clearInterval(interval);
  }, [task?.id]);

  const updateStatus = (id, status) => {
    fetch('/update-status', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id, status})});
    setEmails(emails.map(e => e.id === id ? {...e, status} : e));
  };

  const confirm = () => {
    const ids = emails.filter(e => e.status === 'spam').map(e => e.id);
    fetch('/confirm', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ids})});
  };

  return (
    <div className="container">
      <div className="main">
        <h1>Shopify Spam Filter</h1>
        <button onClick={linkGmail}>Link Gmail</button>
        <div>
          <input placeholder="OpenRouter API Key" value={apiKey} onChange={e => setApiKey(e.target.value)} />
          <button onClick={saveKey}>Save Key</button>
        </div>
        <div>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)} rows="3" cols="60" />
        </div>
        <div>
          <label>Days: {days}</label>
          <input type="range" min="1" max="60" value={days} onChange={e => setDays(e.target.value)} />
        </div>
        <button onClick={scan}>Scan Emails</button>
        {task && task.stage !== 'done' && (
          <div className="progress">
            <div>{task.stage} {task.progress}/{task.total}</div>
            <progress value={task.progress} max={task.total || 1}></progress>
          </div>
        )}
        <table>
          <thead>
            <tr><th>Sender</th><th>Subject</th><th>Date</th><th>Action</th></tr>
          </thead>
          <tbody>
            {emails.map(e => (
              <tr key={e.id}>
                <td>{e.sender}</td>
                <td>{e.subject}</td>
                <td>{e.date}</td>
                <td>
                  <button className={`spam ${e.status==='spam'?'active':''}`} onClick={() => updateStatus(e.id,'spam')}>Spam</button>
                  <button className={`not-spam ${e.status==='not_spam'?'active':''}`} onClick={() => updateStatus(e.id,'not_spam')}>Not Spam</button>
                  <button className={`whitelist ${e.status==='whitelist'?'active':''}`} onClick={() => updateStatus(e.id,'whitelist')}>Whitelist</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <button onClick={confirm}>Confirm Choices</button>
      </div>
      <div className="chat-log">
        {chatLog.map((c, i) => (
          <div key={i} className={`chat-${c.role}`}>{c.role}: {c.content}</div>
        ))}
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

