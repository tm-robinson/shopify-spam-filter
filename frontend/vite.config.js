export default {
  root: '.',
  server: {
    proxy: {
      '/auth': 'http://localhost:5000',
      '/oauth2callback': 'http://localhost:5000',
      '/openrouter-key': 'http://localhost:5000',
      '/scan-emails': 'http://localhost:5000',
      '/toggle-label': 'http://localhost:5000',
      '/confirm': 'http://localhost:5000',
    },
  },
};
