import { useGovEvents } from "../hooks/useGovEvents";

export default function LogConsole() {
  const log = useGovEvents();

  return (
    <div className="p-4 border rounded-xl shadow bg-black text-green-300 text-xs h-60 overflow-y-auto">
      {log.map((e, i) => (
        <div key={i}>
          [{new Date(e.t * 1000).toLocaleTimeString()}] {e.event}
          {e.payload ? " → " + JSON.stringify(e.payload) : ""}
        </div>
      ))}
    </div>
  );
}