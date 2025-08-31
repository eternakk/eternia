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
  retries: {
    runMode: 2,
    openMode: 0,
  },
});