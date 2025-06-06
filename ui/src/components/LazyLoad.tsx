import {ComponentType, JSX, lazy, Suspense} from 'react';
import {LoadingSpinner} from './LoadingIndicator';

interface LazyLoadProps<T extends JSX.IntrinsicAttributes = any> extends Omit<T, 'component' | 'fallback'> {
    component: () => Promise<{ default: ComponentType<T> }>;
    fallback?: React.ReactNode;
}

/**
 * LazyLoad component for lazy loading components with a loading fallback
 * @param component - Function that returns a promise resolving to a component
 * @param fallback - Optional custom fallback component to show while loading
 */
export function createLazyComponent<T extends JSX.IntrinsicAttributes>(
    factory: () => Promise<{ default: ComponentType<T> }>
) {
    const LazyComponent = lazy(factory);

    return (props: T = {} as T) => (
        <Suspense fallback={<LoadingSpinner size="md"/>}>
            <LazyComponent {...props} />
        </Suspense>
    );
}

/**
 * LazyLoad component for lazy loading components with a loading fallback
 * @param component - Function that returns a promise resolving to a component
 * @param fallback - Optional custom fallback component to show while loading
 * @param props - Additional props to pass to the lazy-loaded component
 */
export default function LazyLoad<T extends JSX.IntrinsicAttributes>(props: LazyLoadProps<T>) {
    const { component, fallback, ...rest } = props;
    const LazyComponent = lazy(component);

    return (
        <Suspense fallback={fallback || <LoadingSpinner size="md"/>}>
            <LazyComponent {...rest} />
        </Suspense>
    );
}
