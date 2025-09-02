import { promises as fs } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const envPath = path.resolve(__dirname, '../cypress.env.json');
const backupPath = envPath + '.invalid';

async function ensureValidCypressEnv() {
  try {
    // If no file, nothing to do.
    await fs.access(envPath).catch(() => { throw new Error('NOFILE'); });
  } catch (e) {
    if (e && e.message === 'NOFILE') {
      console.log('[cypress-env] No cypress.env.json found. Skipping validation.');
      return;
    }
    // Unexpected error accessing the file, do not block the run
    console.warn('[cypress-env] Could not access cypress.env.json, continuing:', e?.message || e);
    return;
  }

  let raw;
  try {
    raw = await fs.readFile(envPath, 'utf8');
  } catch (e) {
    console.warn('[cypress-env] Could not read cypress.env.json, continuing:', e?.message || e);
    return;
  }

  try {
    JSON.parse(raw);
    console.log('[cypress-env] cypress.env.json is valid JSON.');
    return;
  } catch {
    // Invalid JSON: back up and replace with {}
    try {
      // Attempt rename first
      await fs.rename(envPath, backupPath);
    } catch {
      // Fallback: try to write a backup copy if rename fails
      try {
        await fs.writeFile(backupPath, raw);
      } catch {
        // Ignore if even backup fails
      }
      // Try to truncate the original before writing
      try {
        await fs.writeFile(envPath, '');
      } catch {
        // ignore
      }
    }

    try {
      await fs.writeFile(envPath, '{}\n');
      console.warn('[cypress-env] Invalid JSON detected. Replaced cypress.env.json with {} and saved original to ' + path.basename(backupPath));
    } catch (e) {
      console.warn('[cypress-env] Failed to write corrected cypress.env.json. Cypress may still fail:', e?.message || e);
    }
  }
}

await ensureValidCypressEnv();
