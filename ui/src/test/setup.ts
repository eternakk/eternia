import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock for ResizeObserver which is not available in jsdom
window.ResizeObserver = class ResizeObserver {
  observe() {
    // do nothing
  }
  unobserve() {
    // do nothing
  }
  disconnect() {
    // do nothing
  }
} as unknown as typeof ResizeObserver;

// Mock for IntersectionObserver which is not available in jsdom
window.IntersectionObserver = class IntersectionObserver {
  callback: IntersectionObserverCallback;

  constructor(callback: IntersectionObserverCallback) {
    this.callback = callback;
  }
  observe() {
    // do nothing
  }
  unobserve() {
    // do nothing
  }
  disconnect() {
    // do nothing
  }
} as unknown as typeof IntersectionObserver;

// Mock for window.matchMedia which is not available in jsdom
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock for canvas methods used by Three.js
const mockCanvasContext = {
  measureText: () => ({ width: 0 }),
  fillRect: vi.fn(),
  fillText: vi.fn(),
  clearRect: vi.fn(),
  getImageData: vi.fn(() => ({ data: new Uint8Array(4) })),
  putImageData: vi.fn(),
  createImageData: vi.fn(() => ({ data: new Uint8Array(4) })),
  setTransform: vi.fn(),
  drawImage: vi.fn(),
  save: vi.fn(),
  restore: vi.fn(),
  beginPath: vi.fn(),
  moveTo: vi.fn(),
  lineTo: vi.fn(),
  closePath: vi.fn(),
  stroke: vi.fn(),
  translate: vi.fn(),
  scale: vi.fn(),
  rotate: vi.fn(),
  arc: vi.fn(),
  fill: vi.fn(),
  // Add required properties for CanvasRenderingContext2D
  canvas: document.createElement('canvas'),
  getContextAttributes: vi.fn(() => ({})),
  globalAlpha: 1,
  globalCompositeOperation: 'source-over',
};

HTMLCanvasElement.prototype.getContext = vi.fn((contextId) => {
  if (contextId === '2d') {
    return mockCanvasContext as unknown as CanvasRenderingContext2D;
  }
  return null;
});
