import StatePanel from "./components/StatePanel";
import ControlPanel from "./components/ControlPanel";
import CheckpointPanel from "./components/CheckPointPanel.tsx";
import AgentDashboard from "./components/AgentDashboard";
import ZoneViewer from "./components/ZoneViewer";
import NotificationContainer from "./components/NotificationContainer";
import {NotificationProvider} from "./contexts/NotificationContext";
import {LoadingProvider} from "./contexts/LoadingContext";
import {FeatureFlagProvider} from "./contexts/FeatureFlagContext";
import {WorldStateProvider} from "./contexts/WorldStateContext";
import GlobalLoadingIndicator from "./components/GlobalLoadingIndicator";
import {createLazyComponent} from "./components/LazyLoad";
import featureFlags from "./config/featureFlags";
import './index.css';
import RitualPanel from "./components/RitualPanel";
import WebVitalsReporter from './components/WebVitalsReporter';
import SecurityPanel from "./components/SecurityPanel";
import ZoneEventOverlay from "./components/ZoneEventOverlay";
import {SceneManagerProvider} from "./scene";

// Lazy load components that are not immediately visible or are large
const LazyLogConsole = createLazyComponent(() => import("./components/LogConsole"));
const LazyZoneCanvas = createLazyComponent(() => import("./components/ZoneCanvas.tsx"));
const LazyMiniVirtualWorld = createLazyComponent(() => import("./components/MiniVirtualWorld"));

export default function App() {
    return (
        <FeatureFlagProvider initialFlags={featureFlags}>
            <NotificationProvider>
                <LoadingProvider>
                    <SceneManagerProvider>
                        <WorldStateProvider refreshInterval={3000}>
                            <div className="min-h-screen bg-slate-100 flex flex-col">
                            <header className="p-4 bg-slate-900 text-white text-lg font-bold">
                                Eterna Mission‑Control
                            </header>

                            <main className="flex-1 grid gap-4 p-6 md:grid-cols-3">
                                <StatePanel/>
                                <AgentDashboard/>
                                <ControlPanel/>
                                <CheckpointPanel/>
                                <SecurityPanel/>

                                <div className="md:col-span-3">
                                    <LazyZoneCanvas/>
                                </div>

                                <div className="md:col-span-3">
                                    <LazyMiniVirtualWorld/>
                                </div>
                                <ZoneViewer/>

                                <div className="md:col-span-3">
                                    <LazyLogConsole/>
                                </div>
                                <RitualPanel/>
                            </main>

                            {/* Notification container for displaying error messages and other notifications */}
                            <NotificationContainer/>

                            {/* Global loading indicator */}
                            <GlobalLoadingIndicator/>
                            <ZoneEventOverlay />
                        </div>
                        {/* Feature-flagged Core Web Vitals reporter (no UI) */}
                        <WebVitalsReporter />
                        </WorldStateProvider>
                    </SceneManagerProvider>
                </LoadingProvider>
            </NotificationProvider>
        </FeatureFlagProvider>
    );
}
