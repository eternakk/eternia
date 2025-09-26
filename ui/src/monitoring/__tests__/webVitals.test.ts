import { afterEach, describe, expect, it, vi } from "vitest";
import { initWebVitals } from "../webVitals";

class MockPerformanceObserver {
  static instances: MockPerformanceObserver[] = [];
  public readonly disconnect = vi.fn();
  private readonly callback: (list: { getEntries: () => any[] }) => void;
  public observedType: string | undefined;

  constructor(cb: (list: { getEntries: () => any[] }) => void) {
    this.callback = cb;
    MockPerformanceObserver.instances.push(this);
  }

  observe(options: { type: string }) {
    this.observedType = options.type;
  }

  emit(entry: any) {
    this.callback({ getEntries: () => [entry] });
  }
}

describe("initWebVitals", () => {
  const originalPerformanceObserver = (globalThis as any).PerformanceObserver;

  afterEach(() => {
    MockPerformanceObserver.instances.length = 0;
    if (originalPerformanceObserver === undefined) {
      delete (globalThis as any).PerformanceObserver;
    } else {
      (globalThis as any).PerformanceObserver = originalPerformanceObserver;
    }
    vi.restoreAllMocks();
  });

  it("reports core metrics and returns cleanup", () => {
    (globalThis as any).PerformanceObserver = MockPerformanceObserver as unknown as typeof PerformanceObserver;
    const navigationEntry = { responseStart: 222 };
    const getEntriesSpy = vi.spyOn(performance, "getEntriesByType");
    getEntriesSpy.mockReturnValue([navigationEntry as PerformanceNavigationTiming]);

    const report = vi.fn();
    const cleanup = initWebVitals(report);

    const observe = (type: string) => MockPerformanceObserver.instances.find((obs) => obs.observedType === type)!;

    observe("largest-contentful-paint").emit({ startTime: 123 });
    const layoutObserver = observe("layout-shift");
    layoutObserver.emit({ hadRecentInput: false, value: 0.05 });
    layoutObserver.emit({ hadRecentInput: true, value: 0.1 });
    observe("first-input").emit({ processingStart: 55, startTime: 10 });
    const paintObserver = observe("paint");
    paintObserver.emit({ name: "first-contentful-paint", startTime: 90 });
    paintObserver.emit({ name: "second-paint", startTime: 120 });

    expect(report).toHaveBeenCalledWith(expect.objectContaining({ name: "TTFB", value: 222 }));
    expect(report).toHaveBeenCalledWith(expect.objectContaining({ name: "LCP", value: 123 }));
    expect(report).toHaveBeenCalledWith(expect.objectContaining({ name: "CLS", value: 0.05 }));
    expect(report).toHaveBeenCalledWith(expect.objectContaining({ name: "FID", value: 45 }));
    expect(report).toHaveBeenCalledWith(expect.objectContaining({ name: "FCP", value: 90 }));
    expect(report).not.toHaveBeenCalledWith(expect.objectContaining({ name: "CLS", value: 0.1 }));

    cleanup();
    for (const observer of MockPerformanceObserver.instances) {
      expect(observer.disconnect).toHaveBeenCalled();
    }
  });

  it("gracefully handles environments without observers", () => {
    delete (globalThis as any).PerformanceObserver;
    const getEntriesSpy = vi.spyOn(performance, "getEntriesByType");
    getEntriesSpy.mockReturnValue([] as PerformanceEntry[]);

    const report = vi.fn();
    const cleanup = initWebVitals(report);

    expect(typeof cleanup).toBe("function");
    expect(report).not.toHaveBeenCalled();
    expect(() => cleanup()).not.toThrow();
  });

  it("ignores observer construction failures", () => {
    (globalThis as any).PerformanceObserver = class {
      constructor() {
        throw new Error("observer unavailable");
      }
    } as unknown as typeof PerformanceObserver;
    const getEntriesSpy = vi.spyOn(performance, "getEntriesByType");
    getEntriesSpy.mockImplementation(() => {
      throw new Error("nav unsupported");
    });

    const report = vi.fn();
    const cleanup = initWebVitals(report);

    expect(report).not.toHaveBeenCalled();
    expect(() => cleanup()).not.toThrow();
  });
});
