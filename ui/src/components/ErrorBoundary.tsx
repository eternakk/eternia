import React from 'react';

export type ErrorBoundaryProps = {
  fallback?: React.ReactNode;
  onError?: (error: Error, info: React.ErrorInfo) => void;
  children: React.ReactNode;
};

export type ErrorBoundaryState = {
  hasError: boolean;
  error?: Error | null;
};

/**
 * ErrorBoundary: Catches render-time errors and displays a fallback UI instead of crashing the app.
 * Usage:
 *   <ErrorBoundary fallback={<MyFallback/>}>
 *     <RiskyComponent />
 *   </ErrorBoundary>
 */
export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Forward to optional onError reporter (e.g., to backend or console)
    if (this.props.onError) {
      try {
        this.props.onError(error, info);
      } catch {}
    }
    // Always log to console to aid local debugging
    // eslint-disable-next-line no-console
    console.error('[ErrorBoundary] Caught error:', error, info);
  }

  reset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      // Default fallback UI
      return (
        <div role="alert" className="p-4 m-4 border border-red-300 bg-red-50 text-red-800 rounded">
          <h2 className="font-bold mb-2">Something went wrong.</h2>
          <p className="text-sm opacity-80">An unexpected error occurred while rendering this section.</p>
          <button
            className="mt-3 px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
            onClick={this.reset}
          >
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
