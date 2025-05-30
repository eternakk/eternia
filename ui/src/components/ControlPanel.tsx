import {sendCommand, rollbackTo} from "../api";
import axios from "axios";

const actions = ["pause", "resume", "shutdown"] as const;
const TOKEN = import.meta.env.VITE_ETERNA_TOKEN;
const api = axios.create({
    baseURL: "http://localhost:8000",
    headers: { Authorization: `Bearer ${TOKEN}` },
});

export default function ControlPanel() {
    // Default companion name or get it from somewhere else if needed
    const companionName = "default";

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
                <button
                    onClick={() => rollbackTo()}
                    className="px-3 py-1 rounded bg-slate-800 text-white text-sm hover:bg-slate-700"
                >
                    ROLLBACK
                </button>
            </div>
            <button
                onClick={() => api.post(`/reward/${companionName}`, {value: 1})}
                className="px-2 py-1 bg-green-600 text-white"
            >
                👍
            </button>
            <button
                onClick={() => api.post(`/reward/${companionName}`, {value: -1})}
                className="px-2 py-1 bg-red-600 text-white"
            >
                👎
            </button>

        </div>
    );
}
