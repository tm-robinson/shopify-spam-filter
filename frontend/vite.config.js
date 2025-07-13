import { defineConfig } from "vite";
import https from "https";

const backend = "https://localhost:5000"; // 1️⃣ https, not http
const httpsAgent = new https.Agent({
  keepAlive: true,
  rejectUnauthorized: false, // 2️⃣ accept Flask’s self-signed cert
});

export default defineConfig({
  root: ".",
  server: {
    proxy: {
      "/auth": {
        target: backend,
        changeOrigin: true,
        secure: false, // 3️⃣ tell http-proxy “don’t verify”
        agent: httpsAgent, // 4️⃣ reuse sockets, avoids ECONNRESET spam
      },
      "/oauth2callback": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/openrouter-key": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/scan-emails": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/scan-status": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/scan-tasks": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/update-status": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/confirm": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      // CODEX: Proxy endpoint for retrieving saved prompt
      "/last-prompt": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/refresh-senders": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/senders": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/reset-sender": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/logs": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
      "/clear-task": {
        target: backend,
        changeOrigin: true,
        secure: false,
        agent: httpsAgent,
      },
    },
  },
});
