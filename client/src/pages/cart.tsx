import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/hooks/use-toast';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { GiftCardPayment } from '@/components/gift-card-payment';
import { AddressSelector } from '@/components/address-selector';
import { useState } from 'react';

interface CartItem {
  id: string;
  cartItemId?: number; // Add cart item ID for backend operations
  name: string;
  price: number;
  quantity: number;
  imageUrl: string;
  brand: string;
}

interface CartPageProps {
  cartItems: CartItem[];
  setCartItems: (items: CartItem[]) => void;
  onBackToHome: () => void;
  onSwitchToOrders: () => void;
  selectedCustomerId: string;
  customer: any;
}

export default function CartPage({ cartItems, setCartItems, onBackToHome, onSwitchToOrders, selectedCustomerId, customer }: CartPageProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [appliedGiftCard, setAppliedGiftCard] = useState<{
    code: string;
    discountAmount: number;
  } | undefined>();
  const [selectedAddress, setSelectedAddress] = useState<any>(null);

  const placeOrderMutation = useMutation({
    mutationFn: async (orderData: any) => {
      return await apiRequest('POST', '/api/orders', orderData);
    },
    onSuccess: async () => {
      // Invalidate all related queries to refresh data
      queryClient.invalidateQueries({ queryKey: [`/api/customers/${selectedCustomerId}/orders`] });
      queryClient.invalidateQueries({ queryKey: ['/api/customers', selectedCustomerId] });
      queryClient.invalidateQueries({ queryKey: ['/api/customers'] });
      
      // Clear cart from database after successful order
      try {
        await apiRequest('DELETE', `/api/customers/${selectedCustomerId}/cart`);
      } catch (error) {
        console.error('Failed to clear cart after order:', error);
      }
      
      setCartItems([]);
      toast({
        title: "Order placed successfully!",
        description: "Your order has been placed and you will receive a confirmation email shortly.",
      });
      
      // Switch to orders view to show the new order
      setTimeout(() => {
        onSwitchToOrders();
      }, 1000);
    },
    onError: (error: any) => {
      console.error('Order placement error:', error);
      toast({
        title: "Order failed",
        description: `Error: ${error.message || 'Please try again.'}`,
        variant: "destructive",
      });
    },
  });

  const handlePlaceOrder = () => {
    if (!customer || cartItems.length === 0 || !selectedAddress) {
      toast({
        title: "Missing Information",
        description: "Please select a delivery address to continue.",
        variant: "destructive"
      });
      return;
    }

    // Format address for shipping
    const formattedAddress = [
      selectedAddress.addressLine1,
      selectedAddress.addressLine2,
      `${selectedAddress.city}, ${selectedAddress.state} ${selectedAddress.zipCode}`,
      selectedAddress.country !== 'USA' ? selectedAddress.country : ''
    ].filter(Boolean).join(', ');

    const orderData = {
      customerId: selectedCustomerId,
      orderDate: new Date().toISOString().split('T')[0],
      totalAmount: total,
      status: "Processing",
      shippingAddress: formattedAddress,
      paymentMethod: appliedGiftCard ? "Gift Card" : "Credit Card",
      giftCardCode: appliedGiftCard?.code,
      items: cartItems.map(item => ({
        productId: item.id,
        quantity: item.quantity,
        price: item.price
      }))
    };

    placeOrderMutation.mutate(orderData);
  };

  const updateQuantity = async (id: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeItem(id);
      return;
    }
    
    const cartItem = cartItems.find(item => item.id === id);
    if (!cartItem?.cartItemId) {
      // Fallback to local state update if no cart item ID
      setCartItems(cartItems.map(item =>
        item.id === id ? { ...item, quantity: newQuantity } : item
      ));
      return;
    }

    try {
      // Update quantity in database
      await apiRequest('PATCH', `/api/cart/${cartItem.cartItemId}`, { quantity: newQuantity });

      // Update local state after successful API call
      setCartItems(cartItems.map(item =>
        item.id === id ? { ...item, quantity: newQuantity } : item
      ));
    } catch (error) {
      console.error('Failed to update cart item:', error);
      toast({
        title: "Error",
        description: "Failed to update item quantity. Please try again.",
        variant: "destructive"
      });
    }
  };

  const removeItem = async (id: string) => {
    const cartItem = cartItems.find(item => item.id === id);
    if (!cartItem?.cartItemId) {
      // Fallback to local state update if no cart item ID
      setCartItems(cartItems.filter(item => item.id !== id));
      toast({
        title: "Item removed",
        description: "Item has been removed from your cart.",
      });
      return;
    }

    try {
      // Remove item from database
      await apiRequest('DELETE', `/api/cart/${cartItem.cartItemId}`);

      // Update local state after successful API call
      setCartItems(cartItems.filter(item => item.id !== id));
      toast({
        title: "Item removed",
        description: "Item has been removed from your cart.",
      });
    } catch (error) {
      console.error('Failed to remove cart item:', error);
      toast({
        title: "Error",
        description: "Failed to remove item from cart. Please try again.",
        variant: "destructive"
      });
    }
  };

  const clearCart = async () => {
    try {
      // Clear cart from database
      await apiRequest('DELETE', `/api/customers/${selectedCustomerId}/cart`);

      // Update local state after successful API call
      setCartItems([]);
      toast({
        title: "Cart cleared",
        description: "All items have been removed from your cart.",
      });
    } catch (error) {
      console.error('Failed to clear cart:', error);
      toast({
        title: "Error",
        description: "Failed to clear cart. Please try again.",
        variant: "destructive"
      });
    }
  };

  const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const tax = subtotal * 0.08; // 8% tax
  const shipping = subtotal > 50 ? 0 : 9.99; // Free shipping over $50
  const giftCardDiscount = appliedGiftCard?.discountAmount || 0;
  const total = Math.max(0, subtotal + tax + shipping - giftCardDiscount);

  if (cartItems.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">Shopping Cart</h1>
          <Button variant="outline" onClick={onBackToHome}>
            <i className="ri-arrow-left-line mr-2"></i>
            Continue Shopping
          </Button>
        </div>

        <Card className="text-center py-12">
          <CardContent>
            <div className="mb-6">
              <i className="ri-shopping-cart-line text-6xl text-gray-300 mb-4 block"></i>
              <h2 className="text-2xl font-semibold mb-2">Your cart is empty</h2>
              <p className="text-gray-500">Add some items to get started</p>
            </div>
            <Button onClick={onBackToHome}>
              <i className="ri-shopping-bag-line mr-2"></i>
              Start Shopping
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Shopping Cart</h1>
        <Button variant="outline" onClick={onBackToHome}>
          <i className="ri-arrow-left-line mr-2"></i>
          Continue Shopping
        </Button>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Cart Items ({cartItems.length})</CardTitle>
              <Button variant="outline" size="sm" onClick={clearCart}>
                <i className="ri-delete-bin-line mr-2"></i>
                Clear Cart
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {cartItems.map((item) => (
                <div key={item.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                  <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                    <img 
                      src={item.imageUrl} 
                      alt={item.name}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjQiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA2NCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0IiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0yMCAyMEg0NFY0NEgyMFYyMFoiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHBhdGggZD0iTTI4IDI4TDM2IDM2IiBzdHJva2U9IiM5Q0EzQUYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPgo=';
                      }}
                    />
                  </div>
                  
                  <div className="flex-1">
                    <h3 className="font-semibold">{item.name}</h3>
                    <p className="text-sm text-gray-500">{item.brand}</p>
                    <p className="text-lg font-bold text-blue-600">${item.price}</p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                    >
                      <i className="ri-subtract-line"></i>
                    </Button>
                    <span className="w-8 text-center font-semibold">{item.quantity}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                    >
                      <i className="ri-add-line"></i>
                    </Button>
                  </div>

                  <div className="text-right">
                    <p className="font-bold">${(item.price * item.quantity).toFixed(2)}</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeItem(item.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <i className="ri-delete-bin-line"></i>
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle>Order Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>${subtotal.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between">
                <span>Tax</span>
                <span>${tax.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between">
                <span>Shipping</span>
                <span>
                  {shipping === 0 ? (
                    <Badge variant="secondary">Free</Badge>
                  ) : (
                    `$${shipping.toFixed(2)}`
                  )}
                </span>
              </div>
              
              {giftCardDiscount > 0 && (
                <div className="flex justify-between text-green-600">
                  <span>Gift Card Discount</span>
                  <span>-${giftCardDiscount.toFixed(2)}</span>
                </div>
              )}
              
              {subtotal < 50 && (
                <div className="text-sm text-gray-500">
                  Add ${(50 - subtotal).toFixed(2)} more for free shipping
                </div>
              )}
              
              <Separator />
              
              <div className="flex justify-between text-lg font-bold">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
              
              <GiftCardPayment
                totalAmount={subtotal + tax + shipping}
                onGiftCardApplied={(code, discountAmount) => {
                  setAppliedGiftCard({ code, discountAmount });
                }}
                onRemoveGiftCard={() => {
                  setAppliedGiftCard(undefined);
                }}
                appliedGiftCard={appliedGiftCard}
              />

              {customer && (
                <AddressSelector 
                  customerId={selectedCustomerId}
                  selectedAddressId={selectedAddress?.id}
                  onAddressSelect={setSelectedAddress}
                />
              )}
              
              <Button 
                className="w-full" 
                size="lg"
                onClick={handlePlaceOrder}
                disabled={placeOrderMutation.isPending || cartItems.length === 0}
              >
                <i className="ri-secure-payment-line mr-2"></i>
                {placeOrderMutation.isPending ? 'Placing Order...' : 'Place Order'}
              </Button>
              
              <div className="text-center text-sm text-gray-500">
                Secure checkout with SSL encryption
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}