import React from 'react';
import { Button } from '@/components/ui/button';

export interface CartItemProps {
  id: string;
  cartItemId?: number;
  name: string;
  price: number;
  quantity: number;
  imageUrl: string;
  brand: string;
  actions?: Array<{
    label: string;
    action: string;
    data?: Record<string, any>;
    variant?: 'default' | 'outline' | 'ghost' | 'destructive';
    icon?: string;
  }>;
  onAction?: (action: string, data?: Record<string, any>) => void;
  className?: string;
}

export const CartItem: React.FC<CartItemProps> = ({
  id,
  cartItemId,
  name,
  price,
  quantity,
  imageUrl,
  brand,
  actions = [],
  onAction,
  className = ''
}) => {
  const handleAction = (action: string, data?: Record<string, any>) => {
    onAction?.(action, { 
      ...data, 
      cartItemId, 
      productId: id,
      quantity,
      price 
    });
  };

  const defaultActions = [
    {
      label: 'Decrease',
      action: 'decrease_quantity',
      data: { productId: id },
      variant: 'outline' as const,
      icon: 'ri-subtract-line'
    },
    {
      label: 'Increase', 
      action: 'increase_quantity',
      data: { productId: id },
      variant: 'outline' as const,
      icon: 'ri-add-line'
    },
    {
      label: 'Remove',
      action: 'remove_item',
      data: { productId: id },
      variant: 'ghost' as const,
      icon: 'ri-delete-bin-line'
    }
  ];

  const combinedActions = actions.length > 0 ? actions : defaultActions;
  const totalPrice = (price * quantity).toFixed(2);

  return (
    <div className={`flex items-center space-x-4 p-4 border rounded-lg ${className}`}>
      {/* Product Image */}
      <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
        <img 
          src={imageUrl} 
          alt={name}
          className="w-full h-full object-cover"
          onError={(e) => {
            e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yMCAyMEg0NFY0NEgyMFYyMFoiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHBhdGggZD0iTTI4IDI4TDM2IDM2IiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPgo=';
          }}
        />
      </div>
      
      {/* Product Info */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold truncate">{name}</h3>
        <p className="text-sm text-gray-500">{brand}</p>
        <p className="text-lg font-bold text-blue-600">${price}</p>
      </div>

      {/* Quantity Controls */}
      <div className="flex items-center space-x-2">
        {combinedActions
          .filter(action => action.action === 'decrease_quantity')
          .map((action, index) => (
            <Button
              key={`decrease-${index}`}
              variant={action.variant || 'outline'}
              size="sm"
              onClick={() => handleAction(action.action, action.data)}
              disabled={quantity <= 1}
            >
              <i className={action.icon || 'ri-subtract-line'}></i>
            </Button>
          ))
        }
        
        <span className="w-8 text-center font-semibold">{quantity}</span>
        
        {combinedActions
          .filter(action => action.action === 'increase_quantity')
          .map((action, index) => (
            <Button
              key={`increase-${index}`}
              variant={action.variant || 'outline'}
              size="sm"
              onClick={() => handleAction(action.action, action.data)}
            >
              <i className={action.icon || 'ri-add-line'}></i>
            </Button>
          ))
        }
      </div>

      {/* Total Price and Remove */}
      <div className="text-right">
        <p className="font-bold">${totalPrice}</p>
        {combinedActions
          .filter(action => action.action === 'remove_item')
          .map((action, index) => (
            <Button
              key={`remove-${index}`}
              variant={action.variant || 'ghost'}
              size="sm"
              onClick={() => handleAction(action.action, action.data)}
              className="text-red-500 hover:text-red-700"
            >
              <i className={action.icon || 'ri-delete-bin-line'}></i>
            </Button>
          ))
        }
      </div>

      {/* Additional Custom Actions */}
      {combinedActions
        .filter(action => !['decrease_quantity', 'increase_quantity', 'remove_item'].includes(action.action))
        .map((action, index) => (
          <Button
            key={`custom-${index}`}
            variant={action.variant || 'outline'}
            size="sm"
            onClick={() => handleAction(action.action, action.data)}
          >
            {action.icon && <i className={`${action.icon} mr-2`}></i>}
            {action.label}
          </Button>
        ))
      }
    </div>
  );
};

export default CartItem;