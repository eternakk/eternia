import { act, render, screen, waitFor } from "@testing-library/react";
import ZoneEventOverlay from "../components/ZoneEventOverlay";

const hoverEvent = (zone: string, tooltip?: string | null, modifiers: string[] = []) =>
  new CustomEvent("eternia:zone-hover", { detail: { zone, tooltip, modifiers } });

const clickEvent = (zone: string, modifiers: string[] = [], tooltip?: string | null) =>
  new CustomEvent("eternia:zone-clicked", { detail: { zone, modifiers, tooltip } });

describe("ZoneEventOverlay", () => {
  it("shows hover tooltip and clears on exit", async () => {
    render(<ZoneEventOverlay />);

    await act(async () => {
      window.dispatchEvent(hoverEvent("Quantum Forest", "Entangled canopy"));
    });

    expect(await screen.findByText(/Hover: Quantum Forest/)).toBeInTheDocument();
    expect(screen.getByText(/Entangled canopy/)).toBeInTheDocument();

    await act(async () => {
      window.dispatchEvent(hoverEvent("Quantum Forest", null));
    });

    await waitFor(() => {
      expect(screen.queryByText(/Hover:/)).not.toBeInTheDocument();
    });
  });

  it("shows focus card on click and can dismiss", async () => {
    render(<ZoneEventOverlay />);

    act(() => {
      window.dispatchEvent(clickEvent("Orikum Sea", ["Tidal Flux"], "Shifting tides"));
    });

    expect(screen.getByText("Orikum Sea")).toBeInTheDocument();
    expect(screen.getByText(/Tidal Flux/)).toBeInTheDocument();

    const dismiss = screen.getByRole("button", { name: /dismiss zone focus overlay/i });
    act(() => {
      dismiss.click();
    });

    await waitFor(() => {
      expect(screen.queryByText("Orikum Sea")).not.toBeInTheDocument();
    });
  });
});
