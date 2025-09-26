import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SceneRenderer } from "../SceneRenderer";

type CanvasProps = Record<string, unknown> & { children: ReactNode };

const canvasSpy = vi.fn<(props: CanvasProps) => void>();

const mockUseSceneRenderConfig = vi.fn();
const mockUseSceneCamera = vi.fn();
const mockUseSceneLighting = vi.fn();

vi.mock("@react-three/fiber", () => ({
  Canvas: (props: CanvasProps) => {
    canvasSpy(props);
    return <div data-testid="canvas">{props.children}</div>;
  },
}));

vi.mock("../SceneManager", () => ({
  useSceneRenderConfig: () => mockUseSceneRenderConfig(),
  useSceneCamera: () => mockUseSceneCamera(),
  useSceneLighting: () => mockUseSceneLighting(),
}));

describe("SceneRenderer", () => {
  beforeEach(() => {
    canvasSpy.mockClear();
    mockUseSceneRenderConfig.mockReset();
    mockUseSceneCamera.mockReset();
    mockUseSceneLighting.mockReset();
  });

  it("uses scene defaults when overrides are not provided", () => {
    mockUseSceneRenderConfig.mockReturnValue({ frameloop: "demand", dpr: [1, 1.5] });
    mockUseSceneCamera.mockReturnValue({
      position: [2, 4, 6] as [number, number, number],
      target: [0, 1.25, 0] as [number, number, number],
      fov: 40,
      near: 0.1,
      far: 120,
    });
    mockUseSceneLighting.mockReturnValue({ ambientIntensity: 0.5, exposure: 1.2 });

    render(
      <SceneRenderer className="scene-wrapper">
        <span>scene content</span>
      </SceneRenderer>
    );

    expect(canvasSpy).toHaveBeenCalledTimes(1);
    const props = canvasSpy.mock.calls[0][0];
    expect(props.className).toBe("scene-wrapper");
    expect(props.frameloop).toBe("demand");
    expect(props.dpr).toEqual([1, 1.5]);
    expect(props.camera).toEqual({ position: [2, 4, 6], fov: 40, near: 0.1, far: 120 });
    expect(props.gl).toEqual({ antialias: true, toneMappingExposure: 1.2 });
    expect(screen.getByText("scene content")).toBeInTheDocument();
  });

  it("respects overrides for camera and render config", () => {
    const customCamera = {
      position: [1, 1, 1] as [number, number, number],
      fov: 60,
      near: 0.5,
      far: 300,
    };
    mockUseSceneRenderConfig.mockReturnValue({ frameloop: "demand", dpr: [1, 1.5] });
    mockUseSceneCamera.mockReturnValue({
      position: [0, 0, 0],
      target: [0, 1, 0],
      fov: 30,
      near: 0.1,
      far: 100,
    });
    mockUseSceneLighting.mockReturnValue({ ambientIntensity: 0.4, exposure: 0.9 });

    render(
      <SceneRenderer camera={customCamera} frameloop="never" dpr={2} canvasKey="sim">
        <span>override</span>
      </SceneRenderer>
    );

    const props = canvasSpy.mock.calls[0][0];
    expect(props.frameloop).toBe("never");
    expect(props.dpr).toBe(2);
    expect(props.camera).toBe(customCamera);
    expect(props.gl).toEqual({ antialias: true, toneMappingExposure: 0.9 });
  });
});
