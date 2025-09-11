import { Button } from './Button';
const meta = {
    title: 'UI/Button',
    component: Button,
    parameters: {
        layout: 'centered',
    },
    tags: ['autodocs'],
    argTypes: {
        variant: {
            control: { type: 'select' },
            options: ['primary', 'secondary', 'danger', 'success', 'warning'],
        },
        size: {
            control: { type: 'select' },
            options: ['sm', 'md', 'lg'],
        },
        onClick: { action: 'clicked' },
    },
};
export default meta;
export const Primary = {
    args: {
        variant: 'primary',
        children: 'Primary Button',
    },
};
export const Secondary = {
    args: {
        variant: 'secondary',
        children: 'Secondary Button',
    },
};
export const Danger = {
    args: {
        variant: 'danger',
        children: 'Danger Button',
    },
};
export const Success = {
    args: {
        variant: 'success',
        children: 'Success Button',
    },
};
export const Warning = {
    args: {
        variant: 'warning',
        children: 'Warning Button',
    },
};
export const Small = {
    args: {
        size: 'sm',
        children: 'Small Button',
    },
};
export const Medium = {
    args: {
        size: 'md',
        children: 'Medium Button',
    },
};
export const Large = {
    args: {
        size: 'lg',
        children: 'Large Button',
    },
};
export const Disabled = {
    args: {
        disabled: true,
        children: 'Disabled Button',
    },
};
export const FullWidth = {
    args: {
        fullWidth: true,
        children: 'Full Width Button',
    },
};
