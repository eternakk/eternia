# Fixing Cypress config/env errors and recommended CI setup

This document summarizes the resolution for two Cypress issues and the recommended approach for environment variables in CI.

## What failed and why
1) Config ESM error (previously):
- Error: "ReferenceError: require is not defined in ES module scope".
- Cause: cypress.config.js was treated as an ES module due to package.json "type": "module", but used CommonJS exports.
- Fix: Use ESM syntax with `export default defineConfig({...})`.

2) Invalid cypress.env.json:
- Error: Unexpected token 'A', "AUTH_TOKEN"... is not valid JSON.
- Cause: cypress.env.json contained non‑JSON (e.g., AUTH_TOKEN=abc style).
- Fix: Either provide strict JSON or avoid committing this file; prefer environment variables in CI.

## Current implementation in this repo
- cypress.config.js is ESM and maps environment variables into Cypress at runtime:
  - AUTH_TOKEN is sourced from AUTH_TOKEN or CYPRESS_AUTH_TOKEN.
  - API_URL is sourced from API_URL or CYPRESS_API_URL.
- We added an example file: ui/cypress.env.json.example (valid JSON) and ignored real ui/cypress.env.json in Git.

Excerpt from ui/cypress.config.js:

import { defineConfig } from 'cypress';

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
  retries: { runMode: 2, openMode: 0 },
});

## Option A (recommended for CI): CYPRESS_* environment variables
- Don’t commit secrets. Pass variables via CI as CYPRESS_*; Cypress will expose them in `Cypress.env()` and our mapping covers non‑prefixed names too.

GitHub Actions example:

- name: Install deps
  run: npm ci

- name: Run Cypress
  run: npm run cypress:run
  env:
    CYPRESS_AUTH_TOKEN: ${{ secrets.AUTH_TOKEN }}
    CYPRESS_API_URL: https://api.example.com

Local example:
- CYPRESS_AUTH_TOKEN=abc123 CYPRESS_API_URL=http://localhost:8000 npm run cypress:run

Usage in tests:
- Cypress.env('AUTH_TOKEN')
- Cypress.env('API_URL')

## Option B: Use a local ui/cypress.env.json (strict JSON only)
Create ui/cypress.env.json (not committed) based on ui/cypress.env.json.example:
{
  "AUTH_TOKEN": "your-token-here",
  "API_URL": "http://localhost:8000"
}

Rules:
- Keys and string values must be quoted.
- No comments, no trailing commas.

## Verifying locally
- If using a cypress.env.json: validate it with a JSON linter or `node -e "JSON.parse(require('fs').readFileSync('ui/cypress.env.json','utf8')); console.log('OK')"`.
- Or temporarily rename the file to confirm it’s the cause: `mv ui/cypress.env.json ui/cypress.env.json.bak`.

## Common pitfalls
- Do not use .env style (KEY=value) inside cypress.env.json.
- Do not commit secrets; use CI envs.
- Remember that env variables passed in CI override example defaults.
