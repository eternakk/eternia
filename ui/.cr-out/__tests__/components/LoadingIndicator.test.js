"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const vitest_1 = require("vitest");
const utils_1 = require("../../test/utils");
const LoadingIndicator_1 = require("../../components/LoadingIndicator");
const LoadingContext_1 = require("../../contexts/LoadingContext");
// Mock the useLoading hook
vitest_1.vi.mock('../../contexts/LoadingContext', async () => {
    const actual = await vitest_1.vi.importActual('../../contexts/LoadingContext');
    return {
        ...actual,
        useLoading: vitest_1.vi.fn(),
    };
});
(0, vitest_1.describe)('LoadingIndicator', () => {
    (0, vitest_1.beforeEach)(() => {
        vitest_1.vi.resetAllMocks();
    });
    (0, vitest_1.it)('renders children when not loading', () => {
        // Mock the useLoading hook to return not loading
        vitest_1.vi.mocked(LoadingContext_1.useLoading).mockReturnValue({
            isLoading: () => false,
            loadingOperations: [],
            startLoading: vitest_1.vi.fn(),
            stopLoading: vitest_1.vi.fn(),
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingIndicator, { children: (0, jsx_runtime_1.jsx)("div", { "data-testid": "child", children: "Child Content" }) }));
        (0, vitest_1.expect)(utils_1.screen.getByTestId('child')).toBeInTheDocument();
        (0, vitest_1.expect)(utils_1.screen.getByText('Child Content')).toBeInTheDocument();
    });
    (0, vitest_1.it)('renders loading indicator when loading', () => {
        // Mock the useLoading hook to return loading
        vitest_1.vi.mocked(LoadingContext_1.useLoading).mockReturnValue({
            isLoading: () => true,
            loadingOperations: [{ id: '1', operationKey: 'test', message: 'Loading...' }],
            startLoading: vitest_1.vi.fn(),
            stopLoading: vitest_1.vi.fn(),
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingIndicator, { children: (0, jsx_runtime_1.jsx)("div", { "data-testid": "child", children: "Child Content" }) }));
        // Child content should be in the document but with opacity
        const child = utils_1.screen.getByTestId('child');
        (0, vitest_1.expect)(child).toBeInTheDocument();
        (0, vitest_1.expect)(child.parentElement).toHaveClass('opacity-50');
        // Loading message should be displayed
        (0, vitest_1.expect)(utils_1.screen.getByText('Loading...')).toBeInTheDocument();
    });
    (0, vitest_1.it)('uses custom fallback when provided', () => {
        // Mock the useLoading hook to return loading
        vitest_1.vi.mocked(LoadingContext_1.useLoading).mockReturnValue({
            isLoading: () => true,
            loadingOperations: [],
            startLoading: vitest_1.vi.fn(),
            stopLoading: vitest_1.vi.fn(),
        });
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingIndicator, { fallback: (0, jsx_runtime_1.jsx)("div", { "data-testid": "custom-fallback", children: "Custom Fallback" }), children: (0, jsx_runtime_1.jsx)("div", { "data-testid": "child", children: "Child Content" }) }));
        (0, vitest_1.expect)(utils_1.screen.getByTestId('custom-fallback')).toBeInTheDocument();
        (0, vitest_1.expect)(utils_1.screen.getByText('Custom Fallback')).toBeInTheDocument();
    });
});
(0, vitest_1.describe)('LoadingSpinner', () => {
    (0, vitest_1.it)('renders with default size', () => {
        const { container } = (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingSpinner, {}));
        const spinner = container.querySelector('.animate-spin');
        (0, vitest_1.expect)(spinner).toBeInTheDocument();
        (0, vitest_1.expect)(spinner).toHaveClass('h-8 w-8'); // Default size is 'md'
    });
    (0, vitest_1.it)('renders with small size', () => {
        const { container } = (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingSpinner, { size: "sm" }));
        const spinner = container.querySelector('.animate-spin');
        (0, vitest_1.expect)(spinner).toBeInTheDocument();
        (0, vitest_1.expect)(spinner).toHaveClass('h-4 w-4');
    });
    (0, vitest_1.it)('renders with large size', () => {
        const { container } = (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingSpinner, { size: "lg" }));
        const spinner = container.querySelector('.animate-spin');
        (0, vitest_1.expect)(spinner).toBeInTheDocument();
        (0, vitest_1.expect)(spinner).toHaveClass('h-12 w-12');
    });
    (0, vitest_1.it)('displays message when provided', () => {
        (0, utils_1.render)((0, jsx_runtime_1.jsx)(LoadingIndicator_1.LoadingSpinner, { message: "Loading data..." }));
        (0, vitest_1.expect)(utils_1.screen.getByText('Loading data...')).toBeInTheDocument();
    });
});
