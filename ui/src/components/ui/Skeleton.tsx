import React from 'react';

// Simple, dependency-free skeleton components using Tailwind classes
// Keep them visually light to avoid layout shift when content loads.

export type SkeletonProps = {
  className?: string;
  style?: React.CSSProperties;
  'data-testid'?: string;
};

export const SkeletonBlock: React.FC<SkeletonProps> = ({ className = '', style, ...rest }) => (
  <div
    className={`animate-pulse bg-slate-200 rounded ${className}`}
    style={style}
    aria-hidden="true"
    {...rest}
  />
);

export const SkeletonText: React.FC<SkeletonProps & { lines?: number; lineClassName?: string }> = ({
  lines = 3,
  className = '',
  lineClassName = 'h-3',
  style,
  ...rest
}) => {
  return (
    <div className={`space-y-2 ${className}`} aria-hidden="true" {...rest}>
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className={`animate-pulse bg-slate-200 rounded ${lineClassName}`} />
      ))}
    </div>
  );
};

export const SkeletonCircle: React.FC<SkeletonProps & { size?: number }> = ({ size = 40, className = '', style, ...rest }) => (
  <div
    className={`animate-pulse bg-slate-200 rounded-full ${className}`}
    style={{ width: size, height: size, ...style }}
    aria-hidden="true"
    {...rest}
  />
);

export const PanelSkeleton: React.FC<{ title?: string } & SkeletonProps> = ({ title, className = '', ...rest }) => (
  <div className={`p-4 border rounded-xl shadow bg-white ${className}`} {...rest}>
    <div className="flex items-center justify-between mb-4">
      <div className="font-semibold text-slate-700">{title || 'Loading…'}</div>
      <SkeletonCircle size={20} />
    </div>
    <SkeletonText lines={4} />
    <div className="grid grid-cols-3 gap-3 mt-4">
      <SkeletonBlock className="h-16" />
      <SkeletonBlock className="h-16" />
      <SkeletonBlock className="h-16" />
    </div>
  </div>
);

export default SkeletonBlock;
