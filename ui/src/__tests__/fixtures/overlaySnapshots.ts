export interface OverlaySnapshotZone {
  name: string;
  modifiers: string[];
}

export interface OverlaySnapshot {
  title: string;
  zones: OverlaySnapshotZone[];
}

export const overlaySnapshots: OverlaySnapshot[] = [
  {
    title: "governor_pause",
    zones: [
      {
        name: "Quantum Forest",
        modifiers: ["Luminous Cascade", "Cosmic Awareness"],
      },
      {
        name: "Orikum Sea",
        modifiers: ["Volcanic Surge"],
      },
      {
        name: "Library of Shared Minds",
        modifiers: ["Shroud of Memory"],
      },
    ],
  },
  {
    title: "alignment_healing",
    zones: [
      {
        name: "Quantum Forest",
        modifiers: ["Vibrant Pulse"],
      },
      {
        name: "Orikum Sea",
        modifiers: [],
      },
    ],
  },
];
