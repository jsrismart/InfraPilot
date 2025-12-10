const http = require('http');
const port = 3001;

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end('<h1>InfraPilot Frontend - Ready!</h1>');
});

server.listen(port, '0.0.0.0', () => {
  console.log(`[${new Date().toISOString()}] Frontend server listening on port ${port}`);
  console.log('Press Ctrl+C to stop');
});

process.on('SIGINT', () => {
  console.log('Server shutting down gracefully...');
  server.close(() => process.exit(0));
});

// Keep process alive
setInterval(() => {}, 1000);
