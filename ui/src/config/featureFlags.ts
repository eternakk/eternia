import { FeatureFlag, FeatureFlagName } from '../contexts/FeatureFlagContext';

/**
 * Default feature flags configuration
 * 
 * This file defines the initial state of feature flags in the application.
 * Each flag has a name, enabled status, and optional description, rollout percentage, and user groups.
 * 
 * For gradual rollout:
 * - Set enabled to true
 * - Set rolloutPercentage to a value between 0-100
 * 
 * For user group targeting:
 * - Set enabled to true
 * - Add user groups to enabledForGroups array
 */
const featureFlags: Record<FeatureFlagName, FeatureFlag> = {
  // UI quality-of-life flags (repo defaults)
  'ui_skeletons': {
    name: 'ui_skeletons',
    enabled: true,
    description: 'Show skeleton placeholders during async loads',
  },
  'ui_cache': {
    name: 'ui_cache',
    enabled: false,
    description: 'Enable client-side caching layer for GET responses',
  },
  'web_vitals': {
    name: 'web_vitals',
    enabled: false,
    description: 'Collect and report Core Web Vitals metrics',
  },

  // Example of a fully enabled feature
  'advanced-search': {
    name: 'advanced-search',
    enabled: true,
    description: 'Advanced search functionality with filters and sorting',
  },

  // Example of a feature in gradual rollout (50% of users)
  'new-dashboard-layout': {
    name: 'new-dashboard-layout',
    enabled: true,
    description: 'New dashboard layout with improved visualization',
    rolloutPercentage: 50,
  },

  // Example of a feature enabled only for specific user groups
  'admin-analytics': {
    name: 'admin-analytics',
    enabled: true,
    description: 'Advanced analytics for administrators',
    enabledForGroups: ['admin', 'analyst'],
  },

  // Example of a feature in early testing (10% rollout)
  'real-time-collaboration': {
    name: 'real-time-collaboration',
    enabled: true,
    description: 'Real-time collaboration features',
    rolloutPercentage: 10,
  },

  // Example of a disabled feature
  'experimental-ai-suggestions': {
    name: 'experimental-ai-suggestions',
    enabled: false,
    description: 'AI-powered suggestions for rituals and zones',
  },

  // Example of a feature enabled for beta testers
  'beta-features': {
    name: 'beta-features',
    enabled: true,
    description: 'Access to beta features',
    enabledForGroups: ['beta-tester'],
  },

  // Example of a feature with both percentage rollout and group targeting
  'enhanced-visualization': {
    name: 'enhanced-visualization',
    enabled: true,
    description: 'Enhanced visualization for zones and agents',
    rolloutPercentage: 25,
    enabledForGroups: ['premium-user', 'researcher'],
  },
};

export default featureFlags;
