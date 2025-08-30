import { jsx as _jsx } from "react/jsx-runtime";
import { lazy, Suspense } from 'react';
import { LoadingSpinner } from './LoadingIndicator';
/**
 * LazyLoad component for lazy loading components with a loading fallback
 * @param component - Function that returns a promise resolving to a component
 * @param fallback - Optional custom fallback component to show while loading
 */
export function createLazyComponent(factory) {
    const LazyComponent = lazy(factory);
    return (props) => (_jsx(Suspense, { fallback: _jsx(LoadingSpinner, { size: "md" }), children: _jsx(LazyComponent, { ...props }) }));
}
/**
 * LazyLoad component for lazy loading components with a loading fallback
 * @param component - Function that returns a promise resolving to a component
 * @param fallback - Optional custom fallback component to show while loading
 * @param props - Additional props to pass to the lazy-loaded component
 */
export default function LazyLoad(props) {
    const { component, fallback, ...rest } = props;
    const LazyComponent = lazy(component);
    return (_jsx(Suspense, { fallback: fallback || _jsx(LoadingSpinner, { size: "md" }), children: _jsx(LazyComponent, { ...rest }) }));
}
