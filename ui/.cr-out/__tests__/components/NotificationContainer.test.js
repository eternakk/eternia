"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const vitest_1 = require("vitest");
const utils_1 = require("../../test/utils");
const NotificationContainer_1 = __importDefault(require("../../components/NotificationContainer"));
const NotificationContext_1 = require("../../contexts/NotificationContext");
// Mock the useNotification hook
vitest_1.vi.mock('../../contexts/NotificationContext', async () => {
    const actual = await vitest_1.vi.importActual('../../contexts/NotificationContext');
    return {
        ...actual,
        useNotification: vitest_1.vi.fn(),
    };
});
(0, vitest_1.describe)('NotificationContainer', () => {
    (0, vitest_1.beforeEach)(() => {
        vitest_1.vi.resetAllMocks();
    });
    (0, vitest_1.it)('renders nothing when there are no notifications', () => {
        // Mock the useNotification hook to return empty notifications
        vitest_1.vi.mocked(NotificationContext_1.useNotification).mockReturnValue({
            notifications: [],
            addNotification: vitest_1.vi.fn(),
            removeNotification: vitest_1.vi.fn(),
        });
        const { container } = (0, utils_1.render)((0, jsx_runtime_1.jsx)(NotificationContainer_1.default, {}));
        (0, vitest_1.expect)(container.firstChild).toBeNull();
    });
    (0, vitest_1.it)('renders info notification correctly', () => {
        const removeNotification = vitest_1.vi.fn();
        // Mock the useNotification hook to return an info notification
        vitest_1.vi.mocked(NotificationContext_1.useNotification).mockReturnValue({
            notifications: [
                { id: '1', type: 'info', message: 'This is an info message' },
            ],
            addNotification: vitest_1.vi.fn(),
            removeNotification,
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(NotificationContainer_1.default, {}));
        // Check that the notification is rendered with the correct styles and content
        const notification = utils_1.screen.getByText('This is an info message');
        (0, vitest_1.expect)(notification).toBeInTheDocument();
        // Check that the parent element has the correct background color class
        const notificationContainer = notification.closest('div[class*="bg-blue-100"]');
        (0, vitest_1.expect)(notificationContainer).toBeInTheDocument();
        // Check that the info icon is rendered
        (0, vitest_1.expect)(utils_1.screen.getByText('ℹ️')).toBeInTheDocument();
    });
    (0, vitest_1.it)('renders error notification correctly', () => {
        const removeNotification = vitest_1.vi.fn();
        // Mock the useNotification hook to return an error notification
        vitest_1.vi.mocked(NotificationContext_1.useNotification).mockReturnValue({
            notifications: [
                { id: '1', type: 'error', message: 'This is an error message' },
            ],
            addNotification: vitest_1.vi.fn(),
            removeNotification,
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(NotificationContainer_1.default, {}));
        // Check that the notification is rendered with the correct styles and content
        const notification = utils_1.screen.getByText('This is an error message');
        (0, vitest_1.expect)(notification).toBeInTheDocument();
        // Check that the parent element has the correct background color class
        const notificationContainer = notification.closest('div[class*="bg-red-100"]');
        (0, vitest_1.expect)(notificationContainer).toBeInTheDocument();
        // Check that the error icon is rendered
        (0, vitest_1.expect)(utils_1.screen.getByText('❌')).toBeInTheDocument();
    });
    (0, vitest_1.it)('calls removeNotification when close button is clicked', () => {
        const removeNotification = vitest_1.vi.fn();
        // Mock the useNotification hook to return a notification
        vitest_1.vi.mocked(NotificationContext_1.useNotification).mockReturnValue({
            notifications: [
                { id: '1', type: 'info', message: 'This is an info message' },
            ],
            addNotification: vitest_1.vi.fn(),
            removeNotification,
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(NotificationContainer_1.default, {}));
        // Click the close button
        const closeButton = utils_1.screen.getByRole('button', { name: /close notification/i });
        utils_1.fireEvent.click(closeButton);
        // Check that removeNotification was called with the correct ID
        (0, vitest_1.expect)(removeNotification).toHaveBeenCalledWith('1');
    });
    (0, vitest_1.it)('renders multiple notifications correctly', () => {
        const removeNotification = vitest_1.vi.fn();
        // Mock the useNotification hook to return multiple notifications
        vitest_1.vi.mocked(NotificationContext_1.useNotification).mockReturnValue({
            notifications: [
                { id: '1', type: 'info', message: 'This is an info message' },
                { id: '2', type: 'error', message: 'This is an error message' },
                { id: '3', type: 'warning', message: 'This is a warning message' },
            ],
            addNotification: vitest_1.vi.fn(),
            removeNotification,
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(NotificationContainer_1.default, {}));
        // Check that all notifications are rendered
        (0, vitest_1.expect)(utils_1.screen.getByText('This is an info message')).toBeInTheDocument();
        (0, vitest_1.expect)(utils_1.screen.getByText('This is an error message')).toBeInTheDocument();
        (0, vitest_1.expect)(utils_1.screen.getByText('This is a warning message')).toBeInTheDocument();
        // Check that all icons are rendered
        (0, vitest_1.expect)(utils_1.screen.getByText('ℹ️')).toBeInTheDocument();
        (0, vitest_1.expect)(utils_1.screen.getByText('❌')).toBeInTheDocument();
        (0, vitest_1.expect)(utils_1.screen.getByText('⚠️')).toBeInTheDocument();
    });
});
