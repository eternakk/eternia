import { defineConfig } from 'cypress';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Guard against invalid cypress.env.json which can crash Cypress in CI if someone
// mistakenly commits shell-style content (e.g., AUTH_TOKEN=abc) instead of JSON.
// If it's invalid JSON, we replace it with an empty object to let the run proceed.
try {
  const envPath = path.resolve(__dirname, 'cypress.env.json');
  if (fs.existsSync(envPath)) {
    const raw = fs.readFileSync(envPath, 'utf8');
    try {
      JSON.parse(raw);
    } catch {
      fs.writeFileSync(envPath, '{}\n');
      // eslint-disable-next-line no-console
      console.warn('[cypress-env] Invalid JSON detected in cypress.env.json. Replaced with {} for this run.');
    }
  }
} catch {
  // ignore all errors here; Cypress will continue using process.env defaults
}

async function isServerUp(url) {
  try {
    const res = await fetch(url, { method: 'GET' });
    return res.ok || res.status === 200;
  } catch {
    return false;
  }
}

async function waitForServer(url, timeoutMs = 90000, intervalMs = 1000) {
  const start = Date.now();
  // eslint-disable-next-line no-console
  console.log(`[cypress] Waiting for server at ${url} ...`);
  while (Date.now() - start < timeoutMs) {
    if (await isServerUp(url)) {
      // eslint-disable-next-line no-console
      console.log(`[cypress] Server is up at ${url}`);
      return true;
    }
    await new Promise((r) => setTimeout(r, intervalMs));
  }
  return false;
}

let devServerProc = null;

async function ensureDevServer(baseUrl) {
  // If already running, do nothing
  if (await isServerUp(baseUrl)) return null;

  // Start Vite dev server
  // eslint-disable-next-line no-console
  console.log('[cypress] baseUrl is not reachable. Starting Vite dev server...');
  const proc = spawn('npm', ['run', 'dev'], {
    cwd: __dirname, // ui directory
    stdio: 'inherit',
    shell: process.platform === 'win32',
  });
  devServerProc = proc;

  const ok = await waitForServer(baseUrl);
  if (!ok) {
    // eslint-disable-next-line no-console
    console.error('[cypress] Timed out waiting for Vite dev server to start.');
    try { proc.kill(); } catch {}
    throw new Error('Dev server did not start in time');
  }
  return proc;
}

function stopDevServer() {
  if (devServerProc && !devServerProc.killed) {
    // eslint-disable-next-line no-console
    console.log('[cypress] Stopping Vite dev server...');
    try { devServerProc.kill('SIGTERM'); } catch {}
    // Fallback hard kill after short delay
    setTimeout(() => {
      try { if (devServerProc && !devServerProc.killed) devServerProc.kill('SIGKILL'); } catch {}
    }, 5000);
  }
}

const BASE_URL = process.env.CYPRESS_BASE_URL || 'http://localhost:5173';
// Ensure dev server is running before Cypress validates baseUrl
await ensureDevServer(BASE_URL);

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    async setupNodeEvents(on, config) {
      // Merge envs from CI/system into Cypress env
      config.env = {
        ...config.env,
        AUTH_TOKEN: process.env.AUTH_TOKEN ?? process.env.CYPRESS_AUTH_TOKEN,
        API_URL: process.env.API_URL ?? process.env.CYPRESS_API_URL,
      };

      // Auto-start dev server in CI or when cypress is run directly without start-server-and-test
      on('before:run', async () => {
        try {
          await ensureDevServer(config.baseUrl || 'http://localhost:5173');
        } catch (e) {
          // Re-throw to let Cypress fail early with a clear message
          throw e;
        }
      });

      on('after:run', () => {
        stopDevServer();
      });

      // Ensure cleanup on process exit as well
      process.on('exit', stopDevServer);
      process.on('SIGINT', () => { stopDevServer(); process.exit(130); });
      process.on('SIGTERM', () => { stopDevServer(); process.exit(143); });

      return config;
    },
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
  },
  viewportWidth: 1280,
  viewportHeight: 720,
  video: false,
  screenshotOnRunFailure: true,
  retries: {
    runMode: 2,
    openMode: 0,
  },
});