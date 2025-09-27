import {act, cleanup, render, screen} from "@testing-library/react";
import {describe, expect, it} from "vitest";
import ZoneEventOverlay from "../components/ZoneEventOverlay";
import {createInitialRealtimeState, SceneRealtimeState} from "../scene/SceneState";
import {buildTooltip} from "@/scene";
import {overlaySnapshots} from "./fixtures/overlaySnapshots";

describe("ZoneEventOverlay snapshot validation", () => {
    const buildRealtimeState = (modifiersByZone: Record<string, string[]>): SceneRealtimeState => {
        const state = createInitialRealtimeState();
        for (const [zoneName, modifiers] of Object.entries(modifiersByZone)) {
            state.zones.set(zoneName, {
                name: zoneName,
                isExplored: true,
                modifiers: new Set(modifiers),
            });
        }
        state.activeZone = Object.keys(modifiersByZone)[0] ?? null;
        return state;
    };

    it("renders hover and focus overlays using sample snapshots", () => {
        for (const snapshot of overlaySnapshots) {
            const realtime = buildRealtimeState(
                Object.fromEntries(snapshot.zones.map((zone) => [zone.name, zone.modifiers]))
            );

            render(<ZoneEventOverlay/>);

            for (const zone of snapshot.zones) {
                const tooltip = buildTooltip(zone.name, realtime);
                act(() => {
                    window.dispatchEvent(
                        new CustomEvent("eternia:zone-hover", {
                            detail: {zone: zone.name, tooltip, modifiers: zone.modifiers},
                        })
                    );
                });

                const hoverLabel = screen.getByText((_, element) => element?.textContent === `Hover: ${zone.name}`);
                expect(hoverLabel).toBeInTheDocument();
                if (tooltip) {
                    const firstLine = tooltip.split("\n")[0];
                    expect(screen.getByText((content) => content.includes(firstLine))).toBeInTheDocument();
                }

                act(() => {
                    window.dispatchEvent(
                        new CustomEvent("eternia:zone-clicked", {
                            detail: {zone: zone.name, tooltip, modifiers: zone.modifiers},
                        })
                    );
                });

                expect(screen.getAllByText(zone.name)[0]).toBeInTheDocument();
                const modifiersText = zone.modifiers.length ? zone.modifiers.join(", ") : "None";
                expect(
                    screen.getAllByText((_, element) => element?.textContent?.includes(modifiersText) ?? false).length
                ).toBeGreaterThan(0);

                // Dismiss focus overlay before testing next zone to keep assertions deterministic
                const dismissButton = screen.getByRole("button", {name: /dismiss zone focus overlay/i});
                act(() => {
                    dismissButton.click();
                });
            }

            cleanup();
        }
    });
});
