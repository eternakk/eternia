import type {SceneHistoryEntry} from "@/scene";

export interface HistoryStackOptions {
    maxSize?: number;
    dedupe?: boolean;
}

export class SceneHistoryStack {
    private readonly maxSize: number;
    private readonly dedupe: boolean;
    private entries: SceneHistoryEntry[] = [];
    private pointer = -1;

    constructor(options: HistoryStackOptions = {}) {
        this.maxSize = Math.max(1, options.maxSize ?? 50);
        this.dedupe = options.dedupe ?? true;
    }

    push(entry: SceneHistoryEntry): void {
        if (this.dedupe && this.entries[this.pointer]?.signature === entry.signature) {
            this.entries[this.pointer] = entry;
            return;
        }

        if (this.pointer < this.entries.length - 1) {
            this.entries = this.entries.slice(0, this.pointer + 1);
        }

        this.entries.push(entry);
        if (this.entries.length > this.maxSize) {
            const overflow = this.entries.length - this.maxSize;
            this.entries = this.entries.slice(overflow);
            this.pointer = this.entries.length - 1;
        } else {
            this.pointer = this.entries.length - 1;
        }
    }

    current(): SceneHistoryEntry | undefined {
        if (this.pointer < 0) return undefined;
        return this.entries[this.pointer];
    }

    canUndo(): boolean {
        return this.pointer > 0;
    }

    canRedo(): boolean {
        return this.pointer < this.entries.length - 1;
    }

    undo(): SceneHistoryEntry | undefined {
        if (!this.canUndo()) return this.current();
        this.pointer -= 1;
        return this.current();
    }

    redo(): SceneHistoryEntry | undefined {
        if (!this.canRedo()) return this.current();
        this.pointer += 1;
        return this.current();
    }

    replaceCurrent(entry: SceneHistoryEntry): void {
        if (this.pointer < 0) {
            this.push(entry);
            return;
        }
        this.entries[this.pointer] = entry;
    }

    clear(): void {
        this.entries = [];
        this.pointer = -1;
    }

    size(): number {
        return this.entries.length;
    }

    toArray(): SceneHistoryEntry[] {
        return [...this.entries];
    }
}
