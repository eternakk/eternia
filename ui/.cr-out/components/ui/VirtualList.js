import { jsx as _jsx } from "react/jsx-runtime";
import { useRef, useState, useEffect } from 'react';
/**
 * VirtualList component for efficiently rendering large lists
 */
export function VirtualList({ items, renderItem, itemHeight, height, className = '', overscan = 3, id, role = 'list', ariaLabel, }) {
    const containerRef = useRef(null);
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
    const endIndex = Math.min(items.length - 1, Math.floor((scrollTop + height) / itemHeight) + overscan);
    // Slice the items to render only those in view (plus overscan)
    const visibleItems = items.slice(startIndex, endIndex + 1);
    return (_jsx("div", { ref: containerRef, className: `overflow-y-auto ${className}`, style: { height: `${height}px` }, id: id, role: role, "aria-label": ariaLabel, children: _jsx("div", { className: "relative", style: { height: `${totalHeight}px` }, children: visibleItems.map((item, index) => {
                const actualIndex = startIndex + index;
                return (_jsx("div", { style: {
                        position: 'absolute',
                        top: `${actualIndex * itemHeight}px`,
                        height: `${itemHeight}px`,
                        width: '100%',
                    }, role: role === 'list' ? 'listitem' : undefined, children: renderItem(item, actualIndex) }, actualIndex));
            }) }) }));
}
export default VirtualList;
