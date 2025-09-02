/**
 * End-to-end tests for zone and agent interactions
 */

describe('Zone and Agent Interactions', () => {
  beforeEach(() => {
    // Login before each test
    cy.login();
    
    // Navigate to the main page
    cy.visit('/');
  });

  it('should allow viewing zone details when clicking on a zone', () => {
    // Click on a zone in the zone canvas
    cy.get('[data-testid="zone-element"]').first().click();
    
    // Verify zone details are displayed
    cy.get('[data-testid="zone-details"]').should('be.visible');
    
    // Verify zone details contain expected information
    cy.get('[data-testid="zone-details"]').within(() => {
      cy.contains('Name');
      cy.contains('Origin');
      cy.contains('Complexity');
      cy.contains('Modifiers');
    });
    
    // Close zone details
    cy.get('[data-testid="close-zone-details"]').click();
    cy.get('[data-testid="zone-details"]').should('not.exist');
  });

  it('should display agent information in the agent dashboard', () => {
    // Check that the agent dashboard is visible
    cy.get('[data-testid="agent-dashboard"]').should('be.visible');
    
    // Click on an agent to view details
    cy.get('[data-testid="agent-item"]').first().click();
    
    // Verify agent details are displayed
    cy.get('[data-testid="agent-details"]').should('be.visible');
    
    // Verify agent details contain expected information
    cy.get('[data-testid="agent-details"]').within(() => {
      cy.contains('Name');
      cy.contains('Role');
      cy.contains('Emotion');
      cy.contains('Current Zone');
    });
    
    // Close agent details
    cy.get('[data-testid="close-agent-details"]').click();
    cy.get('[data-testid="agent-details"]').should('not.exist');
  });

  it('should show the relationship between agents and zones', () => {
    // Read agent name and zone from the first agent card, then act globally
    cy.get('[data-testid="agent-item"]').first().then(($item) => {
      const agentName = $item.find('[data-testid="agent-name"]').text().trim();
      const agentZone = $item.find('[data-testid="agent-zone"]').text().trim();

      // Click on the zone that matches the agent's zone
      cy.get('[data-testid="zone-element"]').contains(agentZone).click();

      // Verify zone details show the agent is in this zone
      cy.get('[data-testid="zone-details"]').within(() => {
        cy.contains('Agents in this zone');
        cy.contains(agentName);
      });
    });
  });

  it('should update the UI when an agent changes zones', () => {
    // This test simulates an agent changing zones and verifies the UI updates
    // In a real application, you would interact with the UI to move an agent
    // Here we'll use a custom event to simulate the backend update
    
    cy.window().then((win) => {
      // Simulate an agent moving to a new zone
      win.dispatchEvent(new CustomEvent('eternia:agent-moved', { 
        detail: { 
          agentId: '1', 
          fromZone: 'OldZone', 
          toZone: 'NewZone' 
        } 
      }));
    });
    
    // Verify the agent dashboard updates to show the new zone
    cy.get('[data-testid="agent-item"]').contains('NewZone');
    
    // Verify the zone canvas updates to show the agent in the new zone
    cy.get('[data-testid="zone-element"]').contains('NewZone').click();
    cy.get('[data-testid="zone-details"]').within(() => {
      cy.contains('Agents in this zone');
    });
  });

  it('should show emotion effects on zones', () => {
    // Click on a zone to view details
    cy.get('[data-testid="zone-element"]').first().click();
    
    // Verify zone details show emotion information
    cy.get('[data-testid="zone-details"]').within(() => {
      cy.contains('Emotion');
    });
    
    // Simulate an emotion change event
    cy.window().then((win) => {
      win.dispatchEvent(new CustomEvent('eternia:emotion-changed', { 
        detail: { 
          zoneId: '1', 
          emotion: 'Joyful', 
          intensity: 0.8 
        } 
      }));
    });
    
    // Verify the zone details update to show the new emotion
    cy.get('[data-testid="zone-details"]').within(() => {
      cy.contains('Joyful');
    });
  });
});