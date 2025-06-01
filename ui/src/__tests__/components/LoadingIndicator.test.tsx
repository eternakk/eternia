import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '../../test/utils';
import { LoadingIndicator, LoadingSpinner } from '../../components/LoadingIndicator';
import { LoadingProvider, useLoading } from '../../contexts/LoadingContext';

// Mock the useLoading hook
vi.mock('../../contexts/LoadingContext', async () => {
  const actual = await vi.importActual('../../contexts/LoadingContext');
  return {
    ...actual,
    useLoading: vi.fn(),
  };
});

describe('LoadingIndicator', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders children when not loading', () => {
    // Mock the useLoading hook to return not loading
    vi.mocked(useLoading).mockReturnValue({
      isLoading: () => false,
      loadingOperations: [],
      startLoading: vi.fn(),
      stopLoading: vi.fn(),
    });

    render(
      <LoadingIndicator>
        <div data-testid="child">Child Content</div>
      </LoadingIndicator>
    );

    expect(screen.getByTestId('child')).toBeInTheDocument();
    expect(screen.getByText('Child Content')).toBeInTheDocument();
  });

  it('renders loading indicator when loading', () => {
    // Mock the useLoading hook to return loading
    vi.mocked(useLoading).mockReturnValue({
      isLoading: () => true,
      loadingOperations: [{ id: '1', operationKey: 'test', message: 'Loading...' }],
      startLoading: vi.fn(),
      stopLoading: vi.fn(),
    });

    render(
      <LoadingIndicator>
        <div data-testid="child">Child Content</div>
      </LoadingIndicator>
    );

    // Child content should be in the document but with opacity
    const child = screen.getByTestId('child');
    expect(child).toBeInTheDocument();
    expect(child.parentElement).toHaveClass('opacity-50');

    // Loading message should be displayed
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('uses custom fallback when provided', () => {
    // Mock the useLoading hook to return loading
    vi.mocked(useLoading).mockReturnValue({
      isLoading: () => true,
      loadingOperations: [],
      startLoading: vi.fn(),
      stopLoading: vi.fn(),
    });

    render(
      <LoadingIndicator fallback={<div data-testid="custom-fallback">Custom Fallback</div>}>
        <div data-testid="child">Child Content</div>
      </LoadingIndicator>
    );

    expect(screen.getByTestId('custom-fallback')).toBeInTheDocument();
    expect(screen.getByText('Custom Fallback')).toBeInTheDocument();
  });
});

describe('LoadingSpinner', () => {
  it('renders with default size', () => {
    const { container } = render(<LoadingSpinner />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('h-8 w-8'); // Default size is 'md'
  });

  it('renders with small size', () => {
    const { container } = render(<LoadingSpinner size="sm" />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('h-4 w-4');
  });

  it('renders with large size', () => {
    const { container } = render(<LoadingSpinner size="lg" />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveClass('h-12 w-12');
  });

  it('displays message when provided', () => {
    render(<LoadingSpinner message="Loading data..." />);

    expect(screen.getByText('Loading data...')).toBeInTheDocument();
  });
});
