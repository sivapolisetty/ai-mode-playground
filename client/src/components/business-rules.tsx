import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface BusinessRule {
  id: string;
  category: string;
  title: string;
  description: string;
  rules: string[];
  examples?: string[];
  applicability: 'all' | 'customers' | 'admin';
}

const BusinessRulesComponent: React.FC = () => {
  const businessRules: BusinessRule[] = [
    {
      id: 'order-mgmt',
      category: 'Order Management',
      title: 'Order Lifecycle and Status Rules',
      description: 'Rules governing order creation, status transitions, and management.',
      applicability: 'all',
      rules: [
        'Orders automatically receive a unique ID in format: ORD-{timestamp}',
        'Order status progresses: Pending → Processing → Shipped → Delivered',
        'Orders can be Cancelled or Returned based on current status',
        'Tracking numbers are automatically generated for all orders',
        'Orders cannot be modified after creation - must cancel and reorder'
      ],
      examples: [
        'Order ID: ORD-1734567890123',
        'Tracking: 1Z999001567890'
      ]
    },
    {
      id: 'order-cancel',
      category: 'Order Management',
      title: 'Order Cancellation Rules',
      description: 'When and how orders can be cancelled by customers.',
      applicability: 'customers',
      rules: [
        'Only orders with status "Pending" or "Processing" can be cancelled',
        'Cancelled orders cannot be uncancelled',
        'Order status changes to "Cancelled" immediately',
        'Both return and cancel flags are set to false after cancellation',
        'Confirmation is required before cancellation'
      ]
    },
    {
      id: 'order-return',
      category: 'Order Management', 
      title: 'Order Return Rules',
      description: 'Return eligibility and process requirements.',
      applicability: 'customers',
      rules: [
        'Orders with status "Delivered" or "Processing" can be returned',
        'Return reason is mandatory for all returns',
        'Return date is automatically set to current date',
        'Order status changes to "Returned" after processing',
        'Returned orders cannot be returned again',
        'Refund processing is handled separately from return requests'
      ]
    },
    {
      id: 'customer-account',
      category: 'Customer Management',
      title: 'Customer Account Rules',
      description: 'Account creation, management, and profile rules.',
      applicability: 'all',
      rules: [
        'Customer IDs follow format: CUST-XXX (e.g., CUST-001)',
        'Required fields: Name, Email, Phone, Address, Date of Birth',
        'Account status can be "Active" or "Inactive"',
        'Email addresses must be unique per customer',
        'Profile information can be updated at any time',
        'Registration date is automatically set and cannot be changed'
      ]
    },
    {
      id: 'address-mgmt',
      category: 'Customer Management',
      title: 'Address Management Rules',
      description: 'Rules for managing customer shipping and billing addresses.',
      applicability: 'customers',
      rules: [
        'Customers can have multiple addresses with descriptive labels',
        'Only one address can be set as default per customer',
        'Setting a new default automatically unsets the previous default',
        'Required fields: Label, Recipient Name, Address Line 1, City, State, ZIP',
        'Country defaults to "USA" but can be changed',
        'Addresses use soft deletion (marked inactive, not removed)',
        'Address Line 2 and Phone are optional fields'
      ]
    },
    {
      id: 'gift-cards',
      category: 'Payment & Gift Cards',
      title: 'Gift Card Usage Rules',
      description: 'Validation and usage rules for gift cards.',
      applicability: 'customers',
      rules: [
        'Gift card codes are case-insensitive and automatically uppercased',
        'Gift cards must be active (isActive = true) to be used',
        'Gift cards cannot be used if expired (when expiry date is set)',
        'Gift cards can be used for partial payments',
        'Discount applied is minimum of gift card balance and order total',
        'Gift card balance tracking requires separate implementation',
        'Gift card code is stored with order for tracking purposes'
      ],
      examples: [
        'Valid codes: GC-HOLIDAY2024, GC-SNEAKER50',
        'Partial payment: $50 gift card on $75 order = $50 discount'
      ]
    },
    {
      id: 'payment-methods',
      category: 'Payment & Gift Cards',
      title: 'Payment Method Rules',
      description: 'Supported payment methods and validation.',
      applicability: 'customers',
      rules: [
        'Accepted methods: Credit Card, PayPal, Cash on Delivery, Gift Card',
        'Payment method must be selected during checkout',
        'Total order amount must be positive',
        'Gift card payments require additional validation',
        'Multiple payment methods can be combined (e.g., gift card + credit card)',
        'Payment processing is validated but not actually processed in demo mode'
      ]
    },
    {
      id: 'product-catalog',
      category: 'Product Management',
      title: 'Product Catalog Rules',
      description: 'Product organization, pricing, and availability rules.',
      applicability: 'all',
      rules: [
        'Products belong to categories: Electronics, Clothing, or Footwear',
        'Product IDs follow format: PROD-XXX (e.g., PROD-001)',
        'Required fields: Category, Name, Description, Price',
        'Prices must be positive numbers',
        'Products can be active or inactive (isActive flag)',
        'Stock quantity is tracked but not automatically deducted',
        'Size and color variations are supported',
        'Electronics can have detailed specifications in JSON format'
      ]
    },
    {
      id: 'inventory',
      category: 'Product Management',
      title: 'Inventory Management Rules',
      description: 'Stock tracking and availability rules.',
      applicability: 'admin',
      rules: [
        'Stock quantity is manually managed through admin interface',
        'No automatic stock deduction on order placement',
        'No inventory reservation during checkout process',
        'Products can be disabled without removing from catalog',
        'Stock levels do not prevent order placement',
        'Low stock alerts are not automated'
      ]
    },
    {
      id: 'shipping',
      category: 'Shipping & Delivery',
      title: 'Shipping and Delivery Rules',
      description: 'Shipping policies and delivery procedures.',
      applicability: 'customers',
      rules: [
        'Shipping currently available within USA only',
        'Each order requires a shipping address',
        'Customers can use saved addresses or enter new ones',
        'Custom shipping addresses can differ from account address',
        'Tracking numbers are provided for all shipments',
        'Shipping costs are not automatically calculated',
        'Delivery date estimation is not currently available'
      ]
    },
    {
      id: 'admin-access',
      category: 'System Administration',
      title: 'Administrative Access Rules',
      description: 'Admin capabilities and system management rules.',
      applicability: 'admin',
      rules: [
        'Full CRUD access to all system entities',
        'Can view and modify all customer, product, and order data',
        'Direct database operations through admin interface',
        'No authentication required (demo limitation)',
        'No audit trail of administrative changes',
        'Can manually update order status and inventory',
        'Access to all historical data and transactions'
      ]
    },
    {
      id: 'data-validation',
      category: 'System Administration',
      title: 'Data Validation Rules',
      description: 'Schema validation and data integrity rules.',
      applicability: 'all',
      rules: [
        'All inputs validated against predefined schemas',
        'Required fields cannot be null or empty',
        'Email format validation enforced',
        'Phone number format validation applied',
        'Numeric fields must contain valid numbers',
        'Date fields must be valid date formats',
        'Foreign key relationships are enforced',
        'Data type validation prevents incorrect formats'
      ]
    }
  ];

  const categories = Array.from(new Set(businessRules.map(rule => rule.category)));

  const getApplicabilityBadge = (applicability: string) => {
    switch (applicability) {
      case 'customers':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Customer Facing</Badge>;
      case 'admin':
        return <Badge variant="secondary" className="bg-purple-100 text-purple-800">Admin Only</Badge>;
      default:
        return <Badge variant="outline" className="bg-green-100 text-green-800">Public</Badge>;
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Business Rules & Policies
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Comprehensive overview of our business rules, policies, and operational guidelines 
          that govern the ShopHub e-commerce platform.
        </p>
      </div>

      {/* Categories Overview */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Rule Categories</CardTitle>
          <CardDescription>
            Our business rules are organized into the following categories
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {categories.map(category => {
              const count = businessRules.filter(rule => rule.category === category).length;
              return (
                <div key={category} className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="font-medium text-gray-900 mb-1">{category}</div>
                  <div className="text-sm text-gray-600">{count} rule{count !== 1 ? 's' : ''}</div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Business Rules by Category */}
      {categories.map(category => (
        <div key={category} className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">{category}</h2>
          
          <div className="space-y-6">
            {businessRules
              .filter(rule => rule.category === category)
              .map(rule => (
                <Card key={rule.id} className="hover:shadow-md transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-lg">{rule.title}</CardTitle>
                        <CardDescription className="mt-1">
                          {rule.description}
                        </CardDescription>
                      </div>
                      <div className="ml-4">
                        {getApplicabilityBadge(rule.applicability)}
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent>
                    <div className="space-y-4">
                      {/* Rules List */}
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Rules:</h4>
                        <ul className="space-y-1">
                          {rule.rules.map((ruleText, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-blue-500 mr-2 mt-1 flex-shrink-0">•</span>
                              <span className="text-gray-700 text-sm">{ruleText}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Examples */}
                      {rule.examples && rule.examples.length > 0 && (
                        <div className="bg-gray-50 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 mb-2">Examples:</h4>
                          <ul className="space-y-1">
                            {rule.examples.map((example, index) => (
                              <li key={index} className="text-sm text-gray-600 font-mono">
                                {example}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
          </div>
        </div>
      ))}

      {/* Quick Reference */}
      <Card className="mt-8 bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">Quick Reference Guide</CardTitle>
          <CardDescription className="text-blue-700">
            Key business rules at a glance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-blue-900 mb-2">Order Actions</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Cancel: Pending/Processing orders</li>
                <li>✓ Return: Delivered/Processing orders</li>
                <li>✗ Modify: Not allowed after creation</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-900 mb-2">Payment Methods</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Credit Card</li>
                <li>✓ PayPal</li>
                <li>✓ Cash on Delivery</li>
                <li>✓ Gift Card (with validation)</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-900 mb-2">Account Features</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Multiple addresses</li>
                <li>✓ One default address</li>
                <li>✓ Profile updates anytime</li>
                <li>✓ Order history tracking</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contact Note */}
      <Card className="mt-8">
        <CardContent className="text-center py-6">
          <p className="text-gray-600">
            Have questions about our business rules or policies? 
            <span className="text-blue-600 font-medium ml-1">Contact our support team</span> for clarification.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};

export default BusinessRulesComponent;