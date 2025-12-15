require('dotenv').config();
const express = require('express');
const fetch = require('cross-fetch');
const app = express();
app.use(express.json());

const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_KEY;
const ALLOWED_BACKENDS = (process.env.ALLOWED_BACKENDS || '').split(',').map(s => s.trim()).filter(Boolean);
const CACHE_TTL = parseInt(process.env.CACHE_TTL || '20', 10); // seconds
const RATE_LIMIT_WINDOW = parseInt(process.env.RATE_LIMIT_WINDOW || '60', 10); // seconds
const RATE_LIMIT_MAX = parseInt(process.env.RATE_LIMIT_MAX || '30', 10); // requests per window per IP

if (!SUPABASE_URL) {
  console.error('Please set SUPABASE_URL and SUPABASE_KEY in .env');
}

// In-memory cache and rate limit stores (sufficient for small-scale or demo)
const cache = new Map();
const rateStore = new Map();

// Basic CORS allowing all origins for demo. For production, restrict origins.
app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, apikey, Authorization');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  if (req.method === 'OPTIONS') return res.sendStatus(200);
  next();
});

// Simple request logger
app.use((req, res, next) => {
  const now = new Date().toISOString();
  console.log(`[${now}] ${req.ip} ${req.method} ${req.originalUrl}`);
  next();
});

// Basic rate limiter (fixed window per IP)
app.use((req, res, next) => {
  try {
    const ip = req.ip || req.connection.remoteAddress || 'unknown';
    const now = Date.now();
    const windowKey = Math.floor(now / (RATE_LIMIT_WINDOW * 1000));
    const key = ip + ':' + windowKey;
    const entry = rateStore.get(key) || { count: 0 };
    entry.count = (entry.count || 0) + 1;
    rateStore.set(key, entry);
    if (entry.count > RATE_LIMIT_MAX) {
      res.setHeader('Retry-After', RATE_LIMIT_WINDOW);
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }
    next();
  } catch (e) {
    next();
  }
});

app.post('/api/check-upcoming-games', async (req, res) => {
  try {
    const url = SUPABASE_URL || (req.body && req.body.url);
    if (!url) return res.status(400).json({ error: 'No SUPABASE_URL configured.' });

    // Allowlist check (if configured)
    if (ALLOWED_BACKENDS.length > 0) {
      const ok = ALLOWED_BACKENDS.some(a => url.startsWith(a));
      if (!ok) return res.status(403).json({ error: 'Backend URL not allowed.' });
    }

    // Cache key
    const cacheKey = `${url}|${JSON.stringify(req.body || {})}`;
    const cached = cache.get(cacheKey);
    if (cached && (Date.now() - cached.ts) < (CACHE_TTL * 1000)) {
      console.log('cache hit');
      res.set(cached.headers || {});
      return res.status(cached.status).send(cached.body);
    }

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
    // store in cache
    try {
      cache.set(cacheKey, { ts: Date.now(), status: r.status, headers: { 'content-type': r.headers.get('content-type') }, body: text });
    } catch (e) { console.warn('cache store failed', e); }
    res.status(r.status).send(text);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: String(err) });
  }
});

// Health endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', env: { cache_ttl: CACHE_TTL, rate_limit_window: RATE_LIMIT_WINDOW, rate_limit_max: RATE_LIMIT_MAX, allowed_backends: ALLOWED_BACKENDS } });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Hydra proxy listening on http://localhost:${port}`));
