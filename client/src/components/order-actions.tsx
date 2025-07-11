import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogTrigger 
} from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';

interface Order {
  id: string;
  customerId: string;
  date: string;
  items: string;
  amount: number;
  status: string;
  canReturn?: boolean;
  canCancel?: boolean;
  paymentMethod?: string;
  giftCardCode?: string;
}

interface OrderActionsProps {
  order: Order;
  customerId: string;
}

export function OrderActions({ order, customerId }: OrderActionsProps) {
  const [returnReason, setReturnReason] = useState('');
  const [isReturnDialogOpen, setIsReturnDialogOpen] = useState(false);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const returnOrderMutation = useMutation({
    mutationFn: async ({ orderId, returnReason }: { orderId: string; returnReason: string }) => {
      return await apiRequest('PATCH', `/api/orders/${orderId}/return`, { returnReason });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/api/customers/${customerId}/orders`] });
      toast({
        title: "Order returned successfully",
        description: "Your order return has been processed.",
      });
      setIsReturnDialogOpen(false);
      setReturnReason('');
    },
    onError: (error: any) => {
      toast({
        title: "Failed to return order",
        description: error.message || "Please try again later.",
        variant: "destructive",
      });
    }
  });

  const cancelOrderMutation = useMutation({
    mutationFn: async (orderId: string) => {
      return await apiRequest('PATCH', `/api/orders/${orderId}/cancel`, {});
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [`/api/customers/${customerId}/orders`] });
      toast({
        title: "Order cancelled successfully",
        description: "Your order has been cancelled.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to cancel order",
        description: error.message || "Please try again later.",
        variant: "destructive",
      });
    }
  });

  const handleReturnOrder = () => {
    if (!returnReason.trim()) {
      toast({
        title: "Return reason required",
        description: "Please provide a reason for returning this order.",
        variant: "destructive",
      });
      return;
    }
    returnOrderMutation.mutate({ orderId: order.id, returnReason });
  };

  const handleCancelOrder = () => {
    if (window.confirm('Are you sure you want to cancel this order?')) {
      cancelOrderMutation.mutate(order.id);
    }
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'Delivered': return 'default';
      case 'Processing': return 'secondary';
      case 'Shipped': return 'outline';
      case 'Cancelled': return 'destructive';
      case 'Returned': return 'destructive';
      default: return 'secondary';
    }
  };

  return (
    <div className="flex items-center gap-2">
      <Badge variant={getStatusBadgeVariant(order.status)}>
        {order.status}
      </Badge>
      
      {order.giftCardCode && (
        <Badge variant="secondary" className="bg-purple-100 text-purple-800">
          Gift Card: {order.giftCardCode}
        </Badge>
      )}

      {order.canReturn && (
        <Dialog open={isReturnDialogOpen} onOpenChange={setIsReturnDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              Return Order
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Return Order {order.id}</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="returnReason">Return Reason</Label>
                <Textarea
                  id="returnReason"
                  placeholder="Please explain why you're returning this order..."
                  value={returnReason}
                  onChange={(e) => setReturnReason(e.target.value)}
                  className="min-h-[100px]"
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => setIsReturnDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={handleReturnOrder}
                  disabled={returnOrderMutation.isPending}
                >
                  {returnOrderMutation.isPending ? 'Processing...' : 'Return Order'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {order.canCancel && (
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleCancelOrder}
          disabled={cancelOrderMutation.isPending}
        >
          {cancelOrderMutation.isPending ? 'Cancelling...' : 'Cancel Order'}
        </Button>
      )}
    </div>
  );
}