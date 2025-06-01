import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '../../test/utils';
import NotificationContainer from '../../components/NotificationContainer';
import { useNotification } from '../../contexts/NotificationContext';

// Mock the useNotification hook
vi.mock('../../contexts/NotificationContext', async () => {
  const actual = await vi.importActual('../../contexts/NotificationContext');
  return {
    ...actual,
    useNotification: vi.fn(),
  };
});

describe('NotificationContainer', () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it('renders nothing when there are no notifications', () => {
    // Mock the useNotification hook to return empty notifications
    vi.mocked(useNotification).mockReturnValue({
      notifications: [],
      addNotification: vi.fn(),
      removeNotification: vi.fn(),
    });

    const { container } = render(<NotificationContainer />);
    expect(container.firstChild).toBeNull();
  });

  it('renders info notification correctly', () => {
    const removeNotification = vi.fn();
    
    // Mock the useNotification hook to return an info notification
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'info', message: 'This is an info message' },
      ],
      addNotification: vi.fn(),
      removeNotification,
    });

    render(<NotificationContainer />);
    
    // Check that the notification is rendered with the correct styles and content
    const notification = screen.getByText('This is an info message');
    expect(notification).toBeInTheDocument();
    
    // Check that the parent element has the correct background color class
    const notificationContainer = notification.closest('div[class*="bg-blue-100"]');
    expect(notificationContainer).toBeInTheDocument();
    
    // Check that the info icon is rendered
    expect(screen.getByText('ℹ️')).toBeInTheDocument();
  });

  it('renders error notification correctly', () => {
    const removeNotification = vi.fn();
    
    // Mock the useNotification hook to return an error notification
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'error', message: 'This is an error message' },
      ],
      addNotification: vi.fn(),
      removeNotification,
    });

    render(<NotificationContainer />);
    
    // Check that the notification is rendered with the correct styles and content
    const notification = screen.getByText('This is an error message');
    expect(notification).toBeInTheDocument();
    
    // Check that the parent element has the correct background color class
    const notificationContainer = notification.closest('div[class*="bg-red-100"]');
    expect(notificationContainer).toBeInTheDocument();
    
    // Check that the error icon is rendered
    expect(screen.getByText('❌')).toBeInTheDocument();
  });

  it('calls removeNotification when close button is clicked', () => {
    const removeNotification = vi.fn();
    
    // Mock the useNotification hook to return a notification
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'info', message: 'This is an info message' },
      ],
      addNotification: vi.fn(),
      removeNotification,
    });

    render(<NotificationContainer />);
    
    // Click the close button
    const closeButton = screen.getByRole('button', { name: /close notification/i });
    fireEvent.click(closeButton);
    
    // Check that removeNotification was called with the correct ID
    expect(removeNotification).toHaveBeenCalledWith('1');
  });

  it('renders multiple notifications correctly', () => {
    const removeNotification = vi.fn();
    
    // Mock the useNotification hook to return multiple notifications
    vi.mocked(useNotification).mockReturnValue({
      notifications: [
        { id: '1', type: 'info', message: 'This is an info message' },
        { id: '2', type: 'error', message: 'This is an error message' },
        { id: '3', type: 'warning', message: 'This is a warning message' },
      ],
      addNotification: vi.fn(),
      removeNotification,
    });

    render(<NotificationContainer />);
    
    // Check that all notifications are rendered
    expect(screen.getByText('This is an info message')).toBeInTheDocument();
    expect(screen.getByText('This is an error message')).toBeInTheDocument();
    expect(screen.getByText('This is a warning message')).toBeInTheDocument();
    
    // Check that all icons are rendered
    expect(screen.getByText('ℹ️')).toBeInTheDocument();
    expect(screen.getByText('❌')).toBeInTheDocument();
    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });
});