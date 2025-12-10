const express = require('express');
const path = require('path');
const app = express();

const PORT = 3001;
const DIST_PATH = path.join(__dirname, 'frontend/dist');

app.use(express.static(DIST_PATH));

app.get('*', (req, res) => {
  res.sendFile(path.join(DIST_PATH, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`InfraPilot frontend server running on http://localhost:${PORT}`);
});
