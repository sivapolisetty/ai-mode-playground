import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useLocation } from 'wouter';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/hooks/use-toast';
import { apiRequest, queryClient } from '@/lib/queryClient';
import CartPage from './cart';
import FAQPage from './faq';
import BusinessRulesComponent from '@/components/business-rules';
import { OrderActions } from '@/components/order-actions';
import { ProductConfiguration } from '@/components/product-configuration';

const Home: React.FC = () => {
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>('CUST-001');
  const [activeView, setActiveView] = useState<'home' | 'products' | 'orders' | 'profile' | 'cart' | 'faq' | 'rules'>('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [cartItems, setCartItems] = useState<any[]>([]);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [editingAddressId, setEditingAddressId] = useState<number | null>(null);
  const [, navigate] = useLocation();
  const { toast } = useToast();

  // Check for customer ID in URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const customerIdFromUrl = urlParams.get('customerId');
    if (customerIdFromUrl) {
      setSelectedCustomerId(customerIdFromUrl);
      // Clean up URL
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, []);
  
  const [profileFormData, setProfileFormData] = useState({
    name: '',
    email: '',
    phone: '',
    dob: '',
    address: '',
    accountType: ''
  });

  const [addressFormData, setAddressFormData] = useState({
    label: '',
    recipientName: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'USA',
    phone: '',
    isDefault: false
  });
  
  // Fetch ecommerce data
  const { data: categories = [] } = useQuery({
    queryKey: ['/api/categories']
  });
  
  const { data: products = [] } = useQuery({
    queryKey: ['/api/products']
  });
  
  const { data: customers = [] } = useQuery({
    queryKey: ['/api/customers']
  });
  
  const { data: currentCustomer } = useQuery({
    queryKey: ['/api/customers', selectedCustomerId],
    enabled: !!selectedCustomerId
  });
  
  const { data: customerOrders = [] } = useQuery({
    queryKey: [`/api/customers/${selectedCustomerId}/orders`],
    enabled: !!selectedCustomerId && activeView === 'orders'
  });

  const { data: customerAddresses = [] } = useQuery({
    queryKey: [`/api/customers/${selectedCustomerId}/addresses`],
    enabled: !!selectedCustomerId && activeView === 'profile'
  });

  // Add to cart function
  const addToCart = async (product: any) => {
    try {
      // Call the backend API to add item to cart
      await apiRequest('POST', `/api/customers/${selectedCustomerId}/cart`, {
        productId: product.id,
        quantity: 1,
        selectedColor: product.color || null,
        selectedSize: product.size || null
      });

      // Update local state after successful API call
      setCartItems(prev => {
        const existingItem = prev.find(item => item.id === product.id);
        if (existingItem) {
          return prev.map(item =>
            item.id === product.id 
              ? { ...item, quantity: item.quantity + 1 }
              : item
          );
        }
        return [...prev, { ...product, quantity: 1 }];
      });
      
      toast({
        title: "Added to cart",
        description: `${product.name} has been added to your cart.`,
      });
    } catch (error) {
      console.error('Failed to add item to cart:', error);
      toast({
        title: "Error",
        description: "Failed to add item to cart. Please try again.",
        variant: "destructive"
      });
    }
  };

  // Load cart items from database
  const loadCartItems = async (customerId: string) => {
    try {
      const response = await apiRequest('GET', `/api/customers/${customerId}/cart`);
      const cartData = await response.json();
      // Transform cart data to match the local cart format
      const transformedCart = cartData.map((item: any) => ({
        id: item.product.id,
        cartItemId: item.id, // Add cart item ID for backend operations
        name: item.product.name,
        price: item.product.price,
        imageUrl: item.product.imageUrl,
        brand: item.product.brand,
        color: item.selectedColor || item.product.color,
        size: item.selectedSize || item.product.size,
        quantity: item.quantity
      }));
      setCartItems(transformedCart);
    } catch (error) {
      console.error('Failed to load cart items:', error);
      setCartItems([]); // Clear cart on error
    }
  };

  // Handle user switch - load cart for new user
  const handleUserSwitch = (userId: string) => {
    setSelectedCustomerId(userId);
    loadCartItems(userId); // Load cart for the new user
    toast({
      title: "User switched",
      description: "Loading cart for the new user.",
    });
  };

  // Get current customer info
  const customer = Array.isArray(customers) ? customers.find((c: any) => c.id === selectedCustomerId) : null;

  // Load cart items when customer changes
  React.useEffect(() => {
    if (selectedCustomerId) {
      loadCartItems(selectedCustomerId);
    }
  }, [selectedCustomerId]);

  // Profile editing functions
  React.useEffect(() => {
    if (customer && isEditingProfile) {
      setProfileFormData({
        name: customer.name,
        email: customer.email,
        phone: customer.phone,
        dob: customer.dob,
        address: customer.address,
        accountType: customer.accountType || ''
      });
    }
  }, [customer, isEditingProfile]);

  const handleProfileInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setProfileFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveProfile = async () => {
    try {
      await apiRequest('PATCH', `/api/customers/${selectedCustomerId}`, profileFormData);
      queryClient.invalidateQueries({ queryKey: ['/api/customers', selectedCustomerId] });
      toast({
        title: "Success",
        description: "Profile updated successfully",
      });
      setIsEditingProfile(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive"
      });
    }
  };

  // Address management functions
  const formatAddress = (address: any) => {
    const parts = [
      address.addressLine1,
      address.addressLine2,
      `${address.city}, ${address.state} ${address.zipCode}`,
      address.country !== 'USA' ? address.country : ''
    ].filter(Boolean);
    return parts.join(', ');
  };

  const handleAddressInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setAddressFormData(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value 
    }));
  };

  const resetAddressForm = () => {
    setAddressFormData({
      label: '',
      recipientName: '',
      addressLine1: '',
      addressLine2: '',
      city: '',
      state: '',
      zipCode: '',
      country: 'USA',
      phone: '',
      isDefault: false
    });
    setEditingAddressId(null);
    setShowAddressForm(false);
  };

  const handleAddAddress = () => {
    if (customer) {
      setAddressFormData({
        ...addressFormData,
        recipientName: customer.name,
        phone: customer.phone
      });
    }
    setShowAddressForm(true);
  };

  const handleEditAddress = (address: any) => {
    setAddressFormData({
      label: address.label,
      recipientName: address.recipientName,
      addressLine1: address.addressLine1,
      addressLine2: address.addressLine2 || '',
      city: address.city,
      state: address.state,
      zipCode: address.zipCode,
      country: address.country,
      phone: address.phone || '',
      isDefault: address.isDefault
    });
    setEditingAddressId(address.id);
    setShowAddressForm(true);
  };

  const handleSaveAddress = async () => {
    try {
      const addressData = {
        ...addressFormData,
        customerId: selectedCustomerId,
        isActive: true,
        createdDate: new Date().toISOString()
      };

      if (editingAddressId) {
        await apiRequest('PUT', `/api/admin/customerAddresses/${editingAddressId}`, addressData);
        toast({
          title: "Success",
          description: "Address updated successfully",
        });
      } else {
        await apiRequest('POST', `/api/customers/${selectedCustomerId}/addresses`, addressData);
        toast({
          title: "Success",
          description: "Address added successfully",
        });
      }

      queryClient.invalidateQueries({ queryKey: [`/api/customers/${selectedCustomerId}/addresses`] });
      resetAddressForm();
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${editingAddressId ? 'update' : 'add'} address`,
        variant: "destructive"
      });
    }
  };

  const handleDeleteAddress = async (addressId: number) => {
    if (!confirm('Are you sure you want to delete this address?')) return;

    try {
      await apiRequest('DELETE', `/api/admin/customerAddresses/${addressId}`);
      toast({
        title: "Success",
        description: "Address deleted successfully",
      });
      queryClient.invalidateQueries({ queryKey: [`/api/customers/${selectedCustomerId}/addresses`] });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete address",
        variant: "destructive"
      });
    }
  };

  const handleSetDefaultAddress = async (addressId: number) => {
    try {
      await apiRequest('PUT', `/api/customers/${selectedCustomerId}/addresses/${addressId}/default`);
      toast({
        title: "Success",
        description: "Default address updated successfully",
      });
      queryClient.invalidateQueries({ queryKey: [`/api/customers/${selectedCustomerId}/addresses`] });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to set default address",
        variant: "destructive"
      });
    }
  };

  // Filter products based on search and category
  const filteredProducts = Array.isArray(products) ? products.filter((product: any) => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.brand?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.categoryId.toString() === selectedCategory;
    return matchesSearch && matchesCategory;
  }) : [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <nav className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <i className="ri-shopping-bag-fill text-white text-lg"></i>
                </div>
                <h1 className="ml-2 text-xl font-bold text-gray-900">ShopHub</h1>
              </div>
            </div>

            {/* Navigation Links */}
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <button
                  onClick={() => setActiveView('home')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeView === 'home' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Home
                </button>
                <button
                  onClick={() => setActiveView('products')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeView === 'products' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Products
                </button>
                <button
                  onClick={() => setActiveView('orders')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeView === 'orders' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  My Orders
                </button>
                <button
                  onClick={() => setActiveView('profile')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeView === 'profile' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Profile
                </button>
                <button
                  onClick={() => setActiveView('faq')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeView === 'faq' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  FAQ
                </button>
                <button
                  onClick={() => setActiveView('rules')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    activeView === 'rules' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Rules
                </button>
              </div>
            </div>

            {/* User Switcher */}
            <div className="flex items-center space-x-4">
              <Select value={selectedCustomerId} onValueChange={handleUserSwitch}>
                <SelectTrigger className="w-48">
                  <div className="flex items-center space-x-2">
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="text-xs">
                        {customer?.name?.split(' ').map((n: string) => n[0]).join('') || 'U'}
                      </AvatarFallback>
                    </Avatar>
                    <span className="truncate">{customer?.name || 'Select User'}</span>
                  </div>
                </SelectTrigger>
                <SelectContent>
                  {Array.isArray(customers) && customers.map((cust: any) => (
                    <SelectItem key={cust.id} value={cust.id}>
                      <div className="flex items-center space-x-2">
                        <Avatar className="h-6 w-6">
                          <AvatarFallback className="text-xs">
                            {cust.name.split(' ').map((n: string) => n[0]).join('')}
                          </AvatarFallback>
                        </Avatar>
                        <span>{cust.name}</span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <Button size="sm" variant="outline" onClick={() => setActiveView('cart')}>
                <i className="ri-shopping-cart-line mr-1"></i>
                Cart ({cartItems.length})
              </Button>
              
              <Button size="sm" variant="outline" onClick={() => navigate('/admin')}>
                <i className="ri-settings-line mr-1"></i>
                Admin
              </Button>
              
              <Button 
                size="sm" 
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700"
                onClick={() => navigate(`/intelligent-ui?customerId=${selectedCustomerId}`)}
              >
                <i className="ri-robot-line mr-1"></i>
                AI Assistant
              </Button>
              
              <Button 
                size="sm" 
                variant="outline"
                className="border-purple-300 text-purple-700 hover:bg-purple-50"
                onClick={() => navigate('/ui-test')}
              >
                <i className="ri-test-tube-line mr-1"></i>
                UI Test
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Home Page */}
        {activeView === 'home' && (
          <div className="space-y-8">
            {/* Welcome Banner */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-6 text-white">
              <h1 className="text-3xl font-bold mb-2">Welcome to ShopHub, {customer?.name || 'Guest'}!</h1>
              <p className="text-blue-100">Discover amazing products and great deals</p>
            </div>

            {/* Featured Categories */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Shop by Category</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Array.isArray(categories) && categories.map((category: any) => (
                  <Card key={category.id} className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => {
                    setSelectedCategory(category.id.toString());
                    setActiveView('products');
                  }}>
                    <CardContent className="p-6">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                          <i className={`ri-${category.name.toLowerCase() === 'electronics' ? 'smartphone' : category.name.toLowerCase() === 'clothing' ? 'shirt' : 'footprints'}-line text-blue-600 text-xl`}></i>
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold">{category.name}</h3>
                          <p className="text-gray-500 text-sm">{category.description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>

            {/* Featured Products */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Featured Products</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {Array.isArray(products) && products.slice(0, 8).map((product: any) => (
                  <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                    <div className="aspect-w-1 aspect-h-1">
                      <img 
                        src={product.imageUrl || '/placeholder-product.jpg'} 
                        alt={product.name}
                        className="w-full h-48 object-cover"
                      />
                    </div>
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-gray-900 mb-1">{product.name}</h3>
                      <p className="text-gray-500 text-sm mb-2">{product.brand}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-xl font-bold text-blue-600">${product.price}</span>
                        <Button size="sm" onClick={() => addToCart(product)}>Add to Cart</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          </div>
        )}

        {/* Products Page */}
        {activeView === 'products' && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Products</h1>
              <p className="text-gray-600">Browse our complete product catalog</p>
            </div>

            {/* Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {Array.isArray(categories) && categories.map((category: any) => (
                    <SelectItem key={category.id} value={category.id.toString()}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Products Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredProducts.map((product: any) => (
                <Card key={product.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                  <div className="aspect-w-1 aspect-h-1">
                    <img 
                      src={product.imageUrl || '/placeholder-product.jpg'} 
                      alt={product.name}
                      className="w-full h-48 object-cover"
                    />
                  </div>
                  <CardContent className="p-4">
                    <h3 className="font-semibold text-gray-900 mb-1">{product.name}</h3>
                    <p className="text-gray-500 text-sm mb-2">{product.brand}</p>
                    <p className="text-gray-600 text-xs mb-3 line-clamp-2">{product.description}</p>
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-xl font-bold text-blue-600">${product.price}</span>
                      <Badge variant={product.stockQuantity > 0 ? "default" : "destructive"}>
                        {product.stockQuantity > 0 ? "In Stock" : "Out of Stock"}
                      </Badge>
                    </div>
                    <Button 
                      className="w-full" 
                      disabled={product.stockQuantity === 0}
                      onClick={() => addToCart(product)}
                    >
                      <i className="ri-shopping-cart-line mr-2"></i>
                      Add to Cart
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* Orders Page */}
        {activeView === 'orders' && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Orders</h1>
              <p className="text-gray-600">Track your order history and status</p>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Order History</CardTitle>
                <CardDescription>Your recent orders and their status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Array.isArray(customerOrders) && customerOrders.length > 0 ? (
                    customerOrders.map((order: any) => (
                      <div key={order.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <h3 className="font-semibold">Order #{order.id}</h3>
                            <p className="text-sm text-gray-500">{new Date(order.orderDate).toLocaleDateString()}</p>
                          </div>
                          <OrderActions 
                            order={{
                              id: order.id,
                              customerId: order.customerId,
                              date: order.orderDate,
                              items: `${order.orderItems?.length || 0} items`,
                              amount: order.totalAmount,
                              status: order.status,
                              canReturn: order.canReturn,
                              canCancel: order.canCancel,
                              paymentMethod: order.paymentMethod,
                              giftCardCode: order.giftCardCode
                            }}
                            customerId={selectedCustomerId}
                          />
                        </div>
                        
                        {/* Product Items Display */}
                        {order.orderItems && order.orderItems.length > 0 && (
                          <div className="mb-4">
                            <h4 className="text-sm font-medium text-gray-700 mb-3">Items Ordered:</h4>
                            <div className="space-y-3">
                              {order.orderItems.map((item: any) => (
                                <div key={item.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                                  {/* Product Image */}
                                  {item.product?.imageUrl ? (
                                    <img 
                                      src={item.product.imageUrl} 
                                      alt={item.product.name}
                                      className="w-16 h-16 object-cover rounded-md border"
                                    />
                                  ) : (
                                    <div className="w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center border">
                                      <span className="text-gray-400 text-xs">No Image</span>
                                    </div>
                                  )}
                                  
                                  {/* Product Details */}
                                  <div className="flex-1">
                                    <h5 className="font-medium text-gray-900">
                                      {item.product?.name || 'Unknown Product'}
                                      {item.product?.model && <span className="text-gray-500 font-normal"> ({item.product.model})</span>}
                                    </h5>
                                    {item.product?.description && (
                                      <p className="text-sm text-gray-600 mt-1">
                                        {item.product.description}
                                      </p>
                                    )}
                                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                                      {item.product?.brand && <span>Brand: {item.product.brand}</span>}
                                      {item.selectedColor && <span>Color: {item.selectedColor}</span>}
                                      {item.selectedSize && <span>Size: {item.selectedSize}</span>}
                                      <span>Qty: {item.quantity}</span>
                                      <span className="font-medium">${item.price.toFixed(2)} each</span>
                                    </div>
                                  </div>
                                  
                                  {/* Item Total */}
                                  <div className="text-right">
                                    <div className="font-medium text-gray-900">
                                      ${(item.price * item.quantity).toFixed(2)}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        <div className="flex justify-between items-center pt-3 border-t">
                          <p className="text-sm text-gray-500">Shipping to: {order.shippingAddress}</p>
                          <p className="text-lg font-semibold text-gray-900">Total: ${order.totalAmount.toFixed(2)}</p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <i className="ri-shopping-bag-line text-4xl text-gray-300 mb-4"></i>
                      <p className="text-gray-500">No orders found</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Profile Page */}
        {activeView === 'profile' && customer && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
                <p className="text-gray-600">Manage your account information</p>
              </div>
              <Button
                onClick={() => setIsEditingProfile(!isEditingProfile)}
                variant={isEditingProfile ? "outline" : "default"}
              >
                <i className={`${isEditingProfile ? 'ri-eye-line' : 'ri-edit-line'} mr-2`}></i>
                {isEditingProfile ? 'View' : 'Edit Profile'}
              </Button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {!isEditingProfile ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Full Name</label>
                        <p className="text-gray-900">{customer.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <p className="text-gray-900">{customer.email}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Phone</label>
                        <p className="text-gray-900">{customer.phone}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Date of Birth</label>
                        <p className="text-gray-900">{new Date(customer.dob).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Full Name</label>
                        <Input
                          name="name"
                          value={profileFormData.name}
                          onChange={handleProfileInputChange}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <Input
                          name="email"
                          type="email"
                          value={profileFormData.email}
                          onChange={handleProfileInputChange}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Phone</label>
                        <Input
                          name="phone"
                          type="tel"
                          value={profileFormData.phone}
                          onChange={handleProfileInputChange}
                          className="mt-1"
                        />
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Date of Birth</label>
                        <Input
                          name="dob"
                          value={profileFormData.dob}
                          onChange={handleProfileInputChange}
                          className="mt-1"
                        />
                      </div>
                    </div>
                  )}
                  
                  {isEditingProfile && (
                    <div className="flex justify-end space-x-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => setIsEditingProfile(false)}
                      >
                        Cancel
                      </Button>
                      <Button onClick={handleSaveProfile}>
                        Save Changes
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Account Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Status</label>
                    <div className="mt-1">
                      <Badge variant={customer.status === 'active' ? 'default' : 'secondary'}>
                        {customer.status}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Member Since</label>
                    <p className="text-gray-900">{new Date(customer.registrationDate).toLocaleDateString()}</p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Addresses Section */}
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <CardTitle>Addresses</CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleAddAddress}
                  >
                    <i className="ri-add-line mr-2"></i>
                    Add Address
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {Array.isArray(customerAddresses) && customerAddresses.length > 0 ? (
                  <div className="space-y-4">
                    {customerAddresses.map((address: any) => (
                      <div key={address.id} className="border rounded-lg p-4 bg-slate-50">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="font-medium text-gray-900">{address.label}</span>
                              {address.isDefault && (
                                <Badge variant="default" className="text-xs">
                                  Default
                                </Badge>
                              )}
                            </div>
                            <div className="text-sm text-gray-700 mb-1">{address.recipientName}</div>
                            <div className="text-sm text-gray-600">{formatAddress(address)}</div>
                            {address.phone && (
                              <div className="text-sm text-gray-600 mt-1">Phone: {address.phone}</div>
                            )}
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            {!address.isDefault && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => handleSetDefaultAddress(address.id)}
                                className="text-xs"
                              >
                                Set Default
                              </Button>
                            )}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditAddress(address)}
                              className="text-xs"
                            >
                              <i className="ri-edit-line"></i>
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteAddress(address.id)}
                              className="text-xs text-red-600 hover:text-red-700"
                            >
                              <i className="ri-delete-bin-line"></i>
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <i className="ri-map-pin-line text-4xl mb-4"></i>
                    <p>No addresses found</p>
                    <Button
                      variant="outline"
                      onClick={handleAddAddress}
                      className="mt-4"
                    >
                      Add Your First Address
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Cart View */}
        {activeView === 'cart' && (
          <CartPage 
            cartItems={cartItems}
            setCartItems={setCartItems}
            onBackToHome={() => setActiveView('home')}
            onSwitchToOrders={() => setActiveView('orders')}
            selectedCustomerId={selectedCustomerId}
            customer={customer}
          />
        )}

        {/* FAQ View */}
        {activeView === 'faq' && (
          <FAQPage />
        )}

        {/* Business Rules View */}
        {activeView === 'rules' && (
          <BusinessRulesComponent />
        )}
      </main>

      {/* Address Form Modal */}
      {showAddressForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingAddressId ? 'Edit Address' : 'Add New Address'}
              </h3>
            </div>
            
            <div className="px-6 py-4">
              <form className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="sm:col-span-1">
                  <label htmlFor="label" className="block text-sm font-medium text-gray-700">
                    Address Label
                  </label>
                  <Input
                    type="text"
                    name="label"
                    id="label"
                    placeholder="e.g., Home, Work, Billing"
                    value={addressFormData.label}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="recipientName" className="block text-sm font-medium text-gray-700">
                    Recipient Name
                  </label>
                  <Input
                    type="text"
                    name="recipientName"
                    id="recipientName"
                    value={addressFormData.recipientName}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-2">
                  <label htmlFor="addressLine1" className="block text-sm font-medium text-gray-700">
                    Address Line 1
                  </label>
                  <Input
                    type="text"
                    name="addressLine1"
                    id="addressLine1"
                    placeholder="Street address"
                    value={addressFormData.addressLine1}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-2">
                  <label htmlFor="addressLine2" className="block text-sm font-medium text-gray-700">
                    Address Line 2 (Optional)
                  </label>
                  <Input
                    type="text"
                    name="addressLine2"
                    id="addressLine2"
                    placeholder="Apt, suite, unit, building, floor, etc."
                    value={addressFormData.addressLine2}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="city" className="block text-sm font-medium text-gray-700">
                    City
                  </label>
                  <Input
                    type="text"
                    name="city"
                    id="city"
                    value={addressFormData.city}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="state" className="block text-sm font-medium text-gray-700">
                    State
                  </label>
                  <Input
                    type="text"
                    name="state"
                    id="state"
                    value={addressFormData.state}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="zipCode" className="block text-sm font-medium text-gray-700">
                    ZIP Code
                  </label>
                  <Input
                    type="text"
                    name="zipCode"
                    id="zipCode"
                    value={addressFormData.zipCode}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="country" className="block text-sm font-medium text-gray-700">
                    Country
                  </label>
                  <Input
                    type="text"
                    name="country"
                    id="country"
                    value={addressFormData.country}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                    Phone (Optional)
                  </label>
                  <Input
                    type="tel"
                    name="phone"
                    id="phone"
                    value={addressFormData.phone}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1 flex items-center mt-6">
                  <input
                    type="checkbox"
                    name="isDefault"
                    id="isDefault"
                    checked={addressFormData.isDefault}
                    onChange={handleAddressInputChange}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="isDefault" className="ml-2 block text-sm text-gray-700">
                    Set as default address
                  </label>
                </div>
              </form>
            </div>
            
            <div className="px-6 py-4 border-t flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={resetAddressForm}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleSaveAddress}
              >
                {editingAddressId ? 'Update Address' : 'Add Address'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
