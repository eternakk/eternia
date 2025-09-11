import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { VirtualList } from './VirtualList';
const meta = {
    title: 'UI/VirtualList',
    component: VirtualList,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
};
export default meta;
// Generate a large list of items for the examples
const generateItems = (count) => {
    return Array.from({ length: count }, (_, i) => ({
        id: i,
        text: `Item ${i + 1}`,
        description: `This is the description for item ${i + 1}`,
    }));
};
// Basic example with 1000 items
export const Default = {
    args: {
        items: generateItems(1000),
        renderItem: (item) => {
            const typedItem = item;
            return (_jsxs("div", { className: "p-2 border-b border-gray-200", children: [_jsx("div", { className: "font-medium", children: typedItem.text }), _jsx("div", { className: "text-sm text-gray-500", children: typedItem.description })] }));
        },
        itemHeight: 60,
        height: 300,
    },
};
// Example with custom styling
export const CustomStyling = {
    args: {
        items: generateItems(1000),
        renderItem: (item) => {
            const typedItem = item;
            return (_jsxs("div", { className: "p-3 border-b border-blue-200 hover:bg-blue-50", children: [_jsx("div", { className: "font-bold text-blue-700", children: typedItem.text }), _jsx("div", { className: "text-sm text-gray-600", children: typedItem.description })] }));
        },
        itemHeight: 70,
        height: 350,
        className: 'border border-blue-300 rounded',
    },
};
// Example with very large dataset (10,000 items)
export const VeryLargeDataset = {
    args: {
        items: generateItems(10000),
        renderItem: (item) => {
            const typedItem = item;
            return (_jsxs("div", { className: "p-2 border-b border-gray-200", children: [_jsx("div", { className: "font-medium", children: typedItem.text }), _jsx("div", { className: "text-sm text-gray-500", children: typedItem.description })] }));
        },
        itemHeight: 60,
        height: 400,
    },
};
// Example with small items
export const SmallItems = {
    args: {
        items: generateItems(1000),
        renderItem: (item) => {
            const typedItem = item;
            return (_jsx("div", { className: "py-1 px-2 border-b border-gray-200 text-sm", children: typedItem.text }));
        },
        itemHeight: 30,
        height: 300,
    },
};
// Example with alternating row colors
export const AlternatingRows = {
    args: {
        items: generateItems(1000),
        renderItem: (item, index) => {
            const typedItem = item;
            return (_jsxs("div", { className: `p-2 border-b border-gray-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`, children: [_jsx("div", { className: "font-medium", children: typedItem.text }), _jsx("div", { className: "text-sm text-gray-500", children: typedItem.description })] }));
        },
        itemHeight: 60,
        height: 300,
    },
};
