import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface Product {
  id: string;
  name: string;
  description?: string;
  imageUrl?: string;
  price: number;
  brand?: string;
  color?: string;
  size?: string;
  model?: string;
  specifications?: string;
}

interface OrderItem {
  id: number;
  productId: string;
  quantity: number;
  price: number;
  selectedSize?: string;
  selectedColor?: string;
  selectedConfiguration?: string;
  product?: Product;
}

interface Order {
  id: string;
  customerId: string;
  date: string;
  items: string;
  amount: number;
  status: string;
  orderItems?: OrderItem[];
}

interface OrderViewDialogProps {
  order: Order | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const OrderViewDialog: React.FC<OrderViewDialogProps> = ({ 
  order, 
  open, 
  onOpenChange 
}) => {
  if (!order) return null;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'pending':
        return 'bg-yellow-50 text-yellow-700 border-yellow-200';
      case 'failed':
        return 'bg-red-50 text-red-700 border-red-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Order Details</DialogTitle>
          <DialogDescription>
            View complete order information and transaction details.
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <span className="text-sm font-medium text-slate-500">Order ID:</span>
            <span className="col-span-3 text-sm font-mono text-slate-900">{order.id}</span>
          </div>
          
          <div className="grid grid-cols-4 items-center gap-4">
            <span className="text-sm font-medium text-slate-500">Customer:</span>
            <span className="col-span-3 text-sm text-slate-900">{order.customerId}</span>
          </div>
          
          <div className="grid grid-cols-4 items-center gap-4">
            <span className="text-sm font-medium text-slate-500">Date:</span>
            <span className="col-span-3 text-sm text-slate-900">{order.date}</span>
          </div>
          
          <div className="grid gap-4">
            <span className="text-sm font-medium text-slate-500">Items:</span>
            {order.orderItems && order.orderItems.length > 0 ? (
              <div className="space-y-3">
                {order.orderItems.map((item) => (
                  <div key={item.id} className="flex items-center gap-3 p-3 border rounded-lg">
                    {item.product?.imageUrl ? (
                      <img 
                        src={item.product.imageUrl} 
                        alt={item.product.name}
                        className="w-12 h-12 object-cover rounded-md"
                      />
                    ) : (
                      <div className="w-12 h-12 bg-gray-200 rounded-md flex items-center justify-center">
                        <span className="text-gray-400 text-xs">No Image</span>
                      </div>
                    )}
                    <div className="flex-1">
                      <h4 className="text-sm font-medium text-slate-900">
                        {item.product?.name || 'Unknown Product'}
                        {item.product?.model && <span className="text-slate-500 font-normal"> ({item.product.model})</span>}
                      </h4>
                      {item.product?.description && (
                        <p className="text-xs text-slate-600 mt-1 mb-2">
                          {item.product.description}
                        </p>
                      )}
                      <div className="text-xs text-slate-500 space-y-1">
                        {item.product?.brand && <div>Brand: {item.product.brand}</div>}
                        {item.selectedColor && <div>Color: {item.selectedColor}</div>}
                        {item.selectedSize && <div>Size: {item.selectedSize}</div>}
                        <div>Quantity: {item.quantity}</div>
                        <div>Price: ${item.price.toFixed(2)} each</div>
                        {item.product?.specifications && (() => {
                          try {
                            const specs = JSON.parse(item.product.specifications);
                            return (
                              <div className="mt-2">
                                <div className="font-medium mb-1">Specifications:</div>
                                {Object.entries(specs).map(([key, value]) => (
                                  <div key={key} className="text-xs">
                                    <span className="capitalize">{key}:</span> {String(value)}
                                  </div>
                                ))}
                              </div>
                            );
                          } catch {
                            return null;
                          }
                        })()}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-slate-900">
                        ${(item.price * item.quantity).toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <span className="col-span-3 text-sm text-slate-900">{order.items}</span>
            )}
          </div>
          
          <div className="grid grid-cols-4 items-center gap-4">
            <span className="text-sm font-medium text-slate-500">Amount:</span>
            <span className="col-span-3 text-sm font-semibold text-slate-900">
              ${order.amount.toFixed(2)}
            </span>
          </div>
          
          <div className="grid grid-cols-4 items-center gap-4">
            <span className="text-sm font-medium text-slate-500">Status:</span>
            <div className="col-span-3">
              <Badge className={getStatusColor(order.status)}>
                {order.status}
              </Badge>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default OrderViewDialog;