import { Suspense, lazy } from 'react';
import StatePanel from "./components/StatePanel";
import ControlPanel from "./components/ControlPanel";
import CheckpointPanel from "./components/CheckPointPanel.tsx";
import AgentDashboard from "./components/AgentDashboard";
import ZoneViewer from "./components/ZoneViewer";
import NotificationContainer from "./components/NotificationContainer";
import {NotificationProvider} from "./contexts/NotificationContext";
import {AppStateProvider} from "./contexts/AppStateContext";
import {ZoneProvider} from "./contexts/ZoneContext";
import {LoadingProvider} from "./contexts/LoadingContext";
import {FeatureFlagProvider} from "./contexts/FeatureFlagContext";
import GlobalLoadingIndicator from "./components/GlobalLoadingIndicator";
import { createLazyComponent } from "./components/LazyLoad";
import featureFlags from "./config/featureFlags";
import './index.css';

// Lazy load components that are not immediately visible or are large
const LazyLogConsole = createLazyComponent(() => import("./components/LogConsole"));
const LazyRitualPanel = createLazyComponent(() => import("./components/RitualPanel"));
const LazyZoneCanvas = createLazyComponent(() => import("./components/ZoneCanvas.tsx"));

export default function App() {
    return (
        <FeatureFlagProvider initialFlags={featureFlags}>
            <NotificationProvider>
                <LoadingProvider>
                    <AppStateProvider refreshInterval={3000}>
                        <div className="min-h-screen bg-slate-100 flex flex-col">
                            <header className="p-4 bg-slate-900 text-white text-lg font-bold">
                                Eterna Mission‑Control
                            </header>

                            <main className="flex-1 grid gap-4 p-6 md:grid-cols-3">
                                <StatePanel/>
                                <AgentDashboard/>
                                <ControlPanel/>
                                <CheckpointPanel/>

                                <ZoneProvider>
                                    <div className="md:col-span-3">
                                        <LazyZoneCanvas />
                                    </div>
                                    <ZoneViewer/>
                                </ZoneProvider>

                                <div className="md:col-span-3">
                                    <LazyLogConsole />
                                </div>
                                <LazyRitualPanel />
                            </main>

                            {/* Notification container for displaying error messages and other notifications */}
                            <NotificationContainer/>

                            {/* Global loading indicator */}
                            <GlobalLoadingIndicator/>
                        </div>
                    </AppStateProvider>
                </LoadingProvider>
            </NotificationProvider>
        </FeatureFlagProvider>
    );
}
