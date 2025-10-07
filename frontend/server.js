import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;

// Serve static files from the public directory (our website)
app.use(express.static(path.join(__dirname, 'public')));

// Serve blog and podcast pages
app.get('/blog', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'blog', 'index.html'));
});

app.get('/podcast', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'podcast', 'index.html'));
});

// Serve the main website for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Website server is running on port ${port}`);
  console.log(`Serving static files from: ${path.join(__dirname, 'public')}`);
});
