import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface ProductCardProps {
  title: string;
  description?: string;
  price: string;
  imageUrl?: string;
  metadata?: Record<string, any>;
  actions?: Array<{
    label: string;
    action: string;
    data?: Record<string, any>;
    variant?: 'default' | 'outline' | 'destructive';
  }>;
  onAction?: (action: string, data?: Record<string, any>) => void;
  className?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  title,
  description,
  price,
  imageUrl,
  metadata,
  actions = [],
  onAction,
  className = ''
}) => {
  return (
    <Card className={`hover:shadow-lg transition-shadow ${className}`}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
        {description && (
          <CardDescription className="text-sm text-gray-600">
            {description}
          </CardDescription>
        )}
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Product Image */}
        {imageUrl && (
          <div className="w-full h-48 overflow-hidden rounded-md">
            <img 
              src={imageUrl} 
              alt={title} 
              className="w-full h-full object-cover hover:scale-105 transition-transform"
            />
          </div>
        )}
        
        {/* Price Display */}
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold text-green-600">
            {price}
          </span>
          {metadata?.brand && (
            <Badge variant="secondary" className="text-xs">
              {metadata.brand}
            </Badge>
          )}
        </div>
        
        {/* Metadata */}
        {metadata && Object.keys(metadata).length > 1 && (
          <div className="space-y-1">
            {Object.entries(metadata)
              .filter(([key]) => key !== 'brand') // Brand is shown as badge
              .map(([key, value]) => (
                <div key={key} className="flex justify-between text-sm text-gray-600">
                  <span className="capitalize font-medium">{key}:</span>
                  <span>{String(value)}</span>
                </div>
              ))
            }
          </div>
        )}
      </CardContent>
      
      {/* Action Buttons */}
      {actions.length > 0 && (
        <CardFooter className="flex gap-2 pt-4">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || (action.label === 'Add to Cart' ? 'default' : 'outline')}
              size="sm"
              className="flex-1"
              onClick={() => onAction?.(action.action, action.data)}
            >
              {action.label}
            </Button>
          ))}
        </CardFooter>
      )}
    </Card>
  );
};

export default ProductCard;