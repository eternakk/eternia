import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

/**
 * Union type of all feature flag names
 * This ensures type safety when referencing feature flags
 */
export type FeatureFlagName = 
  | 'advanced-search'
  | 'new-dashboard-layout'
  | 'admin-analytics'
  | 'real-time-collaboration'
  | 'experimental-ai-suggestions'
  | 'beta-features'
  | 'enhanced-visualization';

// Define the shape of a feature flag
export interface FeatureFlag {
  name: FeatureFlagName;
  enabled: boolean;
  description?: string;
  // Optional percentage for gradual rollout (0-100)
  rolloutPercentage?: number;
  // Optional user groups that have this feature enabled
  enabledForGroups?: string[];
}

// Define the shape of the context
interface FeatureFlagContextType {
  // All available feature flags
  flags: Record<FeatureFlagName, FeatureFlag>;
  // Check if a feature is enabled
  isFeatureEnabled: (featureName: FeatureFlagName, userId?: string, userGroups?: string[]) => boolean;
  // Update a feature flag (for admin purposes)
  updateFeatureFlag: (name: FeatureFlagName, updates: Partial<FeatureFlag>) => void;
}

// Create the context with a default value
const FeatureFlagContext = createContext<FeatureFlagContextType>({
  flags: {},
  isFeatureEnabled: () => false,
  updateFeatureFlag: () => {},
});

// Props for the provider component
interface FeatureFlagProviderProps {
  children: ReactNode;
  // Initial flags can be provided as a prop
  initialFlags?: Record<string, FeatureFlag>;
  // URL to fetch flags from
  flagsUrl?: string;
}

export const FeatureFlagProvider: React.FC<FeatureFlagProviderProps> = ({
  children,
  initialFlags = {},
  flagsUrl,
}) => {
  const [flags, setFlags] = useState<Record<string, FeatureFlag>>(initialFlags);

  // Fetch flags from the server if a URL is provided
  useEffect(() => {
    if (flagsUrl) {
      const fetchFlags = async () => {
        try {
          const response = await fetch(flagsUrl);
          if (!response.ok) {
            throw new Error(`Failed to fetch feature flags: ${response.statusText}`);
          }
          const data = await response.json();
          setFlags(data);
        } catch (error) {
          console.error('Error fetching feature flags:', error);
          // Fall back to initial flags if fetch fails
        }
      };

      fetchFlags();
    }
  }, [flagsUrl]);

  // Check if a feature is enabled for a specific user
  const isFeatureEnabled = (featureName: FeatureFlagName, userId?: string, userGroups: string[] = []): boolean => {
    const flag = flags[featureName];

    // If the flag doesn't exist or is explicitly disabled, return false
    if (!flag || !flag.enabled) {
      return false;
    }

    // If the flag is enabled with no additional conditions, return true
    if (flag.enabled && !flag.rolloutPercentage && (!flag.enabledForGroups || flag.enabledForGroups.length === 0)) {
      return true;
    }

    // Check if the user is in an enabled group
    if (flag.enabledForGroups && flag.enabledForGroups.length > 0) {
      if (userGroups.some(group => flag.enabledForGroups?.includes(group))) {
        return true;
      }
    }

    // Check rollout percentage if specified
    if (flag.rolloutPercentage !== undefined && userId) {
      // Use a deterministic hash of the feature name and user ID to determine if the user gets the feature
      // This ensures the same user always gets the same result for a given feature
      const hash = hashString(`${featureName}-${userId}`);
      const normalizedHash = (hash % 100) + 100; // Ensure positive value between 0-99
      return normalizedHash % 100 < flag.rolloutPercentage;
    }

    // Default to the flag's enabled state
    return flag.enabled;
  };

  // Update a feature flag
  const updateFeatureFlag = (name: FeatureFlagName, updates: Partial<FeatureFlag>) => {
    setFlags(prevFlags => ({
      ...prevFlags,
      [name]: {
        ...prevFlags[name],
        ...updates,
      },
    }));
  };

  // Simple string hashing function for deterministic rollout
  const hashString = (str: string): number => {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  };

  return (
    <FeatureFlagContext.Provider value={{ flags, isFeatureEnabled, updateFeatureFlag }}>
      {children}
    </FeatureFlagContext.Provider>
  );
};

// Custom hook for using the feature flags
export const useFeatureFlag = () => {
  const context = useContext(FeatureFlagContext);
  if (context === undefined) {
    throw new Error('useFeatureFlag must be used within a FeatureFlagProvider');
  }
  return context;
};

// Convenience hook to check if a specific feature is enabled
export const useIsFeatureEnabled = (featureName: FeatureFlagName, userId?: string, userGroups?: string[]) => {
  const { isFeatureEnabled } = useFeatureFlag();
  return isFeatureEnabled(featureName, userId, userGroups);
};

// Component to conditionally render based on feature flag
interface FeatureFlaggedProps {
  feature: FeatureFlagName;
  userId?: string;
  userGroups?: string[];
  children: ReactNode;
  fallback?: ReactNode;
}

export const FeatureFlagged: React.FC<FeatureFlaggedProps> = ({
  feature,
  userId,
  userGroups,
  children,
  fallback = null,
}) => {
  const { isFeatureEnabled } = useFeatureFlag();
  return isFeatureEnabled(feature, userId, userGroups) ? <>{children}</> : <>{fallback}</>;
};

export default FeatureFlagContext;
