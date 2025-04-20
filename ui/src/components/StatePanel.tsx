import useSWR from "swr";
import { getState } from "../api";

export default function StatePanel() {
  const { data } = useSWR("state", getState, { refreshInterval: 1000 });

  if (!data) return <div>Loading state…</div>;

  return (
    <div className="p-4 border rounded-xl shadow bg-white">
      <h2 className="font-semibold mb-2">World State</h2>
      <ul className="space-y-1 text-sm">
        <li>Cycle: {data.cycle}</li>
        <li>Identity Score: {data.identity_score.toFixed(3)}</li>
        <li>Emotion: {data.emotion ?? "–"}</li>
        <li>Modifiers: {Object.keys(data.modifiers).length}</li>
      </ul>
    </div>
  );
}