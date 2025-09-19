/// <reference types="cypress" />

// Dashboard smoke: verify key panels and columns render.
describe('Dashboard smoke', () => {
  it('loads the app and displays agent dashboard columns', () => {
    cy.visit('/');

    // Header
    cy.contains('Eterna Mission‑Control').should('be.visible');

    // AgentDashboard column headers
    cy.contains('Name').should('be.visible');
    cy.contains('Role').should('be.visible');
    cy.contains('Zone').should('be.visible');
    cy.contains('Mood').should('be.visible');
    cy.contains('Stress').should('be.visible');

    // At least one agent with stubbed zone label should appear
    cy.contains('Zone-α').should('exist');
  });
});
