import { describe, it, expect, vi, beforeEach } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock heavy components to lightweight stubs
vi.mock('@/components/StatePanel', () => ({ __esModule: true, default: () => <div data-testid="state-panel" /> }));
vi.mock('@/components/ControlPanel', () => ({ __esModule: true, default: () => <div data-testid="control-panel" /> }));
vi.mock('@/components/CheckPointPanel.tsx', () => ({ __esModule: true, default: () => <div data-testid="checkpoint-panel" /> }));
vi.mock('@/components/AgentDashboard', () => ({ __esModule: true, default: () => <div data-testid="agent-dashboard" /> }));
vi.mock('@/components/ZoneViewer', () => ({ __esModule: true, default: () => <div data-testid="zone-viewer" /> }));
vi.mock('@/components/NotificationContainer', () => ({ __esModule: true, default: () => <div data-testid="notification-container" /> }));
vi.mock('@/components/GlobalLoadingIndicator', () => ({ __esModule: true, default: () => <div data-testid="global-loading" /> }));

// Stub lazy loader to immediate components
vi.mock('@/components/LazyLoad', () => ({
  __esModule: true,
  createLazyComponent: () => () => <div data-testid="lazy-component" />,
  default: ({ component }: { component: () => Promise<{ default: React.ComponentType }> }) => {
    // Render immediately with a placeholder; execute factory to cover branch
    void component();
    return <div data-testid="lazy-default" />;
  },
}));

// Make providers render children directly
vi.mock('@/contexts/NotificationContext', async () => {
  const mod = await vi.importActual<typeof import('@/contexts/NotificationContext')>('@/contexts/NotificationContext');
  return { __esModule: true, ...mod, NotificationProvider: ({ children }: { children: React.ReactNode }) => <>{children}</> };
});
vi.mock('@/contexts/LoadingContext', async () => {
  const mod = await vi.importActual<typeof import('@/contexts/LoadingContext')>('@/contexts/LoadingContext');
  return { __esModule: true, ...mod, LoadingProvider: ({ children }: { children: React.ReactNode }) => <>{children}</> };
});
vi.mock('@/contexts/FeatureFlagContext', async () => {
  const mod = await vi.importActual<typeof import('@/contexts/FeatureFlagContext')>('@/contexts/FeatureFlagContext');
  return { __esModule: true, ...mod, FeatureFlagProvider: ({ children }: { children: React.ReactNode }) => <>{children}</> };
});
vi.mock('@/contexts/WorldStateContext', async () => {
  const mod = await vi.importActual<typeof import('@/contexts/WorldStateContext')>('@/contexts/WorldStateContext');
  return { __esModule: true, ...mod, WorldStateProvider: ({ children }: { children: React.ReactNode }) => <>{children}</> };
});

import App from '@/App';

describe('App smoke', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the header and stubs for children', () => {
    render(<App />);
    expect(screen.getByText('Eterna Mission‑Control')).toBeInTheDocument();
    expect(screen.getByTestId('state-panel')).toBeInTheDocument();
    expect(screen.getByTestId('agent-dashboard')).toBeInTheDocument();
    expect(screen.getByTestId('control-panel')).toBeInTheDocument();
    expect(screen.getByTestId('checkpoint-panel')).toBeInTheDocument();
    expect(screen.getAllByTestId('lazy-component').length).toBeGreaterThan(0);
    expect(screen.getByTestId('notification-container')).toBeInTheDocument();
    expect(screen.getByTestId('global-loading')).toBeInTheDocument();
  });
});
