/// <reference types="cypress" />

describe('Zone and Agent interactions', () => {
  it('shows zones list and reflects agent move events in the dashboard', () => {
    cy.visit('/');

    // Zones heading present
    cy.contains('h2', 'Zones').should('be.visible');

    // There should be at least one zone card from stub
    cy.get('#zones-grid').within(() => {
      cy.contains('Zone-α').should('exist');
    });

    // Dispatch a synthetic agent-moved event to update dashboard
    cy.window().then((win) => {
      const evt = new CustomEvent('eternia:agent-moved', { detail: { toZone: 'Zone-β' } });
      win.dispatchEvent(evt);
    });

    // AgentDashboard should reflect new zone label
    cy.contains('Zone: Zone-β').should('exist');
  });
});
