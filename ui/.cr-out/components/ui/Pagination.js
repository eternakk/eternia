import { jsx as _jsx, Fragment as _Fragment, jsxs as _jsxs } from "react/jsx-runtime";
/**
 * Pagination component for navigating through pages of data
 */
export const Pagination = ({ totalItems, itemsPerPage, currentPage, onPageChange, maxPageButtons = 5, className = '', }) => {
    const totalPages = Math.max(1, Math.ceil(totalItems / itemsPerPage));
    // Ensure current page is within valid range
    const validCurrentPage = Math.min(Math.max(1, currentPage), totalPages);
    // Calculate range of page buttons to show
    let startPage = Math.max(1, validCurrentPage - Math.floor(maxPageButtons / 2));
    let endPage = startPage + maxPageButtons - 1;
    if (endPage > totalPages) {
        endPage = totalPages;
        startPage = Math.max(1, endPage - maxPageButtons + 1);
    }
    const pageNumbers = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);
    const handlePrevious = () => {
        if (validCurrentPage > 1) {
            onPageChange(validCurrentPage - 1);
        }
    };
    const handleNext = () => {
        if (validCurrentPage < totalPages) {
            onPageChange(validCurrentPage + 1);
        }
    };
    // Don't render pagination if there's only one page
    if (totalPages <= 1) {
        return null;
    }
    return (_jsx("nav", { className: `flex items-center justify-center mt-4 ${className}`, "aria-label": "Pagination", children: _jsxs("ul", { className: "flex items-center space-x-1", children: [_jsx("li", { children: _jsx("button", { onClick: handlePrevious, disabled: validCurrentPage === 1, className: `px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${validCurrentPage === 1
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`, "aria-label": "Go to previous page", children: "\u00AB" }) }), startPage > 1 && (_jsxs(_Fragment, { children: [_jsx("li", { children: _jsx("button", { onClick: () => onPageChange(1), className: "px-3 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": "Go to page 1", children: "1" }) }), startPage > 2 && (_jsx("li", { className: "px-1", children: _jsx("span", { className: "text-gray-500", children: "..." }) }))] })), pageNumbers.map(number => (_jsx("li", { children: _jsx("button", { onClick: () => onPageChange(number), className: `px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${number === validCurrentPage
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`, "aria-label": `Go to page ${number}`, "aria-current": number === validCurrentPage ? 'page' : undefined, children: number }) }, number))), endPage < totalPages && (_jsxs(_Fragment, { children: [endPage < totalPages - 1 && (_jsx("li", { className: "px-1", children: _jsx("span", { className: "text-gray-500", children: "..." }) })), _jsx("li", { children: _jsx("button", { onClick: () => onPageChange(totalPages), className: "px-3 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500", "aria-label": `Go to page ${totalPages}`, children: totalPages }) })] })), _jsx("li", { children: _jsx("button", { onClick: handleNext, disabled: validCurrentPage === totalPages, className: `px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${validCurrentPage === totalPages
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`, "aria-label": "Go to next page", children: "\u00BB" }) })] }) }));
};
export default Pagination;
