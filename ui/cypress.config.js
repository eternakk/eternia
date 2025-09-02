import { defineConfig } from 'cypress';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Guard against invalid cypress.env.json which can crash Cypress in CI if someone
// mistakenly commits shell-style content (e.g., AUTH_TOKEN=abc) instead of JSON.
// If it's invalid JSON, we replace it with an empty object to let the run proceed.
try {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
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

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:5173',
    setupNodeEvents(on, config) {
      // Merge envs from CI/system into Cypress env
      config.env = {
        ...config.env,
        AUTH_TOKEN: process.env.AUTH_TOKEN ?? process.env.CYPRESS_AUTH_TOKEN,
        API_URL: process.env.API_URL ?? process.env.CYPRESS_API_URL,
      };
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