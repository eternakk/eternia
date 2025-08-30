"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const vitest_1 = require("vitest");
const utils_1 = require("../../test/utils");
const LoadingContext_1 = require("../../contexts/LoadingContext");
const GlobalLoadingIndicator_1 = __importDefault(require("../../components/GlobalLoadingIndicator"));
// Mock the useLoading hook
vitest_1.vi.mock('../../contexts/LoadingContext', async () => {
    const actual = await vitest_1.vi.importActual('../../contexts/LoadingContext');
    return {
        ...actual,
        useLoading: vitest_1.vi.fn(),
    };
});
(0, vitest_1.describe)('GlobalLoadingIndicator', () => {
    (0, vitest_1.beforeEach)(() => {
        vitest_1.vi.resetAllMocks();
    });
    (0, vitest_1.it)('renders nothing when not loading', () => {
        // Mock the useLoading hook to return not loading
        vitest_1.vi.mocked(LoadingContext_1.useLoading).mockReturnValue({
            isLoading: () => false,
            loadingOperations: [],
            startLoading: vitest_1.vi.fn(),
            stopLoading: vitest_1.vi.fn(),
        });
        const { container } = (0, utils_1.render)((0, jsx_runtime_1.jsx)(GlobalLoadingIndicator_1.default, {}));
        (0, vitest_1.expect)(container.firstChild).toBeNull();
    });
    (0, vitest_1.it)('renders loading indicator when loading', () => {
        // Mock the useLoading hook to return loading
        vitest_1.vi.mocked(LoadingContext_1.useLoading).mockReturnValue({
            isLoading: () => true,
            loadingOperations: [{ id: '1', operationKey: 'test', message: 'Loading...' }],
            startLoading: vitest_1.vi.fn(),
            stopLoading: vitest_1.vi.fn(),
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(GlobalLoadingIndicator_1.default, {}));
        // Check that the loading indicator is rendered
        (0, vitest_1.expect)(utils_1.screen.getByText('Loading...')).toBeInTheDocument();
    });
    (0, vitest_1.it)('renders default message when no message is provided', () => {
        // Mock the useLoading hook to return loading but without a message
        vitest_1.vi.mocked(LoadingContext_1.useLoading).mockReturnValue({
            isLoading: () => true,
            loadingOperations: [{ id: '1', operationKey: 'test' }],
            startLoading: vitest_1.vi.fn(),
            stopLoading: vitest_1.vi.fn(),
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(GlobalLoadingIndicator_1.default, {}));
        // Check that the default loading message is rendered
        (0, vitest_1.expect)(utils_1.screen.getByText('Loading...')).toBeInTheDocument();
    });
});
