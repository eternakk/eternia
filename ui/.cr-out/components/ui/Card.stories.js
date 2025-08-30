import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Card } from './Card';
import { Button } from './Button';
const meta = {
    title: 'UI/Card',
    component: Card,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
    argTypes: {
        variant: {
            control: { type: 'select' },
            options: ['default', 'outlined', 'elevated'],
        },
        onClick: { action: 'clicked' },
    },
};
export default meta;
export const Default = {
    args: {
        title: 'Card Title',
        children: _jsx("p", { children: "This is a basic card with some content." }),
    },
};
export const WithSubtitle = {
    args: {
        title: 'Card Title',
        subtitle: 'Card Subtitle',
        children: _jsx("p", { children: "This is a card with a title and subtitle." }),
    },
};
export const Outlined = {
    args: {
        variant: 'outlined',
        title: 'Outlined Card',
        children: _jsx("p", { children: "This is an outlined card." }),
    },
};
export const Elevated = {
    args: {
        variant: 'elevated',
        title: 'Elevated Card',
        children: _jsx("p", { children: "This is an elevated card with a shadow." }),
    },
};
export const WithFooter = {
    args: {
        title: 'Card with Footer',
        children: _jsx("p", { children: "This card has a footer with actions." }),
        footerContent: (_jsxs("div", { className: "flex justify-end space-x-2", children: [_jsx(Button, { variant: "secondary", size: "sm", children: "Cancel" }), _jsx(Button, { variant: "primary", size: "sm", children: "Save" })] })),
    },
};
export const WithCustomHeader = {
    args: {
        headerContent: (_jsxs("div", { className: "flex justify-between items-center", children: [_jsx("h3", { className: "text-lg font-medium text-gray-900", children: "Custom Header" }), _jsx(Button, { variant: "secondary", size: "sm", children: "Action" })] })),
        children: _jsx("p", { children: "This card has a custom header with an action button." }),
    },
};
export const Clickable = {
    args: {
        title: 'Clickable Card',
        children: _jsx("p", { children: "Click this card to trigger an action." }),
        onClick: () => alert('Card clicked!'),
    },
};
