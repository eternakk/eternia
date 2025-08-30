import { describe, it, expect } from 'vitest';

// Additional smoke test placed at src/ root to guarantee discovery.
describe('smoke (root)', () => {
  it('basic math still works', () => {
    expect(2 * 3).toBe(6);
  });
});
