import type { Meta, StoryObj } from '@storybook/react';
import { Pagination } from './Pagination';
import { useState } from 'react';

const meta = {
  title: 'UI/Pagination',
  component: Pagination,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Pagination>;

export default meta;
type Story = StoryObj<typeof meta>;

// Basic pagination example
export const Default: Story = {
  args: {
    totalItems: 100,
    itemsPerPage: 10,
    currentPage: 1,
    onPageChange: () => {},
  },
};

// Interactive example with state
const InteractivePaginationTemplate = () => {
  const [currentPage, setCurrentPage] = useState(1);
  
  return (
    <div className="w-full max-w-2xl">
      <div className="mb-4 p-4 bg-gray-100 rounded">
        <p>Current Page: {currentPage}</p>
      </div>
      <Pagination
        totalItems={100}
        itemsPerPage={10}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
      />
    </div>
  );
};

export const Interactive: Story = {
  render: () => <InteractivePaginationTemplate />,
};

// Example with many pages
export const ManyPages: Story = {
  args: {
    totalItems: 500,
    itemsPerPage: 10,
    currentPage: 25,
    onPageChange: () => {},
  },
};

// Example with few pages
export const FewPages: Story = {
  args: {
    totalItems: 30,
    itemsPerPage: 10,
    currentPage: 2,
    onPageChange: () => {},
  },
};

// Example with custom max page buttons
export const CustomMaxPageButtons: Story = {
  args: {
    totalItems: 100,
    itemsPerPage: 10,
    currentPage: 5,
    maxPageButtons: 3,
    onPageChange: () => {},
  },
};