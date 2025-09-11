/**
 * End-to-end tests for the dashboard functionality
 */

describe('Dashboard', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Navigate to the dashboard
    cy.visit('/');
  });

  it('should display the state panel with cycle and continuity information', () => {
    // Check that the state panel is visible
    cy.get('[data-testid="state-panel"]').should('be.visible');
    
    // Check that it contains cycle information
    cy.get('[data-testid="state-panel"]').contains('Cycle');
    
    // Check that it contains continuity information
    cy.get('[data-testid="state-panel"]').contains('Continuity');
  });

  it('should display the agent dashboard with agent information', () => {
    // Check that the agent dashboard is visible
    cy.get('[data-testid="agent-dashboard"]').should('be.visible');
    
    // Check that it contains at least one agent
    cy.get('[data-testid="agent-item"]').should('have.length.at.least', 1);
    
    // Check that agent information is displayed
    cy.get('[data-testid="agent-item"]').first().within(() => {
      cy.contains('Name');
      cy.contains('Mood');
      cy.contains('Stress');
    });
  });

  it('should be able to pause and resume the simulation', () => {
    // Click the pause button
    cy.get('[data-testid="pause-button"]').click();
    
    // Verify the simulation is paused (button text changes to "Resume")
    cy.get('[data-testid="resume-button"]').should('be.visible');
    
    // Click the resume button
    cy.get('[data-testid="resume-button"]').click();
    
    // Verify the simulation is running again (button text changes back to "Pause")
    cy.get('[data-testid="pause-button"]').should('be.visible');
  });

  it('should display zone information in the zone canvas', () => {
    // Check that the zone canvas is visible
    cy.get('[data-testid="zone-canvas"]').should('be.visible');
    
    // Click on a zone to view details
    cy.get('[data-testid="zone-element"]').first().click();
    
    // Verify zone details are displayed
    cy.get('[data-testid="zone-details"]').should('be.visible');
    cy.get('[data-testid="zone-details"]').within(() => {
      cy.contains('Name');
      cy.contains('Modifiers');
    });
  });

  it('should display notifications when events occur', () => {
    // Trigger an event that would cause a notification
    // (This is a simplified example - in a real test, you'd interact with the UI to trigger an event)
    cy.window().then((win) => {
      win.dispatchEvent(new CustomEvent('eternia:notification', { 
        detail: { type: 'info', message: 'Test notification' } 
      }));
    });
    
    // Verify the notification is displayed
    cy.get('[data-testid="notification-container"]').contains('Test notification');
  });
});