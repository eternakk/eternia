import type { Meta, StoryObj } from '@storybook/react';
import { VirtualList } from './VirtualList';

// Define the item type
interface ListItem {
  id: number;
  text: string;
  description: string;
}

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
const generateItems = (count: number): ListItem[] => {
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
    renderItem: (item: unknown, index: number) => {
      const typedItem = item as ListItem;
      return (
        <div className="p-2 border-b border-gray-200">
          <div className="font-medium">{typedItem.text}</div>
          <div className="text-sm text-gray-500">{typedItem.description}</div>
        </div>
      );
    },
    itemHeight: 60,
    height: 300,
  },
};

// Example with custom styling
export const CustomStyling: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item: unknown, index: number) => {
      const typedItem = item as ListItem;
      return (
        <div className="p-3 border-b border-blue-200 hover:bg-blue-50">
          <div className="font-bold text-blue-700">{typedItem.text}</div>
          <div className="text-sm text-gray-600">{typedItem.description}</div>
        </div>
      );
    },
    itemHeight: 70,
    height: 350,
    className: 'border border-blue-300 rounded',
  },
};

// Example with very large dataset (10,000 items)
export const VeryLargeDataset: Story = {
  args: {
    items: generateItems(10000),
    renderItem: (item: unknown, index: number) => {
      const typedItem = item as ListItem;
      return (
        <div className="p-2 border-b border-gray-200">
          <div className="font-medium">{typedItem.text}</div>
          <div className="text-sm text-gray-500">{typedItem.description}</div>
        </div>
      );
    },
    itemHeight: 60,
    height: 400,
  },
};

// Example with small items
export const SmallItems: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item: unknown, index: number) => {
      const typedItem = item as ListItem;
      return (
        <div className="py-1 px-2 border-b border-gray-200 text-sm">
          {typedItem.text}
        </div>
      );
    },
    itemHeight: 30,
    height: 300,
  },
};

// Example with alternating row colors
export const AlternatingRows: Story = {
  args: {
    items: generateItems(1000),
    renderItem: (item: unknown, index: number) => {
      const typedItem = item as ListItem;
      return (
        <div 
          className={`p-2 border-b border-gray-200 ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}
        >
          <div className="font-medium">{typedItem.text}</div>
          <div className="text-sm text-gray-500">{typedItem.description}</div>
        </div>
      );
    },
    itemHeight: 60,
    height: 300,
  },
};
