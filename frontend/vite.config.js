const backend = 'http://localhost:5000';

export default {
  root: '.',
  server: {
    proxy: {
      '/auth': { target: backend, changeOrigin: true },
      '/oauth2callback': { target: backend, changeOrigin: true },
      '/openrouter-key': { target: backend, changeOrigin: true },
      '/scan-emails': { target: backend, changeOrigin: true },
      '/toggle-label': { target: backend, changeOrigin: true },
      '/confirm': { target: backend, changeOrigin: true },
    },
  },
};
