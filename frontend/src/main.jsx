import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';

function App() {
    const [apiKey, setApiKey] = useState('');
    const [prompt, setPrompt] = useState('Identify shopify abandoned basket spam emails. Return yes or no.');
    const [emails, setEmails] = useState([]);

    const linkGmail = () => {
        window.location.href = '/auth';
    };

    const saveKey = () => {
        fetch('/openrouter-key', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({key: apiKey})});
    };

    const scan = () => {
        fetch('/scan-emails', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt})})
          .then(r => r.json())
          .then(setEmails);
    };

    const toggle = (id, spam) => {
        fetch('/toggle-label', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id, spam})});
        setEmails(emails.map(e => e.id === id ? {...e, spam} : e));
    };

    const confirm = () => {
        const ids = emails.filter(e => e.spam).map(e => e.id);
        fetch('/confirm', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ids})});
    };

    return (
        <div>
            <h1>Shopify Spam Filter</h1>
            <button onClick={linkGmail}>Link Gmail</button>
            <div>
                <input placeholder="OpenRouter API Key" value={apiKey} onChange={e => setApiKey(e.target.value)} />
                <button onClick={saveKey}>Save Key</button>
            </div>
            <div>
                <textarea value={prompt} onChange={e => setPrompt(e.target.value)} rows="3" cols="60" />
            </div>
            <button onClick={scan}>Scan Emails</button>
            <table border="1">
                <thead>
                    <tr><th>Sender</th><th>Subject</th><th>Date</th><th>Spam</th></tr>
                </thead>
                <tbody>
                    {emails.map(e => (
                        <tr key={e.id}>
                            <td>{e.sender}</td>
                            <td>{e.subject}</td>
                            <td>{e.date}</td>
                            <td><input type="checkbox" checked={e.spam} onChange={ev => toggle(e.id, ev.target.checked)} /></td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <button onClick={confirm}>Confirm Choices</button>
        </div>
    );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
