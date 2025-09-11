import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import StatePanel from "./components/StatePanel";
import ControlPanel from "./components/ControlPanel";
import CheckpointPanel from "./components/CheckPointPanel.tsx";
import AgentDashboard from "./components/AgentDashboard";
import ZoneViewer from "./components/ZoneViewer";
import NotificationContainer from "./components/NotificationContainer";
import { NotificationProvider } from "./contexts/NotificationContext";
import { LoadingProvider } from "./contexts/LoadingContext";
import { FeatureFlagProvider } from "./contexts/FeatureFlagContext";
import { WorldStateProvider } from "./contexts/WorldStateContext";
import GlobalLoadingIndicator from "./components/GlobalLoadingIndicator";
import { createLazyComponent } from "./components/LazyLoad";
import featureFlags from "./config/featureFlags";
import './index.css';
// Lazy load components that are not immediately visible or are large
const LazyLogConsole = createLazyComponent(() => import("./components/LogConsole"));
const LazyRitualPanel = createLazyComponent(() => import("./components/RitualPanel"));
const LazyZoneCanvas = createLazyComponent(() => import("./components/ZoneCanvas.tsx"));
export default function App() {
    return (_jsx(FeatureFlagProvider, { initialFlags: featureFlags, children: _jsx(NotificationProvider, { children: _jsx(LoadingProvider, { children: _jsx(WorldStateProvider, { refreshInterval: 3000, children: _jsxs("div", { className: "min-h-screen bg-slate-100 flex flex-col", children: [_jsx("header", { className: "p-4 bg-slate-900 text-white text-lg font-bold", children: "Eterna Mission\u2011Control" }), _jsxs("main", { className: "flex-1 grid gap-4 p-6 md:grid-cols-3", children: [_jsx(StatePanel, {}), _jsx(AgentDashboard, {}), _jsx(ControlPanel, {}), _jsx(CheckpointPanel, {}), _jsx("div", { className: "md:col-span-3", children: _jsx(LazyZoneCanvas, {}) }), _jsx(ZoneViewer, {}), _jsx("div", { className: "md:col-span-3", children: _jsx(LazyLogConsole, {}) }), _jsx(LazyRitualPanel, {})] }), _jsx(NotificationContainer, {}), _jsx(GlobalLoadingIndicator, {})] }) }) }) }) }));
}
