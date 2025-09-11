import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { forwardRef } from 'react';
/**
 * Input component for text entry
 */
export const Input = forwardRef(({ label, helperText, error, size = 'md', fullWidth = false, variant = 'outlined', className = '', startIcon, endIcon, disabled = false, id, ...rest }, ref) => {
    // Generate a unique ID if none is provided
    const inputId = id || `input-${Math.random().toString(36).substring(2, 9)}`;
    const baseClasses = 'rounded focus:outline-none transition-colors';
    const sizeClasses = {
        sm: 'py-1 px-2 text-sm',
        md: 'py-2 px-3 text-base',
        lg: 'py-3 px-4 text-lg',
    };
    const variantClasses = {
        outlined: 'border border-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 bg-white',
        filled: 'border border-transparent bg-gray-100 focus:bg-white focus:border-blue-500',
    };
    const widthClass = fullWidth ? 'w-full' : '';
    const errorClass = error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : '';
    const disabledClass = disabled ? 'bg-gray-100 text-gray-500 cursor-not-allowed' : '';
    const hasStartIcon = !!startIcon;
    const hasEndIcon = !!endIcon;
    const paddingLeftClass = hasStartIcon ? 'pl-10' : '';
    const paddingRightClass = hasEndIcon ? 'pr-10' : '';
    return (_jsxs("div", { className: `${fullWidth ? 'w-full' : ''} ${className}`, children: [label && (_jsx("label", { htmlFor: inputId, className: "block text-sm font-medium text-gray-700 mb-1", children: label })), _jsxs("div", { className: "relative", children: [hasStartIcon && (_jsx("div", { className: "absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-gray-500", children: startIcon })), _jsx("input", { ref: ref, id: inputId, disabled: disabled, className: `
              ${baseClasses}
              ${sizeClasses[size]}
              ${variantClasses[variant]}
              ${widthClass}
              ${errorClass}
              ${disabledClass}
              ${paddingLeftClass}
              ${paddingRightClass}
            `, ...rest }), hasEndIcon && (_jsx("div", { className: "absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-gray-500", children: endIcon }))] }), (helperText || error) && (_jsx("p", { className: `mt-1 text-sm ${error ? 'text-red-600' : 'text-gray-500'}`, children: error || helperText }))] }));
});
Input.displayName = 'Input';
export default Input;
