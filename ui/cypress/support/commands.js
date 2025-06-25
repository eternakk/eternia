// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })

/**
 * Custom command to login to the application
 * @example cy.login()
 */
Cypress.Commands.add('login', () => {
  // This is a simplified login command that assumes there's a token-based authentication
  // In a real application, you would need to implement the actual login flow
  localStorage.setItem('auth_token', Cypress.env('AUTH_TOKEN') || 'test-token-for-authentication');
  
  // Reload the page to apply the token
  cy.reload();
});

/**
 * Custom command to navigate to a specific page and wait for it to load
 * @example cy.navigateTo('dashboard')
 */
Cypress.Commands.add('navigateTo', (page) => {
  cy.visit(`/${page}`);
  cy.get('body').should('be.visible');
});

/**
 * Custom command to wait for API requests to complete
 * @example cy.waitForApi()
 */
Cypress.Commands.add('waitForApi', () => {
  cy.wait(500); // Simple timeout, in a real app you'd use cy.intercept() and cy.wait('@apiCall')
});