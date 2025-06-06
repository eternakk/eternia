# UI Architecture

This document provides an overview of the UI architecture for the Eternia project.

## Overview

The Eternia UI is built using React and TypeScript, with Tailwind CSS for styling. The architecture follows modern React best practices, including functional components, hooks, and context-based state management.

## Technology Stack

- **React**: A JavaScript library for building user interfaces
- **TypeScript**: A typed superset of JavaScript that compiles to plain JavaScript
- **Tailwind CSS**: A utility-first CSS framework
- **Vite**: A build tool that provides a faster and leaner development experience
- **ESLint**: A tool for identifying and reporting on patterns in JavaScript/TypeScript
- **Vitest**: A testing framework for React components

## Directory Structure

The UI codebase follows a standard React project structure:

```
ui/
├── public/              # Static assets
├── src/                 # Source code
│   ├── components/      # React components
│   ├── contexts/        # React contexts for state management
│   ├── hooks/           # Custom React hooks
│   ├── utils/           # Utility functions
│   ├── assets/          # Assets used in the application
│   ├── __tests__/       # Test files
│   ├── App.tsx          # Main application component
│   ├── api.ts           # API client for backend communication
│   └── main.tsx         # Entry point
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Component Architecture

The UI follows a component-based architecture where each component is responsible for a specific part of the UI. Components are organized in a hierarchy, with higher-level components composing lower-level ones.

### Component Hierarchy

```
App
├── GlobalLoadingIndicator
├── NotificationContainer
├── ControlPanel
├── ZoneViewer
│   └── ZoneCanvas
├── AgentDashboard
├── StatePanel
├── CheckPointPanel
├── RitualPanel
└── LogConsole
```

### Component Design Principles

1. **Single Responsibility**: Each component should have a single responsibility
2. **Reusability**: Components should be designed to be reusable
3. **Composability**: Components should be composable to build complex UIs
4. **Testability**: Components should be easy to test

## State Management

The Eternia UI uses React's Context API for state management. This approach allows for sharing state between components without prop drilling.

### Key Contexts

- **SimulationContext**: Manages the state of the simulation
- **NotificationContext**: Manages notification messages
- **AuthContext**: Manages authentication state

### State Flow

1. State is initialized in the context provider
2. Components consume the state using the `useContext` hook
3. Components dispatch actions to update the state
4. The context provider updates the state based on the action
5. Components re-render with the updated state

## API Integration

The UI communicates with the backend API using a dedicated API client defined in `api.ts`. This client provides methods for all API endpoints and handles authentication, error handling, and request/response formatting.

### API Client Structure

```typescript
// Example API client structure
export const api = {
  // Authentication
  login: (username: string, password: string) => { /* ... */ },
  logout: () => { /* ... */ },

  // Simulation
  startSimulation: () => { /* ... */ },
  pauseSimulation: () => { /* ... */ },
  resetSimulation: () => { /* ... */ },

  // Checkpoints
  getCheckpoints: () => { /* ... */ },
  saveCheckpoint: (name: string) => { /* ... */ },
  loadCheckpoint: (id: string) => { /* ... */ },

  // Zones
  getZones: () => { /* ... */ },
  getZoneDetails: (id: string) => { /* ... */ },

  // Agents
  getAgents: () => { /* ... */ },
  getAgentDetails: (id: string) => { /* ... */ },
};
```

### API Integration Best Practices

1. Use the API client for all backend communication
2. Handle loading states with the LoadingIndicator component
3. Handle errors with the NotificationContainer component
4. Use TypeScript interfaces for API request and response types
5. Implement retry logic for failed requests

## Event Handling

The UI handles events using a combination of React's event system and custom event handlers. Events are propagated up the component hierarchy through callback props.

### Event Flow

1. User interacts with a component (e.g., clicks a button)
2. The component calls the appropriate callback prop
3. The parent component handles the event and updates the state
4. The updated state flows back down to the components

## Responsive Design

The UI is designed to be responsive and work on different screen sizes. This is achieved using Tailwind CSS's responsive utilities and custom media queries where needed.

### Responsive Design Principles

1. Use Tailwind CSS's responsive utilities (e.g., `md:`, `lg:`)
2. Design for mobile-first, then adapt for larger screens
3. Use flexible layouts that adapt to different screen sizes
4. Test on different devices and screen sizes

## Performance Optimization

The UI architecture includes plans for several performance optimizations to ensure a smooth user experience:

1. **Code Splitting**: The application code will be split into smaller chunks that are loaded on demand (Not yet implemented)
2. **Memoization**: Components and expensive calculations will be memoized using `React.memo` and `useMemo` (Partially implemented)
3. **Virtualization**: Large lists will be virtualized to render only visible items (Not yet implemented)
4. **Lazy Loading**: Components will be loaded lazily when needed (Not yet implemented)

Note: These optimizations are planned but not yet fully implemented. See the [UI Pending Tasks](ui_pending_tasks.md) document for implementation plans.

## Accessibility

The UI architecture includes plans to follow accessibility best practices to ensure that it is usable by everyone:

1. Use semantic HTML elements (Partially implemented)
2. Provide alternative text for images (Minimally implemented)
3. Ensure proper keyboard navigation (Not yet implemented)
4. Use ARIA attributes where needed (Minimally implemented)
5. Maintain sufficient color contrast (Partially implemented)

Note: These accessibility features are planned but not yet fully implemented. See the [UI Pending Tasks](ui_pending_tasks.md) document for implementation plans.

## Testing

The UI components are tested using Vitest and React Testing Library. Tests are located in the `__tests__` directory and follow the component structure.

### Testing Approach

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test how components work together
3. **Snapshot Tests**: Ensure that the UI doesn't change unexpectedly
4. **Accessibility Tests**: Ensure that the UI is accessible

## Conclusion

The Eternia UI architecture follows modern React best practices and is designed to be maintainable, performant, and accessible. By following the principles outlined in this document, developers can contribute to the UI codebase effectively.
