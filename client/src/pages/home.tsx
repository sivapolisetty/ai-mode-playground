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
// Import shared business components
import { ProductCard, ProductList, OrderCard, AddressList, AddressForm } from '@/components/business';

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
                  <ProductCard
                    key={product.id}
                    title={product.name}
                    description={product.description}
                    price={`$${product.price}`}
                    imageUrl={product.imageUrl || '/placeholder-product.jpg'}
                    metadata={{ 
                      brand: product.brand,
                      stock: product.stockQuantity > 0 ? 'In Stock' : 'Out of Stock'
                    }}
                    actions={[
                      {
                        label: 'Add to Cart',
                        action: 'add_to_cart',
                        data: { productId: product.id },
                        variant: product.stockQuantity === 0 ? 'outline' : 'default'
                      }
                    ]}
                    onAction={(action, data) => {
                      if (action === 'add_to_cart') {
                        addToCart(product)
                      }
                    }}
                  />
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
            <ProductList
              products={filteredProducts.map((product: any) => ({
                id: product.id,
                title: product.name,
                description: product.description,
                price: `$${product.price}`,
                imageUrl: product.imageUrl || '/placeholder-product.jpg',
                metadata: { 
                  brand: product.brand,
                  stock: product.stockQuantity > 0 ? 'In Stock' : 'Out of Stock'
                },
                actions: [
                  {
                    label: 'Add to Cart',
                    action: 'add_to_cart',
                    data: { productId: product.id },
                    variant: product.stockQuantity === 0 ? 'outline' : 'default'
                  }
                ]
              }))}
              onAction={(action, data) => {
                if (action === 'add_to_cart') {
                  const product = Array.isArray(products) ? products.find((p: any) => p.id === data?.productId) : null
                  if (product) {
                    addToCart(product)
                  }
                }
              }}
              layout="grid"
            />
          </div>
        )}

        {/* Orders Page */}
        {activeView === 'orders' && (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Orders</h1>
              <p className="text-gray-600">Track your order history and status</p>
            </div>

            {/* Orders List using shared OrderCard component */}
            <div className="space-y-4">
              {Array.isArray(customerOrders) && customerOrders.length > 0 ? (
                customerOrders.map((order: any) => (
                  <OrderCard
                    key={order.id}
                    id={order.id}
                    status={order.status}
                    total={order.totalAmount}
                    createdAt={order.orderDate}
                    trackingNumber={order.trackingNumber}
                    items={order.orderItems?.map((item: any) => ({
                      id: item.id,
                      product_name: item.product?.name || 'Unknown Product',
                      quantity: item.quantity,
                      price: item.price,
                      total: item.price * item.quantity,
                      imageUrl: item.product?.imageUrl || '/placeholder-product.jpg',
                      brand: item.product?.brand
                    })) || []}
                    actions={[
                      {
                        label: 'View Details',
                        action: 'view_order',
                        data: { orderId: order.id },
                        variant: 'outline'
                      },
                      ...(order.canCancel ? [{
                        label: 'Cancel Order',
                        action: 'cancel_order',
                        data: { orderId: order.id },
                        variant: 'destructive' as const
                      }] : []),
                      ...(order.canReturn ? [{
                        label: 'Return Items',
                        action: 'return_order',
                        data: { orderId: order.id },
                        variant: 'outline' as const
                      }] : []),
                      {
                        label: 'Track Order',
                        action: 'track_order',
                        data: { orderId: order.id, trackingNumber: order.trackingNumber },
                        variant: 'default' as const
                      }
                    ]}
                    onAction={(action, data) => {
                      console.log(`Order action: ${action}`, data)
                      // Handle order actions here
                      switch (action) {
                        case 'view_order':
                          // Navigate to order details
                          break
                        case 'cancel_order':
                          // Handle order cancellation
                          break
                        case 'return_order':
                          // Handle return process
                          break
                        case 'track_order':
                          // Open tracking information
                          break
                        default:
                          console.log('Unhandled order action:', action)
                      }
                    }}
                  />
                ))
              ) : (
                <Card className="text-center py-12">
                  <CardContent>
                    <i className="ri-shopping-bag-line text-4xl text-gray-300 mb-4"></i>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No orders found</h3>
                    <p className="text-gray-500 mb-4">You haven't placed any orders yet.</p>
                    <Button onClick={() => setActiveView('products')}>
                      Start Shopping
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>
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

            {/* Addresses Section using shared AddressList component */}
            <AddressList
              addresses={(Array.isArray(customerAddresses) ? customerAddresses : []).map((address: any) => ({
                id: address.id,
                label: address.label,
                recipientName: address.recipientName,
                street: `${address.addressLine1}${address.addressLine2 ? `, ${address.addressLine2}` : ''}`,
                city: address.city,
                state: address.state,
                zipCode: address.zipCode,
                country: address.country || 'United States',
                phone: address.phone,
                isDefault: address.isDefault,
                type: address.type || 'both'
              }))}
              onAction={(action, data) => {
                switch (action) {
                  case 'add_address':
                    handleAddAddress();
                    break;
                  case 'edit_address':
                    const address = customerAddresses?.find((addr: any) => addr.id === data?.addressId);
                    if (address) handleEditAddress(address);
                    break;
                  case 'delete_address':
                    if (data?.addressId) handleDeleteAddress(data.addressId);
                    break;
                  case 'set_default_address':
                    if (data?.addressId) handleSetDefaultAddress(data.addressId);
                    break;
                  default:
                    console.log('Unhandled address action:', action, data);
                }
              }}
              title="My Addresses"
              description="Manage your shipping and billing addresses"
              showAddButton={true}
            />
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

      {/* Address Form Modal using shared AddressForm component */}
      {showAddressForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <AddressForm
              mode={editingAddressId ? 'edit' : 'create'}
              initialData={editingAddressId ? {
                label: addressFormData.label,
                recipientName: addressFormData.recipientName,
                street: addressFormData.addressLine1,
                street2: addressFormData.addressLine2,
                city: addressFormData.city,
                state: addressFormData.state,
                zipCode: addressFormData.zipCode,
                country: addressFormData.country,
                phone: addressFormData.phone,
                isDefault: addressFormData.isDefault,
                type: 'both'
              } : {
                recipientName: customer?.name || '',
                phone: customer?.phone || '',
                country: 'United States',
                type: 'both'
              }}
              onSubmit={async (data) => {
                // Transform shared component data back to API format
                const addressData = {
                  label: data.label || 'Address',
                  recipientName: data.recipientName,
                  addressLine1: data.street,
                  addressLine2: data.street2 || '',
                  city: data.city,
                  state: data.state,
                  zipCode: data.zipCode,
                  country: data.country,
                  phone: data.phone || '',
                  isDefault: data.isDefault,
                  customerId: selectedCustomerId,
                  isActive: true,
                  createdDate: new Date().toISOString()
                };

                try {
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
              }}
              onCancel={resetAddressForm}
              title={editingAddressId ? 'Edit Address' : 'Add New Address'}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
