import StatePanel from "./components/StatePanel";
import ControlPanel from "./components/ControlPanel";
import LogConsole from "./components/LogConsole";
import CheckpointPanel from "./components/CheckPointPanel.tsx";
import ZoneCanvas from "./components/ZoneCanvas.tsx";
import AgentDashboard from "./components/AgentDashboard";
import ZoneViewer from "./components/ZoneViewer";
import RitualPanel from "./components/RitualPanel";
import NotificationContainer from "./components/NotificationContainer";
import {NotificationProvider} from "./contexts/NotificationContext";
import {AppStateProvider} from "./contexts/AppStateContext";
import {ZoneProvider} from "./contexts/ZoneContext";
import {LoadingProvider} from "./contexts/LoadingContext";
import GlobalLoadingIndicator from "./components/GlobalLoadingIndicator";
import './index.css';

export default function App() {
    return (
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
                                    <ZoneCanvas/>
                                </div>
                                <ZoneViewer/>
                            </ZoneProvider>

                            <div className="md:col-span-3">
                                <LogConsole/>
                            </div>
                            <RitualPanel/>
                        </main>

                        {/* Notification container for displaying error messages and other notifications */}
                        <NotificationContainer/>

                        {/* Global loading indicator */}
                        <GlobalLoadingIndicator/>
                    </div>
                </AppStateProvider>
            </LoadingProvider>
        </NotificationProvider>
    );
}
