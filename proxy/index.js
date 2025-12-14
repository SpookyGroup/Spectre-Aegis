require('dotenv').config();
const express = require('express');
const fetch = require('cross-fetch');
const app = express();
app.use(express.json());

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
if (!SUPABASE_URL) {
  console.error('Please set SUPABASE_URL and SUPABASE_KEY in .env');
}

// Basic CORS allowing all origins for demo. For production, restrict origins.
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, apikey, Authorization');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

app.post('/api/check-upcoming-games', async (req, res) => {
  try {
    const url = SUPABASE_URL || (req.body && req.body.url);
    if (!url) return res.status(400).json({ error: 'No SUPABASE_URL configured.' });

    const r = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'apikey': SUPABASE_KEY || req.headers['apikey'] || '',
        'Authorization': 'Bearer ' + (SUPABASE_KEY || req.headers['authorization'] || '')
      },
      body: JSON.stringify(req.body)
    });

    const text = await r.text();
    res.status(r.status).send(text);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: String(err) });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Hydra proxy listening on http://localhost:${port}`));
