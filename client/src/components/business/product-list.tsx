import React from 'react';
import { ProductCard, ProductCardProps } from './product-card';

export interface ProductListProps {
  products: Array<ProductCardProps & { id: string }>;
  onAction?: (action: string, data?: Record<string, any>) => void;
  layout?: 'grid' | 'list';
  className?: string;
  title?: string;
  description?: string;
}

export const ProductList: React.FC<ProductListProps> = ({
  products,
  onAction,
  layout = 'grid',
  className = '',
  title,
  description
}) => {
  const layoutClasses = layout === 'grid' 
    ? 'grid gap-4 md:grid-cols-2 lg:grid-cols-3'
    : 'space-y-4';

  return (
    <div className={className}>
      {/* List Header */}
      {(title || description) && (
        <div className="mb-6">
          {title && (
            <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
          )}
          {description && (
            <p className="text-gray-600">{description}</p>
          )}
        </div>
      )}
      
      {/* Products Grid/List */}
      {products.length > 0 ? (
        <div className={layoutClasses}>
          {products.map((product) => (
            <ProductCard
              key={product.id}
              {...product}
              onAction={onAction}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <i className="ri-inbox-line text-4xl"></i>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No products found
          </h3>
          <p className="text-gray-500">
            Try adjusting your search criteria or browse our categories.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProductList;