import useSWR from "swr";
import { getCheckpoints, rollbackTo } from "../api";
import { useState } from "react";

export default function CheckpointPanel() {
  const { data: files, mutate } = useSWR("ckpts", getCheckpoints, {
    refreshInterval: 5000,
  });
  const [sel, setSel] = useState<string | undefined>();

  if (!files) return null;

  return (
    <div className="p-4 border rounded-xl shadow bg-white">
      <h2 className="font-semibold mb-2">Checkpoints</h2>
      <select
        value={sel ?? ""}
        onChange={(e) => setSel(e.target.value || undefined)}
        className="border px-2 py-1 text-sm w-full"
      >
        <option value="">latest</option>
        {files.map((f) => (
          <option key={f} value={f}>
            {f.split("/").pop()}
          </option>
        ))}
      </select>
      <button
        onClick={async () => {
          await rollbackTo(sel);
          await mutate();                 // refresh list
        }}
        className="mt-2 w-full bg-indigo-600 text-white text-sm py-1 rounded"
      >
        Roll back
      </button>
    </div>
  );
}