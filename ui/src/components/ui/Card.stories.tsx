import type { Meta, StoryObj } from '@storybook/react';
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
} satisfies Meta<typeof Card>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    title: 'Card Title',
    children: <p>This is a basic card with some content.</p>,
  },
};

export const WithSubtitle: Story = {
  args: {
    title: 'Card Title',
    subtitle: 'Card Subtitle',
    children: <p>This is a card with a title and subtitle.</p>,
  },
};

export const Outlined: Story = {
  args: {
    variant: 'outlined',
    title: 'Outlined Card',
    children: <p>This is an outlined card.</p>,
  },
};

export const Elevated: Story = {
  args: {
    variant: 'elevated',
    title: 'Elevated Card',
    children: <p>This is an elevated card with a shadow.</p>,
  },
};

export const WithFooter: Story = {
  args: {
    title: 'Card with Footer',
    children: <p>This card has a footer with actions.</p>,
    footerContent: (
      <div className="flex justify-end space-x-2">
        <Button variant="secondary" size="sm">Cancel</Button>
        <Button variant="primary" size="sm">Save</Button>
      </div>
    ),
  },
};

export const WithCustomHeader: Story = {
  args: {
    headerContent: (
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Custom Header</h3>
        <Button variant="secondary" size="sm">Action</Button>
      </div>
    ),
    children: <p>This card has a custom header with an action button.</p>,
  },
};

export const Clickable: Story = {
  args: {
    title: 'Clickable Card',
    children: <p>Click this card to trigger an action.</p>,
    onClick: () => alert('Card clicked!'),
  },
};