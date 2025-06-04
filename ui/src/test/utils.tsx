import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { NotificationProvider } from '../contexts/NotificationContext';
import { LoadingProvider } from '../contexts/LoadingContext';
import { AppStateProvider } from '../contexts/AppStateContext';

// Create a custom render function that includes all providers
const AllProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <NotificationProvider>
      <LoadingProvider>
        <AppStateProvider refreshInterval={1000}>
          {children}
        </AppStateProvider>
      </LoadingProvider>
    </NotificationProvider>
  );
};

// Custom render function that wraps the component with all providers
const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllProviders, ...options });

// Re-export everything from testing-library
export * from '@testing-library/react';

// Override the render method
export { customRender as render };