const { spawn } = require('child_process');
const path = require('path');
const httpServer = require('http-server');
const puppeteer = require('puppeteer');

(async () => {
  // start static server
  const server = httpServer.createServer({ root: path.resolve(__dirname, '..', 'dashboards') });
  server.listen(8088);
  console.log('Serving dashboards on http://localhost:8088');

  // run puppeteer
  const browser = await puppeteer.launch({ args: ['--no-sandbox','--disable-setuid-sandbox'] });
  const page = await browser.newPage();
  await page.goto('http://localhost:8088/hydra/index.html?mock=1', { waitUntil: 'networkidle0' });
  // wait for .card elements
  try {
    await page.waitForSelector('.card', { timeout: 5000 });
    console.log('E2E: found card elements — mock mode working');
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
