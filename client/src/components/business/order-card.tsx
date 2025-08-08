import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

export interface OrderItemProps {
  id: string;
  product_name: string;
  quantity: number;
  price: number;
  total: number;
  imageUrl?: string;
  brand?: string;
}

export interface OrderCardProps {
  id: string;
  status: 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';
  total: number;
  createdAt: string | Date;
  items?: OrderItemProps[];
  trackingNumber?: string;
  actions?: Array<{
    label: string;
    action: string;
    data?: Record<string, any>;
    variant?: 'default' | 'outline' | 'destructive';
  }>;
  onAction?: (action: string, data?: Record<string, any>) => void;
  className?: string;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'delivered': return 'bg-green-100 text-green-800 border-green-200';
    case 'shipped': return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'processing': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'pending': return 'bg-gray-100 text-gray-800 border-gray-200';
    case 'cancelled': return 'bg-red-100 text-red-800 border-red-200';
    default: return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export const OrderCard: React.FC<OrderCardProps> = ({
  id,
  status,
  total,
  createdAt,
  items = [],
  trackingNumber,
  actions = [],
  onAction,
  className = ''
}) => {
  const formatDate = (date: string | Date) => {
    return new Date(date).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            Order #{id}
          </CardTitle>
          <Badge className={getStatusColor(status)}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Badge>
        </div>
        <CardDescription className="text-sm text-gray-600">
          Placed on {formatDate(createdAt)}
          {trackingNumber && (
            <span className="ml-2">• Tracking: {trackingNumber}</span>
          )}
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Order Items */}
        {items.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-700">Items ({items.length})</h4>
            <div className="space-y-3">
              {items.map((item, index) => (
                <div key={item.id || index} className="flex items-center space-x-3 text-sm">
                  {/* Product Image */}
                  <div className="w-12 h-12 bg-gray-100 rounded-md overflow-hidden flex-shrink-0">
                    <img 
                      src={item.imageUrl || '/placeholder-product.jpg'} 
                      alt={item.product_name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNiAxNkgzMlYzMkgxNlYxNloiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHBhdGggZD0iTTIxIDIxTDI3IDI3IiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPgo=';
                      }}
                    />
                  </div>
                  
                  {/* Product Info */}
                  <div className="flex-1 min-w-0">
                    <div className="text-gray-900 font-medium truncate">{item.product_name}</div>
                    {item.brand && (
                      <div className="text-gray-500 text-xs">{item.brand}</div>
                    )}
                    <div className="text-gray-500 text-xs">Quantity: {item.quantity}</div>
                  </div>
                  
                  {/* Price */}
                  <div className="text-right">
                    <div className="font-medium text-gray-900">
                      {formatCurrency(item.total)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatCurrency(item.price)} each
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <Separator />
          </div>
        )}
        
        {/* Order Total */}
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-900">Total</span>
          <span className="text-xl font-bold text-green-600">
            {formatCurrency(total)}
          </span>
        </div>
      </CardContent>
      
      {/* Action Buttons */}
      {actions.length > 0 && (
        <CardFooter className="flex gap-2 pt-4">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'outline'}
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

export default OrderCard;