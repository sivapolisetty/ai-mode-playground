import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import OrderViewDialog from './order-view-dialog';
import CreateOrderDialog from './create-order-dialog';

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

interface OrdersTabProps {
  customerId: string;
  orders?: Order[];
}

const OrdersTab: React.FC<OrdersTabProps> = ({ customerId, orders = [] }) => {
  const { toast } = useToast();
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [showViewDialog, setShowViewDialog] = useState(false);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const handleCreateOrder = () => {
    setShowCreateDialog(true);
  };

  const handleViewOrder = (orderId: string) => {
    const order = orders.find(o => o.id === orderId);
    if (order) {
      setSelectedOrder(order);
      setShowViewDialog(true);
    } else {
      toast({
        title: "Error",
        description: "Order not found.",
        variant: "destructive"
      });
    }
  };

  return (
    <div className="px-4 py-5 sm:p-6">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <h3 className="text-base font-semibold leading-6 text-slate-900">Order History</h3>
        <Button
          variant="outline"
          onClick={handleCreateOrder}
          className="mt-3 inline-flex items-center text-sm font-medium text-primary sm:mt-0"
        >
          <i className="ri-add-line mr-1"></i> Create Order
        </Button>
      </div>

      <div className="mt-4 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <table className="min-w-full divide-y divide-slate-200">
              <thead>
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900 sm:pl-0">Order ID</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Date</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Items</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Amount</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Status</th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-0">
                    <span className="sr-only">View</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {orders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-4 text-center text-sm text-slate-500">
                      No orders found for this customer.
                    </td>
                  </tr>
                ) : (
                  orders.map((order: any) => (
                    <tr key={order.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-slate-900 sm:pl-0">{order.id}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">{order.date}</td>
                      <td className="px-3 py-4 text-sm text-slate-500">
                        {order.orderItems && order.orderItems.length > 0 ? (
                          <div className="flex items-center gap-3">
                            <div className="flex -space-x-1">
                              {order.orderItems.slice(0, 3).map((item: any) => (
                                <div key={item.id} className="relative">
                                  {item.product?.imageUrl ? (
                                    <img 
                                      src={item.product.imageUrl} 
                                      alt={item.product.name}
                                      className="w-8 h-8 object-cover rounded-full border-2 border-white"
                                    />
                                  ) : (
                                    <div className="w-8 h-8 bg-gray-200 rounded-full border-2 border-white flex items-center justify-center">
                                      <span className="text-gray-400 text-xs">?</span>
                                    </div>
                                  )}
                                </div>
                              ))}
                              {order.orderItems.length > 3 && (
                                <div className="w-8 h-8 bg-slate-100 rounded-full border-2 border-white flex items-center justify-center">
                                  <span className="text-slate-600 text-xs">+{order.orderItems.length - 3}</span>
                                </div>
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="text-xs text-slate-500 mb-1">
                                {order.orderItems.length} item{order.orderItems.length !== 1 ? 's' : ''}
                              </div>
                              {order.orderItems.length > 0 && (
                                <div className="text-xs text-slate-700 truncate max-w-[200px]">
                                  {order.orderItems[0].product?.name}
                                  {order.orderItems[0].product?.description && (
                                    <span className="text-slate-500 ml-1">
                                      - {order.orderItems[0].product.description.substring(0, 50)}
                                      {order.orderItems[0].product.description.length > 50 ? '...' : ''}
                                    </span>
                                  )}
                                  {order.orderItems.length > 1 && (
                                    <span className="text-slate-400"> & {order.orderItems.length - 1} more</span>
                                  )}
                                </div>
                              )}
                            </div>
                          </div>
                        ) : (
                          <span>{order.items}</span>
                        )}
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">${order.amount.toFixed(2)}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          order.status === 'Completed' 
                            ? 'bg-green-50 text-green-700' 
                            : order.status === 'Pending'
                              ? 'bg-yellow-50 text-yellow-700'
                              : 'bg-red-50 text-red-700'
                        }`}>
                          {order.status}
                        </span>
                      </td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                        <Button
                          variant="link"
                          onClick={() => handleViewOrder(order.id)}
                          className="text-primary hover:text-primary-700"
                        >
                          View
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* View Order Dialog */}
      <OrderViewDialog
        order={selectedOrder}
        open={showViewDialog}
        onOpenChange={setShowViewDialog}
      />

      {/* Create Order Dialog */}
      <CreateOrderDialog
        customerId={customerId}
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </div>
  );
};

export default OrdersTab;
