import { describe, it, expect, vi } from 'vitest';
import { act } from '@testing-library/react';

// Mock NotificationContext to avoid needing React providers and to capture calls
vi.mock('../contexts/NotificationContext', () => {
  const mockAddNotification = vi.fn();
  return {
    __esModule: true,
    useNotification: () => ({ addNotification: mockAddNotification }),
    mockAddNotification,
  };
});

import axios from 'axios';
import { useErrorHandler } from '../utils/errorHandling';
import { mockAddNotification } from '../contexts/NotificationContext';

// Helper to construct an axios-like error easily
function makeAxiosError(partial: Record<string, unknown>) {
  return { isAxiosError: true, ...partial } as unknown as Parameters<typeof axios.isAxiosError>[0];
}

// Narrow Vitest mock type without using `any`
const asMock = (fn: unknown) => fn as { mock: { calls: unknown[][] }, mockClear?: () => void };

describe('utils/errorHandling - handleApiError and withErrorHandling', () => {
  it('shows auth error messages for 401/403', async () => {
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ response: { status: 401, data: {} } }));
      handleApiError(makeAxiosError({ response: { status: 403, data: {} } }));
    });

    const calls = asMock(mockAddNotification).mock.calls as unknown[][];
    const last = calls[calls.length - 1];
    expect(last?.[0]?.type).toBe('error');
    expect(String(last?.[0]?.message)).toContain('Authentication error');
  });

  it('shows not found message for 404 and server error for 500', async () => {
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ response: { status: 404, data: {} } }));
      handleApiError(makeAxiosError({ response: { status: 500, data: {} } }));
    });

    const calls = asMock(mockAddNotification).mock.calls as unknown[][];
    const lastTwo = calls.slice(-2);
    expect(String(lastTwo[0][0].message)).toContain('not found');
    expect(String(lastTwo[1][0].message)).toContain('Server error');
  });

  it('uses server-provided message when available in response.data.message', async () => {
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ response: { status: 418, data: { message: 'I am a teapot' } } }));
    });

    const calls = asMock(mockAddNotification).mock.calls as unknown[][];
    const last = calls[calls.length - 1];
    expect(String(last[0].message)).toContain('I am a teapot');
  });

  it('handles request with no response', async () => {
    const { handleApiError } = useErrorHandler();

    await act(async () => {
      handleApiError(makeAxiosError({ request: {} }));
    });

    const calls = asMock(mockAddNotification).mock.calls as unknown[][];
    const last = calls[calls.length - 1];
    expect(String(last[0].message)).toContain('No response');
  });

  it('withErrorHandling returns undefined and sends a notification when fn throws', async () => {
    asMock(mockAddNotification).mockClear?.();
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
    const calls = asMock(mockAddNotification).mock.calls as unknown[][];
    expect(calls.length).toBeGreaterThan(0);
    expect(String(calls[calls.length - 1][0].message)).toContain('Custom message');
  });
});
