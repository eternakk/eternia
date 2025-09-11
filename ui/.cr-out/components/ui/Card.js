import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Card component for displaying content in a contained card format
 */
export const Card = ({ children, title, subtitle, variant = 'default', className = '', headerContent, footerContent, onClick, }) => {
    const baseClasses = 'rounded-lg overflow-hidden';
    const variantClasses = {
        default: 'bg-white',
        outlined: 'bg-white border border-gray-200',
        elevated: 'bg-white shadow-md',
    };
    const hasHeader = title || subtitle || headerContent;
    const hasFooter = footerContent;
    return (_jsxs("div", { className: `${baseClasses} ${variantClasses[variant]} ${className}`, onClick: onClick, role: onClick ? 'button' : undefined, tabIndex: onClick ? 0 : undefined, children: [hasHeader && (_jsx("div", { className: "px-4 py-3 border-b border-gray-200", children: headerContent || (_jsxs("div", { children: [title && _jsx("h3", { className: "text-lg font-medium text-gray-900", children: title }), subtitle && _jsx("p", { className: "text-sm text-gray-500", children: subtitle })] })) })), _jsx("div", { className: "p-4", children: children }), hasFooter && (_jsx("div", { className: "px-4 py-3 border-t border-gray-200 bg-gray-50", children: footerContent }))] }));
};
export default Card;
