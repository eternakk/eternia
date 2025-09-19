import {beforeEach, describe, expect, it, vi} from 'vitest';
import {render, screen} from '@testing-library/react';
import StatePanel from '../components/StatePanel';
import AgentDashboard from '../components/AgentDashboard';

vi.mock('../contexts/FeatureFlagContext', async () => {
    const actual = await vi.importActual<typeof import('../contexts/FeatureFlagContext')>('../contexts/FeatureFlagContext');
    return {
        ...actual,
        useIsFeatureEnabled: () => true,
    };
});

vi.mock('../contexts/WorldStateContext', async () => {
    const mod = await vi.importActual<any>('../contexts/WorldStateContext');
    return {
        ...mod,
        useWorldState: () => ({state: {worldState: undefined, isLoading: true, error: null}}),
    };
});

describe('UI skeletons', () => {
    beforeEach(() => {
        // Ensure a clean slate
        localStorage.clear();
    });

    it('renders skeleton in StatePanel when loading and flag enabled', () => {
        render(<StatePanel/>);
        expect(screen.getByTestId('state-panel-skeleton')).toBeInTheDocument();
    });

    it('renders skeleton in AgentDashboard when loading and flag enabled', () => {
        render(<AgentDashboard/>);
        expect(screen.getByTestId('agent-dashboard-skeleton')).toBeInTheDocument();
    });
});
