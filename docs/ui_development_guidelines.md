# UI Development Guidelines

This document outlines the guidelines and best practices for UI development in the Eternia project.

## Coding Standards

### General Guidelines

1. **Use TypeScript**: All UI code should be written in TypeScript to ensure type safety.
2. **Functional Components**: Use functional components with hooks instead of class components.
3. **Named Exports**: Use named exports instead of default exports for better refactoring support.
4. **File Organization**: Each component should be in its own file with a `.tsx` extension.
5. **Component Naming**: Use PascalCase for component names (e.g., `AgentDashboard.tsx`).
6. **Prop Types**: Define prop types using TypeScript interfaces.
7. **Destructuring Props**: Destructure props in function parameters.
8. **Default Props**: Provide default values for optional props.

### Example Component Structure

```tsx
import React from 'react';

// Define prop types
interface ButtonProps {
  label: string;
  onClick: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}

// Component with destructured props and default values
export const Button: React.FC<ButtonProps> = ({
  label,
  onClick,
  disabled = false,
  variant = 'primary',
}) => {
  // Component logic here
  
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
};
```

## State Management

### Context API

The Eternia UI uses React's Context API for state management. Follow these guidelines when working with context:

1. **Create Separate Contexts**: Create separate contexts for different parts of the application (e.g., `SimulationContext`, `NotificationContext`).
2. **Use TypeScript**: Define types for context state and actions.
3. **Provide Default Values**: Always provide default values for contexts.
4. **Use Reducers**: Use reducers for complex state logic.
5. **Memoize Context Values**: Use `useMemo` to memoize context values to prevent unnecessary re-renders.

### Example Context Structure

```tsx
import React, { createContext, useContext, useReducer, useMemo } from 'react';

// Define state type
interface SimulationState {
  isRunning: boolean;
  speed: number;
  // Other state properties
}

// Define action types
type SimulationAction =
  | { type: 'START_SIMULATION' }
  | { type: 'PAUSE_SIMULATION' }
  | { type: 'SET_SPEED'; payload: number };

// Define context type
interface SimulationContextType {
  state: SimulationState;
  dispatch: React.Dispatch<SimulationAction>;
}

// Create context with default value
const SimulationContext = createContext<SimulationContextType>({
  state: {
    isRunning: false,
    speed: 1,
  },
  dispatch: () => {},
});

// Reducer function
const simulationReducer = (state: SimulationState, action: SimulationAction): SimulationState => {
  switch (action.type) {
    case 'START_SIMULATION':
      return { ...state, isRunning: true };
    case 'PAUSE_SIMULATION':
      return { ...state, isRunning: false };
    case 'SET_SPEED':
      return { ...state, speed: action.payload };
    default:
      return state;
  }
};

// Provider component
export const SimulationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(simulationReducer, {
    isRunning: false,
    speed: 1,
  });
  
  // Memoize context value
  const contextValue = useMemo(() => ({ state, dispatch }), [state]);
  
  return (
    <SimulationContext.Provider value={contextValue}>
      {children}
    </SimulationContext.Provider>
  );
};

// Custom hook for using the context
export const useSimulation = () => useContext(SimulationContext);
```

## Component Design

### Component Hierarchy

Organize components in a hierarchy, with higher-level components composing lower-level ones. Follow these guidelines:

1. **Single Responsibility**: Each component should have a single responsibility.
2. **Reusability**: Design components to be reusable.
3. **Composability**: Components should be composable to build complex UIs.
4. **Testability**: Components should be easy to test.

### Component Types

Organize components into these categories:

1. **UI Components**: Presentational components that render UI elements (e.g., `Button`, `Card`).
2. **Container Components**: Components that manage state and pass it to UI components.
3. **Page Components**: Top-level components that represent pages or views.
4. **Layout Components**: Components that define the layout of the application (e.g., `Header`, `Sidebar`).

## Styling

### Tailwind CSS

The Eternia UI uses Tailwind CSS for styling. Follow these guidelines:

