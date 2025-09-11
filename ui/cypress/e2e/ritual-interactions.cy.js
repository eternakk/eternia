/**
 * End-to-end tests for ritual interactions
 */

describe('Ritual Interactions', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Navigate to the rituals page
    cy.visit('/rituals');
  });

  it('should display a list of available rituals', () => {
    // Check that the rituals list is visible
    cy.get('[data-testid="rituals-list"]').should('be.visible');
    
    // Check that it contains at least one ritual
    cy.get('[data-testid="ritual-item"]').should('have.length.at.least', 1);
    
    // Check that ritual information is displayed
    cy.get('[data-testid="ritual-item"]').first().within(() => {
      cy.contains('Name');
      cy.contains('Purpose');
    });
  });

  it('should allow viewing ritual details', () => {
    // Click on a ritual to view details
    cy.get('[data-testid="ritual-item"]').first().click();
    
    // Verify ritual details are displayed
    cy.get('[data-testid="ritual-details"]').should('be.visible');
    
    // Verify ritual details contain expected information
    cy.get('[data-testid="ritual-details"]').within(() => {
      cy.contains('Name');
      cy.contains('Purpose');
      cy.contains('Steps');
      cy.contains('Symbolic Elements');
    });
    
    // Close ritual details
    cy.get('[data-testid="close-ritual-details"]').click();
    cy.get('[data-testid="ritual-details"]').should('not.exist');
  });

  it('should allow triggering a ritual', () => {
    // Click on a ritual to view details
    cy.get('[data-testid="ritual-item"]').first().click();
    
    // Click the trigger button
    cy.get('[data-testid="trigger-ritual-button"]').click();
    
    // Verify confirmation dialog appears
    cy.get('[data-testid="ritual-confirmation-dialog"]').should('be.visible');
    
    // Confirm the ritual
    cy.get('[data-testid="confirm-ritual-button"]').click();
    
    // Verify success notification appears
    cy.get('[data-testid="notification-container"]').contains('Ritual triggered successfully');
    
    // Verify the ritual status changes to "In Progress" or similar
    cy.get('[data-testid="ritual-status"]').contains('In Progress');
  });

  it('should show ritual effects on the system', () => {
    // Get the name of the first ritual
    let ritualName;
    cy.get('[data-testid="ritual-item"]').first().within(() => {
      cy.get('[data-testid="ritual-name"]').invoke('text').then((text) => {
        ritualName = text;
      });
    });
    
    // Trigger the ritual
    cy.get('[data-testid="ritual-item"]').first().click();
    cy.get('[data-testid="trigger-ritual-button"]').click();
    cy.get('[data-testid="confirm-ritual-button"]').click();
    
    // Navigate to the dashboard to see effects
    cy.visit('/');
    
    // Verify the ritual effects are visible in the state panel
    cy.get('[data-testid="state-panel"]').within(() => {
      cy.contains('Active Rituals');
      cy.contains(ritualName);
    });
    
    // Verify the ritual effects are visible in the zone canvas
    // (This assumes rituals affect zones in some way)
    cy.get('[data-testid="zone-canvas"]').should('be.visible');
    cy.get('[data-testid="ritual-effect-indicator"]').should('be.visible');
  });

  it('should handle ritual completion', () => {
    // Simulate a ritual completion event
    cy.window().then((win) => {
      win.dispatchEvent(new CustomEvent('eternia:ritual-completed', { 
        detail: { 
          ritualId: '1', 
          ritualName: 'Test Ritual', 
          outcome: 'success' 
        } 
      }));
    });
    
    // Verify completion notification appears
    cy.get('[data-testid="notification-container"]').contains('Ritual completed');
    
    // Navigate to rituals page
    cy.visit('/rituals');
    
    // Verify the ritual status is updated
    cy.get('[data-testid="ritual-item"]').contains('Test Ritual').parent().within(() => {
      cy.get('[data-testid="ritual-status"]').contains('Completed');
    });
    
    // Verify ritual history is updated
    cy.get('[data-testid="ritual-history"]').contains('Test Ritual');
  });
});