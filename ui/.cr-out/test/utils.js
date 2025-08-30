"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.render = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("@testing-library/react");
const NotificationContext_1 = require("../contexts/NotificationContext");
const LoadingContext_1 = require("../contexts/LoadingContext");
const AppStateContext_1 = require("../contexts/AppStateContext");
const ZoneContext_1 = require("../contexts/ZoneContext");
// Create a custom render function that includes all providers
const AllProviders = ({ children }) => {
    return ((0, jsx_runtime_1.jsx)(NotificationContext_1.NotificationProvider, { children: (0, jsx_runtime_1.jsx)(LoadingContext_1.LoadingProvider, { children: (0, jsx_runtime_1.jsx)(AppStateContext_1.AppStateProvider, { refreshInterval: 1000, children: (0, jsx_runtime_1.jsx)(ZoneContext_1.ZoneProvider, { children: children }) }) }) }));
};
// Custom render function that wraps the component with all providers
const customRender = (ui, options) => (0, react_1.render)(ui, { wrapper: AllProviders, ...options });
exports.render = customRender;
// Re-export everything from testing-library
__exportStar(require("@testing-library/react"), exports);
