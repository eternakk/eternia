import { sendCommand } from "../api";

const actions = ["pause", "resume", "rollback", "shutdown"] as const;

export default function ControlPanel() {
  return (
    <div className="p-4 border rounded-xl shadow bg-white">
      <h2 className="font-semibold mb-2">Controls</h2>
      <div className="flex gap-3 flex-wrap">
        {actions.map((a) => (
          <button
            key={a}
            onClick={() => sendCommand(a)}
            className="px-3 py-1 rounded bg-slate-800 text-white text-sm hover:bg-slate-700"
          >
            {a.toUpperCase()}
          </button>
        ))}
      </div>
    </div>
  );
}