1. **Use Utility Classes**: Use Tailwind's utility classes for styling.
2. **Responsive Design**: Use Tailwind's responsive utilities (e.g., `md:`, `lg:`) for responsive design.
3. **Custom Classes**: For complex components, consider creating custom classes in a separate CSS file.
4. **Theme Consistency**: Use the theme colors and spacing defined in `tailwind.config.js`.

### Example Styling

```tsx
// Using Tailwind utility classes
<div className="flex flex-col p-4 bg-gray-100 rounded-lg shadow-md">
  <h2 className="text-xl font-bold text-gray-800 mb-2">Title</h2>
  <p className="text-gray-600">Content</p>
  <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
    Click Me
  </button>
</div>
```

## Performance Optimization

### Memoization

Use memoization to prevent unnecessary re-renders:

1. **React.memo**: Use `React.memo` for components that render the same result given the same props.
2. **useMemo**: Use `useMemo` for expensive calculations.
3. **useCallback**: Use `useCallback` for functions passed as props to child components.

### Code Splitting

Use code splitting to reduce the initial bundle size:

1. **Dynamic Imports**: Use dynamic imports for large components or libraries.
2. **React.lazy**: Use `React.lazy` for component code splitting.
3. **Suspense**: Use `Suspense` with `React.lazy` for loading states.

### Example Code Splitting

```tsx
import React, { Suspense, lazy } from 'react';

// Lazy load a component
const LazyComponent = lazy(() => import('./LazyComponent'));

export const App: React.FC = () => {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <LazyComponent />
      </Suspense>
    </div>
  );
};
```

## Testing

### Testing Framework

The Eternia UI uses Vitest and React Testing Library for testing. Follow these guidelines:

1. **Component Tests**: Write tests for all components.
2. **Integration Tests**: Write integration tests for component interactions.
3. **Snapshot Tests**: Use snapshot tests to detect unexpected UI changes.
4. **Accessibility Tests**: Test for accessibility issues.

### Example Test

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with the correct label', () => {
    render(<Button label="Click Me" onClick={() => {}} />);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button label="Click Me" onClick={handleClick} />);
    fireEvent.click(screen.getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('is disabled when disabled prop is true', () => {
    render(<Button label="Click Me" onClick={() => {}} disabled />);
    expect(screen.getByText('Click Me')).toBeDisabled();
  });
});
```

## Accessibility

### Guidelines

Follow these accessibility guidelines:

1. **Semantic HTML**: Use semantic HTML elements (e.g., `<button>`, `<nav>`, `<header>`).
2. **ARIA Attributes**: Use ARIA attributes when necessary.
3. **Keyboard Navigation**: Ensure all interactive elements are keyboard accessible.
4. **Color Contrast**: Maintain sufficient color contrast for text.
5. **Screen Readers**: Ensure content is accessible to screen readers.

### Example Accessibility Implementation

```tsx
// Accessible button with ARIA attributes
<button
  aria-label="Close dialog"
  aria-pressed={isPressed}
  onClick={handleClick}
  className="p-2 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
>
  <span className="sr-only">Close</span>
  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
</button>
```

## Error Handling

### Guidelines

Follow these error handling guidelines:

1. **Error Boundaries**: Use React error boundaries to catch and handle errors.
2. **Fallback UI**: Provide fallback UI for error states.
3. **Error Messages**: Display user-friendly error messages.
4. **API Errors**: Handle API errors gracefully.

### Example Error Handling

```tsx
import React, { ErrorInfo, Component } from 'react';

interface ErrorBoundaryProps {
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  render(): React.ReactNode {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <h2 className="text-lg font-bold">Something went wrong</h2>
          <p>{this.state.error?.message || 'An error occurred'}</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

## Conclusion

Following these guidelines will help ensure that the Eternia UI is maintainable, performant, and accessible. If you have any questions or need clarification on any of these guidelines, please refer to the [UI Architecture Documentation](ui_architecture.md) or reach out to the team.