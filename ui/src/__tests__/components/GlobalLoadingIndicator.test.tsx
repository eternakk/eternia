import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '../../test/utils';
import { useLoading } from '../../contexts/LoadingContext';
import GlobalLoadingIndicator from '../../components/GlobalLoadingIndicator';

// Mock the useLoading hook
vi.mock('../../contexts/LoadingContext', async () => {
  const actual = await vi.importActual('../../contexts/LoadingContext');
  return {
    ...actual,
    useLoading: vi.fn(),
  };
});

describe('GlobalLoadingIndicator', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders nothing when not loading', () => {
    // Mock the useLoading hook to return not loading
    vi.mocked(useLoading).mockReturnValue({
      isLoading: () => false,
      loadingOperations: [],
      startLoading: vi.fn(),
      stopLoading: vi.fn(),
    });

    const { container } = render(<GlobalLoadingIndicator />);
    expect(container.firstChild).toBeNull();
  });

  it('renders loading indicator when loading', () => {
    // Mock the useLoading hook to return loading
    vi.mocked(useLoading).mockReturnValue({
      isLoading: () => true,
      loadingOperations: [{ id: '1', operationKey: 'test', message: 'Loading...' }],
      startLoading: vi.fn(),
      stopLoading: vi.fn(),
    });

    render(<GlobalLoadingIndicator />);

    // Check that the loading indicator is rendered
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders default message when no message is provided', () => {
    // Mock the useLoading hook to return loading but without a message
    vi.mocked(useLoading).mockReturnValue({
      isLoading: () => true,
      loadingOperations: [{ id: '1', operationKey: 'test' }],
      startLoading: vi.fn(),
      stopLoading: vi.fn(),
    });

    render(<GlobalLoadingIndicator />);

    // Check that the default loading message is rendered
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
