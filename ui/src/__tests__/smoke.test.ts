import { describe, it, expect } from 'vitest';

// Minimal smoke test to ensure Vitest discovers tests and coverage can run.
describe('smoke', () => {
  it('runs a basic assertion', () => {
    expect(1 + 1).toBe(2);
  });
});
