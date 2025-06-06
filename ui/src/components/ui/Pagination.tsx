import React from 'react';

export interface PaginationProps {
  /**
   * Total number of items
   */
  totalItems: number;
  /**
   * Number of items per page
   */
  itemsPerPage: number;
  /**
   * Current page (1-based)
   */
  currentPage: number;
  /**
   * Callback when page changes
   */
  onPageChange: (page: number) => void;
  /**
   * Maximum number of page buttons to show
   */
  maxPageButtons?: number;
  /**
   * Optional additional className
   */
  className?: string;
}

/**
 * Pagination component for navigating through pages of data
 */
export const Pagination: React.FC<PaginationProps> = ({
  totalItems,
  itemsPerPage,
  currentPage,
  onPageChange,
  maxPageButtons = 5,
  className = '',
}) => {
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
  
  return (
    <nav 
      className={`flex items-center justify-center mt-4 ${className}`}
      aria-label="Pagination"
    >
      <ul className="flex items-center space-x-1">
        {/* Previous button */}
        <li>
          <button
            onClick={handlePrevious}
            disabled={validCurrentPage === 1}
            className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validCurrentPage === 1 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            aria-label="Go to previous page"
          >
            &laquo;
          </button>
        </li>
        
        {/* First page button if not in range */}
        {startPage > 1 && (
          <>
            <li>
              <button
                onClick={() => onPageChange(1)}
                className="px-3 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label="Go to page 1"
              >
                1
              </button>
            </li>
            {startPage > 2 && (
              <li className="px-1">
                <span className="text-gray-500">...</span>
              </li>
            )}
          </>
        )}
        
        {/* Page number buttons */}
        {pageNumbers.map(number => (
          <li key={number}>
            <button
              onClick={() => onPageChange(number)}
              className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                number === validCurrentPage
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              aria-label={`Go to page ${number}`}
              aria-current={number === validCurrentPage ? 'page' : undefined}
            >
              {number}
            </button>
          </li>
        ))}
        
        {/* Last page button if not in range */}
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && (
              <li className="px-1">
                <span className="text-gray-500">...</span>
              </li>
            )}
            <li>
              <button
                onClick={() => onPageChange(totalPages)}
                className="px-3 py-1 rounded bg-gray-200 text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                aria-label={`Go to page ${totalPages}`}
              >
                {totalPages}
              </button>
            </li>
          </>
        )}
        
        {/* Next button */}
        <li>
          <button
            onClick={handleNext}
            disabled={validCurrentPage === totalPages}
            className={`px-3 py-1 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              validCurrentPage === totalPages 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
            aria-label="Go to next page"
          >
            &raquo;
          </button>
        </li>
      </ul>
    </nav>
  );
};

export default Pagination;