import type { Meta, StoryObj } from '@storybook/react';
import { VirtualList } from './VirtualList';

const meta = {
  title: 'UI/VirtualList',
  component: VirtualList,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof VirtualList>;

export default meta;
type Story = StoryObj<typeof meta>;

// Generate a large list of items for the examples
const generateItems = (count: number) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    text: `Item ${i + 1}`,
    description: `This is the description for item ${i + 1}`,
  }));
};

// Basic example with 1000 items
export const Default: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item) => (
      <div className="p-2 border-b border-gray-200">
        <div className="font-medium">{item.text}</div>
        <div className="text-sm text-gray-500">{item.description}</div>
      </div>
    ),
    itemHeight: 60,
    height: 300,
  },
};

// Example with custom styling
export const CustomStyling: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item) => (
      <div className="p-3 border-b border-blue-200 hover:bg-blue-50">
        <div className="font-bold text-blue-700">{item.text}</div>
        <div className="text-sm text-gray-600">{item.description}</div>
      </div>
    ),
    itemHeight: 70,
    height: 350,
    className: 'border border-blue-300 rounded',
  },
};

// Example with very large dataset (10,000 items)
export const VeryLargeDataset: Story = {
  args: {
    items: generateItems(10000),
    renderItem: (item) => (
      <div className="p-2 border-b border-gray-200">
        <div className="font-medium">{item.text}</div>
        <div className="text-sm text-gray-500">{item.description}</div>
      </div>
    ),
    itemHeight: 60,
    height: 400,
  },
};

// Example with small items
export const SmallItems: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item) => (
      <div className="py-1 px-2 border-b border-gray-200 text-sm">
        {item.text}
      </div>
    ),
    itemHeight: 30,
    height: 300,
  },
};

// Example with alternating row colors
export const AlternatingRows: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item, index) => (
      <div 
        className={`p-2 border-b border-gray-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}
      >
        <div className="font-medium">{item.text}</div>
        <div className="text-sm text-gray-500">{item.description}</div>
      </div>
    ),
    itemHeight: 60,
    height: 300,
  },
};