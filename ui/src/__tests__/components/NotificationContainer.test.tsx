import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import NotificationContainer from '../../components/NotificationContainer';
import { useNotification } from '../../contexts/NotificationContext';

// Mock the useNotification hook so we can control notifications
vi.mock('../../contexts/NotificationContext', async () => {
  const actual = await vi.importActual<typeof import('../../contexts/NotificationContext')>(
    '../../contexts/NotificationContext'
  );
  return {
    __esModule: true,
    ...actual,
    useNotification: vi.fn(),
  };
});

type MockNotification = {
  id: string;
  type: 'info' | 'error' | 'warning' | 'success';
  message: string;
};

// vi.mocked will provide proper typing for mocked hooks

describe('NotificationContainer', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders nothing when there are no notifications', () => {
    vi.mocked(useNotification).mockReturnValue({
      notifications: [],
      addNotification: vi.fn(),
      removeNotification: vi.fn(),
    } as unknown as ReturnType<typeof useNotification>);

    const { container } = render(<NotificationContainer />);
    expect(container.firstChild).toBeNull();
  });

  it('renders info notification with icon and styles', () => {
    const removeNotification = vi.fn();
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'info', message: 'This is an info message' } as MockNotification,
      ],
      addNotification: vi.fn(),
      removeNotification,
    } as unknown as ReturnType<typeof useNotification>);

    render(<NotificationContainer />);

    const notification = screen.getByText('This is an info message');
    expect(notification).toBeInTheDocument();

    const notificationContainer = notification.closest('div[class*="bg-blue-100"]');
    expect(notificationContainer).toBeInTheDocument();

    // Info icon
    expect(screen.getByText('ℹ️')).toBeInTheDocument();
  });

  it('renders error notification with icon and styles', () => {
    const removeNotification = vi.fn();
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'error', message: 'This is an error message' } as MockNotification,
      ],
      addNotification: vi.fn(),
      removeNotification,
    } as unknown as ReturnType<typeof useNotification>);

    render(<NotificationContainer />);

    const notification = screen.getByText('This is an error message');
    expect(notification).toBeInTheDocument();

    const notificationContainer = notification.closest('div[class*="bg-red-100"]');
    expect(notificationContainer).toBeInTheDocument();

    // Error icon
    expect(screen.getByText('❌')).toBeInTheDocument();
  });

  it('calls removeNotification when close button is clicked', () => {
    const removeNotification = vi.fn();
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'info', message: 'This is an info message' } as MockNotification,
      ],
      addNotification: vi.fn(),
      removeNotification,
    } as unknown as ReturnType<typeof useNotification>);

    render(<NotificationContainer />);

    const closeButton = screen.getByRole('button', { name: /close notification/i });
    fireEvent.click(closeButton);

    expect(removeNotification).toHaveBeenCalledWith('1');
  });

  it('renders multiple notifications and their icons', () => {
    const removeNotification = vi.fn();
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'info', message: 'This is an info message' } as MockNotification,
        { id: '2', type: 'error', message: 'This is an error message' } as MockNotification,
        { id: '3', type: 'warning', message: 'This is a warning message' } as MockNotification,
      ],
      addNotification: vi.fn(),
      removeNotification,
    } as unknown as ReturnType<typeof useNotification>);

    render(<NotificationContainer />);

    expect(screen.getByText('This is an info message')).toBeInTheDocument();
    expect(screen.getByText('This is an error message')).toBeInTheDocument();
    expect(screen.getByText('This is a warning message')).toBeInTheDocument();

    expect(screen.getByText('ℹ️')).toBeInTheDocument();
    expect(screen.getByText('❌')).toBeInTheDocument();
    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });
});
