import { describe, expect, it } from 'vitest';
import { SceneHistoryStack } from '@/scene/history/historyStack';
import type { SceneHistoryEntry } from '@/scene';

type EntryInit = Partial<SceneHistoryEntry> & { signature: string };

const buildEntry = (init: EntryInit): SceneHistoryEntry => {
  return {
    timestamp: init.timestamp ?? `2024-01-01T00:00:00.${init.signature}Z`,
    signature: init.signature,
    scene: init.scene ?? {
      activeZone: 'Zone-α',
      camera: {
        position: [1, 2, 3],
        target: [0, 1, 0],
        fov: 45,
        near: 0.1,
        far: 100,
      },
      lighting: {
        ambientIntensity: 0.5,
        exposure: 1,
      },
      render: {
        frameloop: 'demand',
        dpr: [1, 1.5],
      },
    },
    realtime: init.realtime ?? {
      activeZone: 'Zone-α',
      zones: [
        { name: 'Zone-α', isExplored: true, modifiers: ['Calm'] },
      ],
      governor: {
        isPaused: false,
        lastViolation: null,
        lastRollback: null,
      },
    },
    checkpoint: init.checkpoint,
  };
};

describe('SceneHistoryStack', () => {
  it('pushes entries and tracks the current item', () => {
    const stack = new SceneHistoryStack();
    const first = buildEntry({ signature: 'sig-1' });
    const second = buildEntry({ signature: 'sig-2' });

    stack.push(first);
    stack.push(second);

    expect(stack.size()).toBe(2);
    expect(stack.current()).toEqual(second);
    expect(stack.canUndo()).toBe(true);
    expect(stack.canRedo()).toBe(false);
  });

  it('supports undo and redo navigation', () => {
    const stack = new SceneHistoryStack();
    stack.push(buildEntry({ signature: 'sig-1' }));
    stack.push(buildEntry({ signature: 'sig-2' }));
    stack.push(buildEntry({ signature: 'sig-3' }));

    expect(stack.undo()?.signature).toBe('sig-2');
    expect(stack.undo()?.signature).toBe('sig-1');
    expect(stack.undo()?.signature).toBe('sig-1');

    expect(stack.redo()?.signature).toBe('sig-2');
    expect(stack.redo()?.signature).toBe('sig-3');
    expect(stack.redo()?.signature).toBe('sig-3');
  });

  it('replaces the current entry when dedupe is enabled and signatures match', () => {
    const stack = new SceneHistoryStack({ dedupe: true });
    stack.push(buildEntry({ signature: 'sig-1', timestamp: 'T1' }));
    stack.push(buildEntry({ signature: 'sig-1', timestamp: 'T2' }));

    expect(stack.size()).toBe(1);
    expect(stack.current()?.timestamp).toBe('T2');
  });

  it('trims history when exceeding the configured maximum size', () => {
    const stack = new SceneHistoryStack({ maxSize: 2 });
    stack.push(buildEntry({ signature: 'sig-1' }));
    stack.push(buildEntry({ signature: 'sig-2' }));
    stack.push(buildEntry({ signature: 'sig-3' }));

    const entries = stack.toArray();
    expect(entries.map((entry) => entry.signature)).toEqual(['sig-2', 'sig-3']);
    expect(stack.current()?.signature).toBe('sig-3');
    expect(stack.canUndo()).toBe(true);
  });

  it('replaces current entry when requested and pushes when history is empty', () => {
    const stack = new SceneHistoryStack();
    stack.replaceCurrent(buildEntry({ signature: 'sig-1' }));
    expect(stack.size()).toBe(1);

    stack.replaceCurrent(buildEntry({ signature: 'sig-2' }));
    expect(stack.current()?.signature).toBe('sig-2');
  });

  it('clears history and resets navigation state', () => {
    const stack = new SceneHistoryStack();
    stack.push(buildEntry({ signature: 'sig-1' }));
    stack.push(buildEntry({ signature: 'sig-2' }));

    stack.clear();
    expect(stack.size()).toBe(0);
    expect(stack.current()).toBeUndefined();
    expect(stack.canUndo()).toBe(false);
    expect(stack.canRedo()).toBe(false);
  });
});
