import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useLocation } from 'wouter';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import { DynamicUIRenderer, useDynamicUI, type DynamicUISpec } from '@/components/ui/dynamic-ui-renderer';

interface Customer {
  id: string;
  name: string;
  email: string;
  phone?: string;
  status?: string;
}

interface ConversationEntry {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  uiSpec?: DynamicUISpec; // Add UI specification for enhanced messages
}

interface ChatResponse {
  message: string;
  ui_components?: any[];
  layout_strategy?: string;
  user_intent?: string;
  response_type?: string;
  session_id: string;
  timestamp: string;
  debug?: any;
  validation?: any;
}

export default function IntelligentUIPage() {
  const [conversation, setConversation] = useState<ConversationEntry[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCustomerId, setSelectedCustomerId] = useState('CUST-001');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [, navigate] = useLocation();
  const { toast } = useToast();
  
  // Dynamic UI state
  const { handleAction } = useDynamicUI();

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

  // Fetch customers using existing query pattern
  const { data: customers = [] } = useQuery<Customer[]>({
    queryKey: ['/api/customers'],
    queryFn: async () => {
      const response = await fetch('/api/customers');
      if (!response.ok) throw new Error('Failed to fetch customers');
      return response.json();
    }
  });

  const selectedCustomer = customers.find(c => c.id === selectedCustomerId);

  // Load chat history on component mount
  useEffect(() => {
    const initializeChatSession = async () => {
      const currentSessionId = await findOrCreateChatSession(selectedCustomerId);
      const historyLoaded = await loadChatHistory(currentSessionId);
      
      // If no history was loaded, add welcome message
      if (!historyLoaded) {
        setTimeout(() => {
          addMessage('assistant', `Hi! I'm now assisting customer ${selectedCustomerId}. How can I help you today?`);
        }, 100);
      }
    };
    
    initializeChatSession();
  }, []); // Only run once on mount

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Find or create a chat session for the customer
  const findOrCreateChatSession = async (customerId: string) => {
    try {
      // First, try to get existing sessions for the customer
      const response = await apiRequest('GET', `/api/customers/${customerId}/chat-sessions`);
      const sessions = await response.json();
      
      let currentSessionId: string;
      
      if (sessions.length > 0) {
        // Use the most recent session (sessions are ordered by updatedDate DESC)
        currentSessionId = sessions[0].id;
        console.log('Using existing session:', currentSessionId, 'for customer:', customerId);
      } else {
        // Create a new session if none exists
        currentSessionId = crypto.randomUUID();
        await apiRequest('POST', `/api/customers/${customerId}/chat-sessions`, {
          id: currentSessionId,
          title: `Chat Session - ${new Date().toLocaleDateString()}`
        });
        console.log('Created new session:', currentSessionId, 'for customer:', customerId);
      }
      
      setSessionId(currentSessionId);
      return currentSessionId;
    } catch (error) {
      console.error('Failed to find or create chat session:', error);
      // Fallback: create a session with a new UUID
      const fallbackSessionId = crypto.randomUUID();
      setSessionId(fallbackSessionId);
      return fallbackSessionId;
    }
  };

  // Load chat history for current session
  const loadChatHistory = async (sessionId: string) => {
    try {
      const response = await apiRequest('GET', `/api/chat-sessions/${sessionId}`);
      const sessionData = await response.json();
      
      if (sessionData.messages && sessionData.messages.length > 0) {
        const loadedMessages = sessionData.messages.map((msg: any) => ({
          id: crypto.randomUUID(),
          type: msg.messageType,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        setConversation(loadedMessages);
        console.log(`Loaded ${loadedMessages.length} messages from chat history`);
        return true; // History was loaded
      }
      return false; // No history found
    } catch (error) {
      console.error('Failed to load chat history:', error);
      return false;
    }
  };

  const addMessage = async (type: 'user' | 'assistant', content: string, saveToDatabase = true, uiSpec?: DynamicUISpec) => {
    const newMessage: ConversationEntry = {
      id: crypto.randomUUID(),
      type,
      content,
      timestamp: new Date(),
      ...(uiSpec && { uiSpec })
    };
    setConversation(prev => [...prev, newMessage]);

    // Save message to database
    if (saveToDatabase && sessionId) {
      try {
        await apiRequest('POST', `/api/chat-sessions/${sessionId}/messages`, {
          messageType: type,
          content: content
        });
        console.log(`Saved ${type} message to session ${sessionId}`);
      } catch (error) {
        console.error('Failed to save message to database:', error);
      }
    }
  };

  const handleCustomerChange = async (customerId: string) => {
    setSelectedCustomerId(customerId);
    setConversation([]);
    
    // Find or create chat session for new customer
    const currentSessionId = await findOrCreateChatSession(customerId);
    
    // Try to load existing chat history
    const historyLoaded = await loadChatHistory(currentSessionId);
    
    // If no history was loaded, add welcome message
    if (!historyLoaded) {
      setTimeout(() => {
        addMessage('assistant', `Hi! I'm now assisting customer ${customerId}. How can I help you today?`);
      }, 100);
    }

    toast({
      title: "Customer switched",
      description: `Now assisting ${customers.find(c => c.id === customerId)?.name || customerId}`,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userInput.trim() || isLoading) return;

    const currentInput = userInput;
    setUserInput('');
    setIsLoading(true);

    addMessage('user', currentInput);

    try {
      const response = await fetch('http://localhost:8001/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentInput,
          context: {
            customerId: selectedCustomerId,
            currentView: 'intelligent-ui',
            session_id: sessionId
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from AI');
      }

      const data: ChatResponse = await response.json();
      
      // Create UI specification if components are present
      let uiSpec: DynamicUISpec | undefined;
      if (data.ui_components && data.ui_components.length > 0) {
        uiSpec = {
          ui_components: data.ui_components,
          layout_strategy: data.layout_strategy || 'text_only',
          user_intent: data.user_intent || 'unknown',
          validation: data.validation
        };
      }
      
      addMessage('assistant', data.message, true, uiSpec);
      
      // Log UI generation info
      if (uiSpec) {
        console.log('🎨 Dynamic UI Generated:', {
          components: uiSpec.ui_components.length,
          layout: uiSpec.layout_strategy,
          intent: uiSpec.user_intent
        });
      }

    } catch (error) {
      console.error('Error processing input:', error);
      addMessage('assistant', 'I apologize, but I encountered an error processing your request. Please try again.');
      
      toast({
        title: "Error",
        description: "Failed to process your request. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getCustomerInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <i className="ri-shopping-bag-fill text-white text-lg"></i>
                </div>
                <h1 className="ml-2 text-xl font-bold text-gray-900">ShopHub</h1>
                <span className="ml-2 text-sm text-purple-600 font-medium">AI Assistant</span>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => navigate(`/?customerId=${selectedCustomerId}`)}
              >
                <i className="ri-arrow-left-line mr-1"></i>
                Traditional Mode
              </Button>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                AI Shopping Assistant
              </h1>
              <p className="text-gray-600">
                Get personalized help with your shopping needs using natural language
              </p>
            </div>
            
            {/* Customer Selector */}
            <Card className="p-4 min-w-64">
              <div className="flex items-center gap-3 mb-2">
                <i className="ri-user-line text-blue-600"></i>
                <span className="font-medium text-gray-700">Current Customer</span>
              </div>
              
              <select
                value={selectedCustomerId}
                onChange={(e) => handleCustomerChange(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name} ({customer.email})
                  </option>
                ))}
              </select>
              
              {selectedCustomer && (
                <div className="flex items-center gap-2 mt-2 p-2 bg-blue-50 rounded">
                  <Avatar className="h-6 w-6">
                    <AvatarFallback className="text-xs bg-blue-600 text-white">
                      {getCustomerInitials(selectedCustomer.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="text-sm">
                    <div className="font-medium">{selectedCustomer.name}</div>
                    <div className="text-gray-600">{selectedCustomer.email}</div>
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>

        {/* Chat Interface */}
        <Card className="h-[600px] flex flex-col">
          {/* Messages */}
          <CardContent className="flex-1 overflow-y-auto p-6 space-y-4">
            {conversation.length === 0 && (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <i className="ri-robot-line text-2xl text-white"></i>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Welcome to AI Shopping Assistant
                </h3>
                <p className="text-gray-600 max-w-md mx-auto mb-4">
                  I can help you with orders, products, returns, and more. 
                  Just ask me naturally!
                </p>
                
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto">
                  <p className="text-blue-800 text-sm">
                    <strong>Current Customer:</strong> {selectedCustomer?.name || selectedCustomerId}
                    <br />
                    <span className="text-blue-600">
                      Switch customers using the dropdown above.
                    </span>
                  </p>
                </div>
              </div>
            )}

            {conversation.map((message) => (
              <div key={message.id} className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.type === 'assistant' && (
                  <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <i className="ri-robot-line text-white text-sm"></i>
                  </div>
                )}
                
                <div className={`max-w-4xl ${message.type === 'user' ? 'order-first' : ''}`}>
                  <div className={`rounded-lg px-4 py-2 ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white ml-12' 
                      : 'bg-white border shadow-sm'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                  
                  {/* Dynamic UI Components */}
                  {message.uiSpec && (
                    <div className="mt-3 px-2">
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                          <div className="w-5 h-5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                            <i className="ri-magic-line text-white text-xs"></i>
                          </div>
                          <span className="text-sm font-medium text-gray-700">Interactive UI</span>
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
                            {message.uiSpec.layout_strategy}
                          </span>
                        </div>
                        
                        <DynamicUIRenderer
                          uiSpec={message.uiSpec}
                          onAction={handleAction}
                          context={{
                            customerId: selectedCustomerId,
                            sessionId: sessionId,
                            customer: selectedCustomer
                          }}
                          className="dynamic-ui-message"
                        />
                      </div>
                    </div>
                  )}
                  
                  <div className="text-xs text-gray-500 mt-1 px-2 flex items-center gap-2">
                    <span>{message.timestamp.toLocaleTimeString()}</span>
                    {message.uiSpec && (
                      <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-xs">
                        🎨 {message.uiSpec.ui_components.length} UI components
                      </span>
                    )}
                  </div>
                </div>

                {message.type === 'user' && (
                  <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center flex-shrink-0">
                    <i className="ri-user-line text-white text-sm"></i>
                  </div>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="flex gap-3">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
                  <i className="ri-robot-line text-white text-sm"></i>
                </div>
                <div className="bg-white border rounded-lg px-4 py-2 shadow-sm">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </CardContent>

          {/* Input */}
          <div className="border-t p-4">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Ask me anything... (e.g., 'Show me my recent orders' or 'Find iPhone products')"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <Button
                type="submit"
                disabled={isLoading || !userInput.trim()}
                className="px-6"
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <i className="ri-send-plane-line"></i>
                )}
              </Button>
            </form>
          </div>
        </Card>

        {/* Help Section */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setUserInput("What's the price of iPhone 15 Pro?")}>
            <div className="flex items-center gap-2 mb-2">
              <i className="ri-question-line text-blue-600"></i>
              <h3 className="font-medium">Ask Questions</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              "What's the price of iPhone 15 Pro?" or "Show me my order history"
            </p>
            <span className="text-xs text-blue-600 font-medium">Click to try →</span>
          </Card>
          
          <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setUserInput("Find laptops under $1000")}>
            <div className="flex items-center gap-2 mb-2">
              <i className="ri-search-line text-green-600"></i>
              <h3 className="font-medium">Search Products</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              "Find laptops under $1000" or "Show me Samsung products"
            </p>
            <span className="text-xs text-green-600 font-medium">Click to try →</span>
          </Card>
          
          <Card className="p-4 cursor-pointer hover:shadow-md transition-shadow" onClick={() => setUserInput("Show me my recent orders")}>
            <div className="flex items-center gap-2 mb-2">
              <i className="ri-customer-service-2-line text-purple-600"></i>
              <h3 className="font-medium">Get Help</h3>
            </div>
            <p className="text-sm text-gray-600 mb-2">
              "Show me my recent orders" or "What's my customer information?"
            </p>
            <span className="text-xs text-purple-600 font-medium">Click to try →</span>
          </Card>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-6">
          <Card className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <h3 className="font-medium text-gray-900 mb-3">✨ Try these examples:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
              {[
                "What categories do you have?",
                "Show me all customers", 
                "Find iPhone products",
                "What's my customer info?"
              ].map((example, index) => (
                <button
                  key={index}
                  onClick={() => setUserInput(example)}
                  className="text-left p-2 bg-white rounded border hover:shadow-sm transition-shadow text-sm text-gray-700 hover:text-blue-600"
                >
                  "{example}"
                </button>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}