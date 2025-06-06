import React, { useRef, useState, useEffect } from 'react';

export interface VirtualListProps<T> {
  /**
   * Array of items to render
   */
  items: T[];
  /**
   * Function to render each item
   */
  renderItem: (item: T, index: number) => React.ReactNode;
  /**
   * Height of each item in pixels
   */
  itemHeight: number;
  /**
   * Height of the container in pixels
   */
  height: number;
  /**
   * Optional additional className for the container
   */
  className?: string;
  /**
   * Number of items to render above and below the visible area
   */
  overscan?: number;
  /**
   * Optional ID for the container
   */
  id?: string;
  /**
   * Optional ARIA role for the list
   */
  role?: string;
  /**
   * Optional ARIA label for the list
   */
  ariaLabel?: string;
}

/**
 * VirtualList component for efficiently rendering large lists
 */
export function VirtualList<T>({
  items,
  renderItem,
  itemHeight,
  height,
  className = '',
  overscan = 3,
  id,
  role = 'list',
  ariaLabel,
}: VirtualListProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scrollTop, setScrollTop] = useState(0);

  // Update scrollTop when the user scrolls
  useEffect(() => {
    const handleScroll = () => {
      if (containerRef.current) {
        setScrollTop(containerRef.current.scrollTop);
      }
    };

    const container = containerRef.current;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, []);

  // Calculate which items to render
  const totalHeight = items.length * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.floor((scrollTop + height) / itemHeight) + overscan
  );

  // Slice the items to render only those in view (plus overscan)
  const visibleItems = items.slice(startIndex, endIndex + 1);

  return (
    <div
      ref={containerRef}
      className={`overflow-y-auto ${className}`}
      style={{ height: `${height}px` }}
      id={id}
      role={role}
      aria-label={ariaLabel}
    >
      <div
        className="relative"
        style={{ height: `${totalHeight}px` }}
      >
        {visibleItems.map((item, index) => {
          const actualIndex = startIndex + index;
          return (
            <div
              key={actualIndex}
              style={{
                position: 'absolute',
                top: `${actualIndex * itemHeight}px`,
                height: `${itemHeight}px`,
                width: '100%',
              }}
              role={role === 'list' ? 'listitem' : undefined}
            >
              {renderItem(item, actualIndex)}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default VirtualList;