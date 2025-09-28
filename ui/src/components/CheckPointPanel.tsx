import useSWR from "swr";
import { getCheckpoints, rollbackTo, type CheckpointRecord, normalizeCheckpointRecords } from "../api";
import { useState, useEffect, useRef, useMemo } from "react";
import { PanelSkeleton } from './ui/Skeleton';
import { useIsFeatureEnabled } from '../contexts/FeatureFlagContext';

// Cache duration in milliseconds (5 minutes)
const CACHE_DURATION = 5 * 60 * 1000;

const SAFE_FILENAME_RE = /^[A-Za-z0-9._-]+$/;

const toFilename = (value?: string | null) => {
  if (!value) return undefined;
  const parts = value.split(/[/\\]/);
  return parts[parts.length - 1] || value;
};

const deriveSafeParam = (
  record: CheckpointRecord,
): string | undefined => {
  const candidateOrder = [record.target_path, record.path, record.label];
  for (const candidate of candidateOrder) {
    const file = toFilename(typeof candidate === "string" ? candidate : undefined);
    if (file && SAFE_FILENAME_RE.test(file)) {
      return file;
    }
  }
  return undefined;
};

const formatBytes = (sizeBytes: number | null | undefined) => {
  if (!Number.isFinite(sizeBytes ?? NaN) || (sizeBytes ?? 0) <= 0) {
    return "-";
  }
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = sizeBytes ?? 0;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  return `${size.toFixed(size >= 100 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
};

const formatTimestamp = (timestamp: Date | null) => {
  if (!timestamp) return "-";
  return timestamp.toLocaleString();
};

const parseCheckpointInfo = (record: CheckpointRecord) => {
  const timestamp = new Date(record.created_at);
  const isValidDate = !Number.isNaN(timestamp.getTime());
  const targetPath = record.target_path ?? record.path;
  const safeParam = deriveSafeParam(record);
  const baseName = record.label || toFilename(targetPath) || record.path;

  return {
    record,
    displayName: baseName,
    timestamp: isValidDate ? timestamp : null,
    continuityScore: typeof record.continuity === "number" ? record.continuity : null,
    sizeLabel: formatBytes(typeof record.size_bytes === "number" ? record.size_bytes : null),
    stateVersion: typeof record.state_version === "number" ? record.state_version : null,
    sortKey: isValidDate ? timestamp.getTime() : record.path,
    kind: record.kind,
    targetPath,
    safeParam,
  };
};

export default function CheckpointPanel() {
  const enableSkeletons = useIsFeatureEnabled('ui_skeletons');
  const [isPageVisible, setIsPageVisible] = useState(true);
  const [selectedCheckpoint, setSelectedCheckpoint] = useState<string | undefined>(undefined);
  const [isRestoring, setIsRestoring] = useState(false);

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
          return normalizeCheckpointRecords(cache.data);
        }
      }

      // If no cache or expired, wait for the minimum interval
      await new Promise(resolve => setTimeout(resolve, minRequestInterval));
    }

    lastRequestTimeRef.current = Date.now();

    // Make the actual request
    const data = await getCheckpoints(...args);
    const normalized = normalizeCheckpointRecords(data);

    // Cache the result
    localStorage.setItem('checkpoints_cache', JSON.stringify({
      data: normalized,
      timestamp: Date.now()
    }));

    return normalized;
  };

  const { data: checkpointRecords, mutate } = useSWR("ckpts", debouncedFetcher, {
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

  // Handle restore action
  const handleRestore = async () => {
    if (isRestoring) return;

    setIsRestoring(true);
    try {
      await rollbackTo(selectedCheckpoint);
      await mutate(); // refresh list
    } finally {
      setIsRestoring(false);
    }
  };

  if (!checkpointRecords) {
    if (enableSkeletons) {
      return <PanelSkeleton title="Checkpoints" data-testid="checkpoint-panel-skeleton" />;
    }
    return <div className="p-4 border rounded-xl shadow bg-white">Loading checkpoints...</div>;
  }

  // Define the type for checkpoint info
  type CheckpointInfo = ReturnType<typeof parseCheckpointInfo>;

  const checkpoints = useMemo(() => {
    return checkpointRecords
      .map(parseCheckpointInfo)
      .sort((a: CheckpointInfo, b: CheckpointInfo) => {
        if (typeof a.sortKey === 'number' && typeof b.sortKey === 'number') {
          return b.sortKey - a.sortKey;
        }
        return String(b.sortKey).localeCompare(String(a.sortKey));
      });
  }, [checkpointRecords]);

  const getKindBadgeClass = (kind: CheckpointInfo['kind']) => {
    switch (kind) {
      case 'manual':
        return 'bg-purple-100 text-purple-800';
      case 'rollback':
        return 'bg-yellow-100 text-yellow-800';
      case 'auto':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const latestSelected = selectedCheckpoint === undefined;

  return (
    <div className="p-4 border rounded-xl shadow bg-white">
      <h2 className="font-semibold mb-2">Checkpoints</h2>

      <div className="mb-4 max-h-60 overflow-y-auto border rounded">
        <div className="sticky top-0 bg-gray-100 p-2 grid grid-cols-12 gap-2 text-xs font-semibold border-b">
          <div className="col-span-7">Checkpoint</div>
          <div className="col-span-2">Kind</div>
          <div className="col-span-2">Continuity</div>
          <div className="col-span-1">Action</div>
        </div>

        {checkpoints.length === 0 ? (
          <div className="p-4 text-center text-gray-500">No checkpoints available</div>
        ) : (
          <div className="divide-y">
            {/* Latest checkpoint option */}
            <div 
              className={`p-2 grid grid-cols-12 gap-2 items-center hover:bg-blue-50 cursor-pointer ${latestSelected ? 'bg-blue-100' : ''}`}
              onClick={() => setSelectedCheckpoint(undefined)}
            >
              <div className="col-span-7 text-sm font-medium">
                Latest (Current State)
                <div className="text-xs text-gray-500">Restore to the most recent state</div>
              </div>
              <div className="col-span-2">-</div>
              <div className="col-span-2">-</div>
              <div className="col-span-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedCheckpoint(undefined);
                  }}
                  className="text-xs px-2 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
                  aria-label="Select latest checkpoint"
                >
                  Select
                </button>
              </div>
            </div>

            {/* List of checkpoints */}
            {checkpoints.map((checkpoint: CheckpointInfo, index: number) => (
              <div 
                key={`${checkpoint.record.path}-${index}`}
                className={`p-2 grid grid-cols-12 gap-2 items-center ${checkpoint.safeParam ? 'hover:bg-blue-50 cursor-pointer' : 'opacity-60 cursor-not-allowed'} ${selectedCheckpoint && checkpoint.safeParam === selectedCheckpoint ? 'bg-blue-100' : ''}`}
                onClick={() => {
                  if (!checkpoint.safeParam) return;
                  setSelectedCheckpoint(checkpoint.safeParam);
                }}
              >
                <div className="col-span-7 text-sm">
                  <div className="font-medium">
                    {checkpoint.displayName}
                    {checkpoint.stateVersion !== null && (
                      <span className="ml-2 text-xs text-gray-500">v{checkpoint.stateVersion}</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatTimestamp(checkpoint.timestamp)}
                  </div>
                  <div className="text-xs text-gray-500 truncate" title={checkpoint.targetPath}>
                    {checkpoint.targetPath}
                  </div>
                  <div className="text-xs text-gray-500">Size: {checkpoint.sizeLabel}</div>
                </div>
                <div className="col-span-2">
                  <span className={`px-2 py-1 rounded-full text-xs ${getKindBadgeClass(checkpoint.kind)}`}>
                    {checkpoint.kind}
                  </span>
                </div>
                <div className="col-span-2">
                  {checkpoint.continuityScore !== null 
                    ? <span className="px-2 py-0.5 bg-green-100 rounded-full text-xs">{checkpoint.continuityScore.toFixed(3)}</span>
                    : '-'}
                </div>
                <div className="col-span-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (!checkpoint.safeParam) return;
                      setSelectedCheckpoint(checkpoint.safeParam);
                    }}
                    className={`text-xs px-2 py-1 rounded ${checkpoint.safeParam ? 'bg-blue-500 text-white hover:bg-blue-600' : 'bg-gray-300 text-gray-600 cursor-not-allowed'}`}
                    aria-label={`Select checkpoint ${checkpoint.displayName}`}
                    disabled={!checkpoint.safeParam}
                  >
                    Select
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={handleRestore}
        disabled={isRestoring}
        className={`w-full py-2 rounded font-medium flex items-center justify-center ${
          isRestoring 
            ? 'bg-gray-400 cursor-not-allowed text-white' 
            : 'bg-indigo-600 text-white hover:bg-indigo-700'
        }`}
        aria-busy={isRestoring}
      >
        {isRestoring ? (
          <>
            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Restoring...
          </>
        ) : (
          <>Restore Checkpoint</>
        )}
      </button>
    </div>
  );
}
