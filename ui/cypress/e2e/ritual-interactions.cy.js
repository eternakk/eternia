/// <reference types="cypress" />

describe('Ritual interactions', () => {
  it('lists rituals and allows opening details and confirming trigger', () => {
    cy.visit('/');

    // Heading exists
    cy.contains('Available Rituals').should('be.visible');

    // Ensure at least one ritual item exists (panel seeds one in Cypress mode if empty)
    cy.get('[data-testid="rituals-list"]').within(() => {
      cy.get('[data-testid="ritual-item"]').first().click();
    });

    // Details modal appears
    cy.get('[data-testid="ritual-details"]').should('be.visible');
    cy.get('[data-testid="trigger-ritual-button"]').click();

    // Confirmation dialog then appears
    cy.get('[data-testid="ritual-confirmation-dialog"]').should('be.visible');
    cy.get('[data-testid="confirm-ritual-button"]').click();

    // Modal closes and success path continues (notification is ephemeral; we just ensure dialogs closed)
    cy.get('[data-testid="ritual-confirmation-dialog"]').should('not.exist');
    cy.get('[data-testid="ritual-details"]').should('not.exist');

    // The active ritual is stored in localStorage; verify UI reflects some history structure
    cy.get('[data-testid="ritual-history"]').should('be.visible');
  });
});
