import { jsxs as _jsxs, jsx as _jsx } from "react/jsx-runtime";
import { Pagination } from './Pagination';
import { useState } from 'react';
const meta = {
    title: 'UI/Pagination',
    component: Pagination,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
};
export default meta;
// Basic pagination example
export const Default = {
    args: {
        totalItems: 100,
        itemsPerPage: 10,
        currentPage: 1,
        onPageChange: () => { },
    },
};
// Interactive example with state
const InteractivePaginationTemplate = () => {
    const [currentPage, setCurrentPage] = useState(1);
    return (_jsxs("div", { className: "w-full max-w-2xl", children: [_jsx("div", { className: "mb-4 p-4 bg-gray-100 rounded", children: _jsxs("p", { children: ["Current Page: ", currentPage] }) }), _jsx(Pagination, { totalItems: 100, itemsPerPage: 10, currentPage: currentPage, onPageChange: setCurrentPage })] }));
};
export const Interactive = {
    args: {
        totalItems: 100,
        itemsPerPage: 10,
        currentPage: 1,
        onPageChange: () => { },
    },
    render: () => _jsx(InteractivePaginationTemplate, {}),
};
// Example with many pages
export const ManyPages = {
    args: {
        totalItems: 500,
        itemsPerPage: 10,
        currentPage: 25,
        onPageChange: () => { },
    },
};
// Example with few pages
export const FewPages = {
    args: {
        totalItems: 30,
        itemsPerPage: 10,
        currentPage: 2,
        onPageChange: () => { },
    },
};
// Example with custom max page buttons
export const CustomMaxPageButtons = {
    args: {
        totalItems: 100,
        itemsPerPage: 10,
        currentPage: 5,
        maxPageButtons: 3,
        onPageChange: () => { },
    },
};
