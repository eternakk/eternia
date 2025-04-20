import StatePanel from "./components/StatePanel";
import ControlPanel from "./components/ControlPanel";
import LogConsole from "./components/LogConsole";
import CheckpointPanel from "./components/CheckPointPanel.tsx";
import ZoneCanvas from "./components/ZoneCanvas.tsx";
import './index.css';

export default function App() {
  return (
    <div className="min-h-screen bg-slate-100 flex flex-col">
      <header className="p-4 bg-slate-900 text-white text-lg font-bold">
        Eterna Mission‑Control
      </header>

      <main className="flex-1 grid gap-4 p-6 md:grid-cols-3">
        <StatePanel />
        <ControlPanel />
        <CheckpointPanel />

        <div className="md:col-span-3">
          <ZoneCanvas />
        </div>

        <div className="md:col-span-3">
          <LogConsole />
        </div>
      </main>
    </div>
  );
}