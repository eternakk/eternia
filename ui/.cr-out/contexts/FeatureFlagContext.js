import { jsx as _jsx, Fragment as _Fragment } from "react/jsx-runtime";
import { createContext, useContext, useEffect, useState } from 'react';
// Create the context with a default value
const defaultFlags = {
    'advanced-search': { name: 'advanced-search', enabled: false },
    'new-dashboard-layout': { name: 'new-dashboard-layout', enabled: false },
    'admin-analytics': { name: 'admin-analytics', enabled: false },
    'real-time-collaboration': { name: 'real-time-collaboration', enabled: false },
    'experimental-ai-suggestions': { name: 'experimental-ai-suggestions', enabled: false },
    'beta-features': { name: 'beta-features', enabled: false },
    'enhanced-visualization': { name: 'enhanced-visualization', enabled: false },
};
const FeatureFlagContext = createContext({
    flags: defaultFlags,
    isFeatureEnabled: () => false,
    updateFeatureFlag: () => {
    },
});
export const FeatureFlagProvider = ({ children, initialFlags = {}, flagsUrl, }) => {
    const [flags, setFlags] = useState(initialFlags);
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
                }
                catch (error) {
                    console.error('Error fetching feature flags:', error);
                    // Fall back to initial flags if fetch fails
                }
            };
            fetchFlags();
        }
    }, [flagsUrl]);
    // Check if a feature is enabled for a specific user
    const isFeatureEnabled = (featureName, userId, userGroups = []) => {
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
    const updateFeatureFlag = (name, updates) => {
        setFlags(prevFlags => {
            const updatedFlags = {
                ...prevFlags,
                [name]: {
                    ...prevFlags[name],
                    ...updates,
                    name, // Ensure name is set correctly
                },
            };
            return updatedFlags;
        });
    };
    // Simple string hashing function for deterministic rollout
    const hashString = (str) => {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash);
    };
    return (_jsx(FeatureFlagContext.Provider, { value: { flags, isFeatureEnabled, updateFeatureFlag }, children: children }));
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
export const useIsFeatureEnabled = (featureName, userId, userGroups) => {
    const { isFeatureEnabled } = useFeatureFlag();
    return isFeatureEnabled(featureName, userId, userGroups);
};
export const FeatureFlagged = ({ feature, userId, userGroups, children, fallback = null, }) => {
    const { isFeatureEnabled } = useFeatureFlag();
    return isFeatureEnabled(feature, userId, userGroups) ? _jsx(_Fragment, { children: children }) : _jsx(_Fragment, { children: fallback });
};
export default FeatureFlagContext;
