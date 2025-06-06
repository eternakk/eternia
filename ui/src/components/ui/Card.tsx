import React from 'react';

export interface CardProps {
  /**
   * Card contents
   */
  children: React.ReactNode;
  /**
   * Optional card title
   */
  title?: string;
  /**
   * Optional card subtitle
   */
  subtitle?: string;
  /**
   * Card variant
   */
  variant?: 'default' | 'outlined' | 'elevated';
  /**
   * Optional additional className
   */
  className?: string;
  /**
   * Optional header content
   */
  headerContent?: React.ReactNode;
  /**
   * Optional footer content
   */
  footerContent?: React.ReactNode;
  /**
   * Optional onClick handler
   */
  onClick?: () => void;
}

/**
 * Card component for displaying content in a contained card format
 */
export const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  variant = 'default',
  className = '',
  headerContent,
  footerContent,
  onClick,
}) => {
  const baseClasses = 'rounded-lg overflow-hidden';
  
  const variantClasses = {
    default: 'bg-white',
    outlined: 'bg-white border border-gray-200',
    elevated: 'bg-white shadow-md',
  };
  
  const hasHeader = title || subtitle || headerContent;
  const hasFooter = footerContent;
  
  return (
    <div 
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      {hasHeader && (
        <div className="px-4 py-3 border-b border-gray-200">
          {headerContent || (
            <div>
              {title && <h3 className="text-lg font-medium text-gray-900">{title}</h3>}
              {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
            </div>
          )}
        </div>
      )}
      
      <div className="p-4">
        {children}
      </div>
      
      {hasFooter && (
        <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
          {footerContent}
        </div>
      )}
    </div>
  );
};

export default Card;