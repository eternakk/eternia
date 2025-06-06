import useSWR from "swr";
import { getCheckpoints, rollbackTo } from "../api";
import { useState, useEffect, useRef } from "react";

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

export default function CheckpointPanel() {
  const [isPageVisible, setIsPageVisible] = useState(true);

  // Last request time reference for debouncing
  const lastRequestTimeRef = useRef<number>(0);
  const minRequestInterval = 2000; // Minimum 2 seconds between requests

  // Set up visibility change detection
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsPageVisible(document.visibilityState === 'visible');
    };

    // Set initial visibility state
    handleVisibilityChange();

    // Add event listener for visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Clean up event listener
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  // Custom fetcher with debouncing
  const debouncedFetcher = async (...args: Parameters<typeof getCheckpoints>) => {
    const now = Date.now();

    // Debounce requests
    if (now - lastRequestTimeRef.current < minRequestInterval) {
      // If we're debouncing, return the cached data if available
      const cachedData = localStorage.getItem('checkpoints_cache');
      if (cachedData) {
        const cache = JSON.parse(cachedData);
        if (now - cache.timestamp < CACHE_DURATION) {
          return cache.data;
        }
      }

      // If no cache or expired, wait for the minimum interval
      await new Promise(resolve => setTimeout(resolve, minRequestInterval));
    }

    lastRequestTimeRef.current = Date.now();

    // Make the actual request
    const data = await getCheckpoints(...args);

    // Cache the result
    localStorage.setItem('checkpoints_cache', JSON.stringify({
      data,
      timestamp: Date.now()
    }));

    return data;
  };

  const { data: files, mutate } = useSWR("ckpts", debouncedFetcher, {
    // Pause polling when page is not visible
    refreshWhenHidden: false,
    // Don't revalidate when window is focused if page is not visible
    revalidateOnFocus: isPageVisible,
    // Only poll when page is visible
    refreshWhenOffline: false,
    // Disable polling completely when page is not visible
    refreshInterval: isPageVisible ? 10000 : 0,
    // Add caching
    dedupingInterval: 5000, // Dedupe requests within 5 seconds
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
        {files.map((f: string, index: number) => (
          <option key={`${f}-${index}`} value={f}>
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
