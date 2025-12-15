const { spawn } = require('child_process');
const path = require('path');
const httpServer = require('http-server');
const puppeteer = require('puppeteer');

(async () => {
  // start static server
  const server = httpServer.createServer({ root: path.resolve(__dirname, '..', 'dashboards') });
  server.listen(8088);
  console.log('Serving dashboards on http://localhost:8088');

  // Optional: verify proxy health and endpoint when available
  const fetch = require('node-fetch');
  const proxyHealth = 'http://localhost:3000/health';
  const proxyApi = 'http://localhost:3000/api/check-upcoming-games';

  async function waitForProxy(timeout = 10000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      try {
        const r = await fetch(proxyHealth);
        if (r.ok) return true;
      } catch (e) {
        // ignore
      }
      await new Promise(r => setTimeout(r, 500));
    }
    return false;
  }

  if (await waitForProxy(15000)) {
    console.log('Proxy is healthy — validating /api route');
    try {
      const r = await fetch(proxyApi, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ league: 'americanfootball_nfl' }) });
      if (r.ok) {
        const j = await r.json();
        if (j && Array.isArray(j.games) && j.games.length > 0) {
          console.log('Proxy /api returned mock games — OK');
        } else {
          console.warn('Proxy returned unexpected structure', j && Object.keys(j).slice(0,5));
        }
      } else {
        console.warn('Proxy api returned non-200', r.status);
      }
    } catch (e) { console.warn('Proxy api check failed', e && e.message); }
  } else {
    console.log('Proxy not available — skipping proxy checks');
  }

  // run puppeteer against the real UI using the proxy endpoint if present
  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  const uiUrl = (await waitForProxy(1000)) ? 'http://localhost:8088/hydra/index.html?supabase_url=http://localhost:3000/api/check-upcoming-games&supabase_key=dummy' : 'http://localhost:8088/hydra/index.html?mock=1';
  await page.goto(uiUrl, { waitUntil: 'networkidle0' });
  // wait for .card elements
  try {
    await page.waitForSelector('.card', { timeout: 5000 });
    console.log('E2E: found card elements — UI rendering OK');
    await browser.close();
    server.close();
    process.exit(0);
  } catch (err) {
    console.error('E2E failed: no card elements found', err);
    await browser.close();
    server.close();
    process.exit(2);
  }
})();
