import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import LazyLoad, { createLazyComponent } from '../components/LazyLoad';

// Mock LoadingSpinner to make fallback detectable
vi.mock('../components/LoadingIndicator', () => ({
  __esModule: true,
  LoadingSpinner: ({ size }: { size?: 'sm' | 'md' | 'lg' }) => (
    <div data-testid={`spinner-${size ?? 'md'}`}>spinner</div>
  ),
}));

describe('components/LazyLoad and createLazyComponent', () => {
  it('createLazyComponent renders the loaded component content', async () => {
    const Hello: React.FC = () => <div>hello lazy</div>;
    const Lazy = createLazyComponent(() => Promise.resolve({ default: Hello }));
    render(<Lazy />);
    expect(await screen.findByText('hello lazy')).toBeInTheDocument();
  });

  it('LazyLoad shows fallback until component resolves', async () => {
    let resolveModule: ((m: { default: React.ComponentType }) => void) | undefined;
    const factory = () => new Promise<{ default: React.ComponentType }>((resolve) => {
      resolveModule = resolve;
    });

    render(<LazyLoad component={factory} />);

    // Fallback spinner should initially be visible
    expect(screen.getByTestId('spinner-md')).toBeInTheDocument();

    // Resolve the lazy component
    const Loaded: React.FC = () => <div>loaded later</div>;
    resolveModule?.({ default: Loaded });

    expect(await screen.findByText('loaded later')).toBeInTheDocument();
  });
});
