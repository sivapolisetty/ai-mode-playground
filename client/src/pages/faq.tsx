import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface FAQItem {
  id: string;
  category: string;
  question: string;
  answer: string;
  tags?: string[];
}

const FAQPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  const faqData: FAQItem[] = [
    // Account & Registration
    {
      id: 'acc-1',
      category: 'Account & Registration',
      question: 'What information do I need to create an account?',
      answer: 'To create an account, you need to provide: Full Name, Email Address, Phone Number, Physical Address, and Date of Birth. Your email will be used for login and order notifications.',
      tags: ['registration', 'account', 'signup']
    },
    {
      id: 'acc-2',
      category: 'Account & Registration',
      question: 'Can I change my profile information after registration?',
      answer: 'Yes, you can update your profile information at any time by visiting your Profile page. You can change your name, email, phone number, and date of birth.',
      tags: ['profile', 'update', 'edit']
    },
    {
      id: 'acc-3',
      category: 'Account & Registration',
      question: 'Can I have multiple addresses on my account?',
      answer: 'Yes! You can add multiple addresses to your account (Home, Work, Office, etc.). You can set one as your default address for faster checkout.',
      tags: ['addresses', 'multiple', 'default']
    },

    // Orders & Shopping
    {
      id: 'ord-1',
      category: 'Orders & Shopping',
      question: 'How do I place an order?',
      answer: 'Browse our products, add items to your cart, and proceed to checkout. You\'ll need to select a shipping address and payment method to complete your order.',
      tags: ['order', 'shopping', 'checkout']
    },
    {
      id: 'ord-2',
      category: 'Orders & Shopping',
      question: 'What payment methods do you accept?',
      answer: 'We accept Credit Cards, PayPal, Cash on Delivery, and Gift Cards. You can also use a combination of gift cards and other payment methods.',
      tags: ['payment', 'credit card', 'paypal', 'gift card']
    },
    {
      id: 'ord-3',
      category: 'Orders & Shopping',
      question: 'How do I track my order?',
      answer: 'After placing an order, you\'ll receive a tracking number. You can view your order status and tracking information in the Orders section of your account.',
      tags: ['tracking', 'order status', 'shipping']
    },
    {
      id: 'ord-4',
      category: 'Orders & Shopping',
      question: 'Can I modify my order after placing it?',
      answer: 'Unfortunately, orders cannot be modified after they\'re placed. If you need to make changes, you\'ll need to cancel the order (if eligible) and place a new one.',
      tags: ['modify', 'change', 'edit order']
    },
    {
      id: 'ord-5',
      category: 'Orders & Shopping',
      question: 'What order statuses exist?',
      answer: 'Orders progress through these statuses: Pending (just placed), Processing (being prepared), Shipped (on the way), Delivered (received), Cancelled, or Returned.',
      tags: ['status', 'pending', 'processing', 'shipped', 'delivered']
    },

    // Cancellations & Returns
    {
      id: 'ret-1',
      category: 'Returns & Cancellations',
      question: 'Can I cancel my order?',
      answer: 'You can cancel orders that are in "Pending" or "Processing" status. Once an order is shipped, it cannot be cancelled, but you may be able to return it.',
      tags: ['cancel', 'cancellation', 'pending', 'processing']
    },
    {
      id: 'ret-2',
      category: 'Returns & Cancellations',
      question: 'How do I return an item?',
      answer: 'You can return items from orders with "Delivered" or "Processing" status. Go to your Orders page, find the order, and click "Return Order". You\'ll need to provide a reason for the return.',
      tags: ['return', 'delivered', 'return reason']
    },
    {
      id: 'ret-3',
      category: 'Returns & Cancellations',
      question: 'Which orders can be returned?',
      answer: 'Orders with "Delivered" or "Processing" status can be returned. Cancelled orders or orders that have already been returned cannot be returned again.',
      tags: ['return eligibility', 'delivered', 'processing']
    },
    {
      id: 'ret-4',
      category: 'Returns & Cancellations',
      question: 'What happens after I return an order?',
      answer: 'Once you submit a return request, the order status changes to "Returned" and the return date is recorded. Our customer service team will process your refund according to our refund policy.',
      tags: ['return process', 'refund', 'returned status']
    },

    // Gift Cards
    {
      id: 'gc-1',
      category: 'Gift Cards',
      question: 'How do I use a gift card?',
      answer: 'During checkout, select "Gift Card" as your payment method and enter your gift card code. The system will validate the code and apply the available balance to your order.',
      tags: ['gift card', 'payment', 'checkout', 'code']
    },
    {
      id: 'gc-2',
      category: 'Gift Cards',
      question: 'Can I use a gift card for partial payment?',
      answer: 'Yes! If your gift card balance is less than the order total, the remaining amount will be charged to your other selected payment method.',
      tags: ['partial payment', 'gift card balance', 'combination payment']
    },
    {
      id: 'gc-3',
      category: 'Gift Cards',
      question: 'What if my gift card code doesn\'t work?',
      answer: 'Gift card codes must be active and not expired. Make sure you\'ve entered the code correctly. If you continue having issues, contact customer support.',
      tags: ['gift card error', 'invalid code', 'expired']
    },
    {
      id: 'gc-4',
      category: 'Gift Cards',
      question: 'Do gift cards expire?',
      answer: 'Some gift cards may have expiration dates. Check your gift card details or contact customer support to verify the expiry date of your specific gift card.',
      tags: ['expiration', 'expiry date', 'validity']
    },

    // Products & Inventory
    {
      id: 'prod-1',
      category: 'Products & Inventory',
      question: 'What product categories are available?',
      answer: 'We offer three main categories: Electronics (computers, phones, gadgets), Clothing (apparel and accessories), and Footwear (shoes and related items).',
      tags: ['categories', 'electronics', 'clothing', 'footwear']
    },
    {
      id: 'prod-2',
      category: 'Products & Inventory',
      question: 'How do I know if a product is in stock?',
      answer: 'Product availability is shown on each product page. If a product is out of stock or inactive, it will be clearly marked and unavailable for purchase.',
      tags: ['stock', 'availability', 'out of stock']
    },
    {
      id: 'prod-3',
      category: 'Products & Inventory',
      question: 'Do you offer different sizes and colors?',
      answer: 'Yes! Many products are available in different sizes and colors. For clothing and footwear, we offer various sizes. Colors are available across all product categories where applicable.',
      tags: ['sizes', 'colors', 'variations', 'options']
    },

    // Shipping & Delivery
    {
      id: 'ship-1',
      category: 'Shipping & Delivery',
      question: 'Where do you ship?',
      answer: 'We currently ship within the USA. International shipping may be available in the future. All addresses must include valid US address information.',
      tags: ['shipping', 'delivery', 'USA', 'domestic']
    },
    {
      id: 'ship-2',
      category: 'Shipping & Delivery',
      question: 'How are shipping costs calculated?',
      answer: 'Shipping cost calculation is currently being updated. Please check during checkout for the most current shipping rates and options.',
      tags: ['shipping cost', 'rates', 'calculation']
    },
    {
      id: 'ship-3',
      category: 'Shipping & Delivery',
      question: 'Can I ship to a different address?',
      answer: 'Yes! During checkout, you can select any of your saved addresses or enter a new shipping address that\'s different from your account address.',
      tags: ['different address', 'shipping address', 'delivery address']
    },

    // Technical Support
    {
      id: 'tech-1',
      category: 'Technical Support',
      question: 'I\'m having trouble with the website. What should I do?',
      answer: 'Try refreshing the page or clearing your browser cache. If the problem persists, contact our technical support team with details about the issue you\'re experiencing.',
      tags: ['technical issues', 'website problems', 'support']
    },
    {
      id: 'tech-2',
      category: 'Technical Support',
      question: 'Which browsers are supported?',
      answer: 'Our website works best with modern browsers including Chrome, Firefox, Safari, and Edge. Make sure your browser is updated to the latest version for the best experience.',
      tags: ['browsers', 'compatibility', 'chrome', 'firefox', 'safari']
    },
    {
      id: 'tech-3',
      category: 'Technical Support',
      question: 'Is my information secure?',
      answer: 'We take data security seriously and implement various measures to protect your information. However, as this is a demo platform, please avoid entering real personal or payment information.',
      tags: ['security', 'privacy', 'data protection', 'demo']
    }
  ];

  const categories = ['all', ...Array.from(new Set(faqData.map(item => item.category)))];

  const filteredFAQs = faqData.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    const matchesSearch = searchQuery === '' || 
      item.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.tags?.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesCategory && matchesSearch;
  });

  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const expandAll = () => {
    setExpandedItems(new Set(filteredFAQs.map(item => item.id)));
  };

  const collapseAll = () => {
    setExpandedItems(new Set());
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Frequently Asked Questions
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Find answers to common questions about shopping, orders, returns, and more. 
            Can't find what you're looking for? Contact our support team.
          </p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex flex-col lg:flex-row gap-4 items-center">
              <div className="flex-1 w-full lg:w-auto">
                <Input
                  type="text"
                  placeholder="Search FAQs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full"
                />
              </div>
              
              <div className="flex flex-wrap gap-2">
                {categories.map(category => (
                  <Button
                    key={category}
                    variant={selectedCategory === category ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedCategory(category)}
                    className="text-xs"
                  >
                    {category === 'all' ? 'All Categories' : category}
                  </Button>
                ))}
              </div>
              
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={expandAll}>
                  Expand All
                </Button>
                <Button variant="ghost" size="sm" onClick={collapseAll}>
                  Collapse All
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Summary */}
        {searchQuery && (
          <div className="mb-6">
            <p className="text-sm text-gray-600">
              Found {filteredFAQs.length} result{filteredFAQs.length !== 1 ? 's' : ''} for "{searchQuery}"
            </p>
          </div>
        )}

        {/* FAQ Items */}
        <div className="space-y-4">
          {filteredFAQs.length > 0 ? (
            filteredFAQs.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader 
                  className="cursor-pointer"
                  onClick={() => toggleExpanded(item.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="outline" className="text-xs">
                          {item.category}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg text-left hover:text-blue-600 transition-colors">
                        {item.question}
                      </CardTitle>
                    </div>
                    <div className="ml-4">
                      <i className={`ri-${expandedItems.has(item.id) ? 'subtract' : 'add'}-line text-gray-400`}></i>
                    </div>
                  </div>
                </CardHeader>
                
                {expandedItems.has(item.id) && (
                  <CardContent className="pt-0">
                    <div className="prose prose-sm max-w-none">
                      <p className="text-gray-700 leading-relaxed">
                        {item.answer}
                      </p>
                    </div>
                    
                    {item.tags && item.tags.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-100">
                        <div className="flex flex-wrap gap-1">
                          <span className="text-xs text-gray-500 mr-2">Tags:</span>
                          {item.tags.map(tag => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                )}
              </Card>
            ))
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <i className="ri-search-line text-4xl text-gray-300 mb-4"></i>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your search terms or selecting a different category.
                </p>
                <Button variant="outline" onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                }}>
                  Clear Filters
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Contact Support */}
        <Card className="mt-8 bg-blue-50 border-blue-200">
          <CardContent className="text-center py-8">
            <i className="ri-customer-service-2-line text-3xl text-blue-600 mb-4"></i>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Still need help?
            </h3>
            <p className="text-gray-600 mb-4">
              Can't find the answer you're looking for? Our customer support team is here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button className="bg-blue-600 hover:bg-blue-700">
                <i className="ri-mail-line mr-2"></i>
                Contact Support
              </Button>
              <Button variant="outline">
                <i className="ri-phone-line mr-2"></i>
                Call Us
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Business Rules Summary */}
        <Card className="mt-8">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Business Rules Summary</CardTitle>
                <CardDescription>
                  Key policies and rules that govern our platform
                </CardDescription>
              </div>
              <Button 
                variant="outline"
                onClick={() => window.open('/business-rules', '_blank')}
              >
                <i className="ri-external-link-line mr-2"></i>
                View All Rules
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Order Management</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Orders in "Pending" or "Processing" status can be cancelled</li>
                  <li>• Orders in "Delivered" or "Processing" status can be returned</li>
                  <li>• Tracking numbers are provided for all orders</li>
                  <li>• Orders cannot be modified after placement</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Payment & Gift Cards</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Multiple payment methods accepted</li>
                  <li>• Gift cards can be used for partial payments</li>
                  <li>• Gift cards must be active and not expired</li>
                  <li>• Payment validation occurs at checkout</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Account & Addresses</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Multiple addresses allowed per account</li>
                  <li>• One default address per customer</li>
                  <li>• Profile information can be updated anytime</li>
                  <li>• Account status: Active or Inactive</li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Shipping & Returns</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Shipping currently available within USA</li>
                  <li>• Return reason required for all returns</li>
                  <li>• Custom shipping addresses allowed</li>
                  <li>• Order status tracking available</li>
                </ul>
              </div>
            </div>
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <div className="flex items-center">
                <i className="ri-information-line text-blue-600 mr-2"></i>
                <span className="text-sm text-blue-800">
                  This is a summary of our key business rules. For comprehensive details and examples, 
                  view the complete business rules documentation.
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default FAQPage;