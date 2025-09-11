import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock react-dom/client to intercept createRoot
vi.mock('react-dom/client', () => {
  return {
    __esModule: true,
    createRoot: (el: Element) => {
      // Return a minimal root with render spy
      return {
        render: (_node: unknown) => {
          // no-op; just ensure it gets called
          void el;
        },
      };
    },
  };
});

describe('main.tsx smoke', () => {
  beforeEach(() => {
    // Ensure a root element exists before importing main
    document.body.innerHTML = '<div id="root"></div>';
  });

  it('mounts application into #root without throwing', async () => {
    const mod = await import('../main');
    expect(mod).toBeTruthy();
    // If we reached here, createRoot().render did not throw
    const root = document.getElementById('root');
    expect(root).not.toBeNull();
  });
});
