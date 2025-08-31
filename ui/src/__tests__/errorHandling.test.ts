import { describe, it, expect, vi } from 'vitest';
import { act } from '@testing-library/react';

// Use hoisted storage for the mock to avoid TDZ with vi.mock hoisting
const h = vi.hoisted(() => {
  return {
    addNotificationMock: vi.fn() as ((arg: unknown) => void) & { mock: { calls: unknown[][] }, mockClear?: () => void },
  };
});

// Mock NotificationContext to avoid needing React providers and to capture calls
vi.mock('../contexts/NotificationContext', () => {
  return {
    __esModule: true,
    useNotification: () => ({ addNotification: h.addNotificationMock }),
  };
});

import axios from 'axios';

// Helper to construct an axios-like error easily
function makeAxiosError(partial: Record<string, unknown>) {
  return { isAxiosError: true, ...partial } as unknown as Parameters<typeof axios.isAxiosError>[0];
}

// Helper to read last notification arg safely
const getLastNotificationArg = () => {
  const calls = h.addNotificationMock.mock.calls as unknown[][];
  const last = calls[calls.length - 1]?.[0] ?? {};
  return last as { type?: string; message?: unknown };
};

// Helper to safely read message from an unknown call arg (for tsc strict)
const readMsg = (arg: unknown) => String((arg as { message?: unknown })?.message);

describe('utils/errorHandling - handleApiError and withErrorHandling', () => {
  it('shows auth error messages for 401/403', async () => {
    const { useErrorHandler } = await import('../utils/errorHandling');
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ response: { status: 401, data: {} } }));
      handleApiError(makeAxiosError({ response: { status: 403, data: {} } }));
    });

    const last = getLastNotificationArg();
    expect(last?.type).toBe('error');
    expect(String(last?.message)).toContain('Authentication error');
  });

  it('shows not found message for 404 and server error for 500', async () => {
    const { useErrorHandler } = await import('../utils/errorHandling');
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ response: { status: 404, data: {} } }));
      handleApiError(makeAxiosError({ response: { status: 500, data: {} } }));
    });

    const calls = h.addNotificationMock.mock.calls as unknown[][];
    const lastTwo = calls.slice(-2);
    expect(readMsg(lastTwo[0]?.[0])).toContain('not found');
    expect(readMsg(lastTwo[1]?.[0])).toContain('Server error');
  });

  it('uses server-provided message when available in response.data.message', async () => {
    const { useErrorHandler } = await import('../utils/errorHandling');
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ response: { status: 418, data: { message: 'I am a teapot' } } }));
    });

    const calls = h.addNotificationMock.mock.calls as unknown[][];
    const last = calls[calls.length - 1];
    expect(readMsg(last?.[0])).toContain('I am a teapot');
  });

  it('handles request with no response', async () => {
    const { useErrorHandler } = await import('../utils/errorHandling');
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ request: {} }));
    });

    const calls = h.addNotificationMock.mock.calls as unknown[][];
    const last = calls[calls.length - 1];
    expect(readMsg(last?.[0])).toContain('No response');
  });

  it('withErrorHandling returns undefined and sends a notification when fn throws', async () => {
    h.addNotificationMock.mockClear?.();
    const { useErrorHandler } = await import('../utils/errorHandling');
    const { withErrorHandling } = useErrorHandler();

    const throwing = async () => {
      throw new Error('boom');
    };
    const safe = withErrorHandling(throwing, 'Custom message');

    let result: unknown;
    await act(async () => {
      result = await safe();
    });

    expect(result).toBeUndefined();
    const calls = h.addNotificationMock.mock.calls as unknown[][];
    expect(calls.length).toBeGreaterThan(0);
    expect(readMsg(calls[calls.length - 1]?.[0])).toContain('Custom message');
  });
});
