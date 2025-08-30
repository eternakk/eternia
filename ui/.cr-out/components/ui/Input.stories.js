import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { Input } from './Input';
const meta = {
    title: 'UI/Input',
    component: Input,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
    argTypes: {
        variant: {
            control: { type: 'select' },
            options: ['outlined', 'filled'],
        },
        size: {
            control: { type: 'select' },
            options: ['sm', 'md', 'lg'],
        },
        type: {
            control: { type: 'select' },
            options: ['text', 'password', 'email', 'number', 'tel', 'url'],
        },
    },
};
export default meta;
export const Default = {
    args: {
        placeholder: 'Enter text...',
    },
};
export const WithLabel = {
    args: {
        label: 'Email',
        placeholder: 'Enter your email',
        type: 'email',
    },
};
export const WithHelperText = {
    args: {
        label: 'Password',
        placeholder: 'Enter your password',
        type: 'password',
        helperText: 'Password must be at least 8 characters',
    },
};
export const WithError = {
    args: {
        label: 'Username',
        placeholder: 'Enter your username',
        error: 'Username is already taken',
        value: 'johndoe',
    },
};
export const Filled = {
    args: {
        label: 'Search',
        placeholder: 'Search...',
        variant: 'filled',
    },
};
export const Small = {
    args: {
        size: 'sm',
        placeholder: 'Small input',
    },
};
export const Medium = {
    args: {
        size: 'md',
        placeholder: 'Medium input',
    },
};
export const Large = {
    args: {
        size: 'lg',
        placeholder: 'Large input',
    },
};
export const FullWidth = {
    args: {
        label: 'Full Width',
        placeholder: 'This input takes up the full width',
        fullWidth: true,
    },
};
export const Disabled = {
    args: {
        label: 'Disabled Input',
        placeholder: 'You cannot edit this',
        disabled: true,
        value: 'Disabled value',
    },
};
export const WithStartIcon = {
    args: {
        label: 'Search',
        placeholder: 'Search...',
        startIcon: (_jsx("svg", { xmlns: "http://www.w3.org/2000/svg", className: "h-5 w-5", viewBox: "0 0 20 20", fill: "currentColor", children: _jsx("path", { fillRule: "evenodd", d: "M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z", clipRule: "evenodd" }) })),
    },
};
export const WithEndIcon = {
    args: {
        label: 'Password',
        type: 'password',
        placeholder: 'Enter your password',
        endIcon: (_jsxs("svg", { xmlns: "http://www.w3.org/2000/svg", className: "h-5 w-5", viewBox: "0 0 20 20", fill: "currentColor", children: [_jsx("path", { d: "M10 12a2 2 0 100-4 2 2 0 000 4z" }), _jsx("path", { fillRule: "evenodd", d: "M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z", clipRule: "evenodd" })] })),
    },
};
