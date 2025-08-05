import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { initializeDatabase, db } from "./db";
import { seedEcommerceDatabase } from "./db/ecommerce-seed";
import { z } from "zod";
import { 
  insertCustomerSchema, 
  insertCategorySchema,
  insertProductSchema,
  insertOrderSchema,
  insertOrderItemSchema,
  insertCartItemSchema,
  insertChatSessionSchema,
  insertChatMessageSchema,
  cartItems,
  chatSessions,
  chatMessages
} from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);

  // Initialize database
  await initializeDatabase();
  
  // Seed database with ecommerce data
  await seedEcommerceDatabase();

  
  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      services: {
        database: 'connected'
      }
    });
  });
  
  // REST API routes (for write operations)
  
  // Customer routes
  app.post('/api/customers', async (req, res) => {
    try {
      const validatedData = insertCustomerSchema.parse(req.body);
      const customer = await storage.createCustomer(validatedData);
      res.status(201).json(customer);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: 'Failed to create customer' });
    }
  });

  app.patch('/api/customers/:id', async (req, res) => {
    try {
      const { id } = req.params;
      const validatedData = insertCustomerSchema.partial().parse(req.body);
      const customer = await storage.updateCustomer(id, validatedData);
      
      if (!customer) {
        return res.status(404).json({ error: 'Customer not found' });
      }
      
      res.json(customer);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: 'Failed to update customer' });
    }
  });

  // Customer orders route
  app.get('/api/customers/:id/orders', async (req, res) => {
    try {
      const { id } = req.params;
      const orders = await storage.getOrdersByCustomerIdWithItems(id);
      res.json(orders);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch customer orders' });
    }
  });

  // Customer addresses routes
  app.get('/api/customers/:id/addresses', async (req, res) => {
    try {
      const { id } = req.params;
      const addresses = await storage.getCustomerAddresses(id);
      res.json(addresses);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch customer addresses' });
    }
  });

  app.post('/api/customers/:id/addresses', async (req, res) => {
    try {
      const { id } = req.params;
      const addressData = { ...req.body, customerId: id };
      const address = await storage.createCustomerAddress(addressData);
      res.status(201).json(address);
    } catch (error) {
      res.status(500).json({ error: 'Failed to create customer address' });
    }
  });

  app.put('/api/customers/:customerId/addresses/:addressId/default', async (req, res) => {
    try {
      const { customerId, addressId } = req.params;
      const success = await storage.setDefaultAddress(customerId, parseInt(addressId));
      if (success) {
        res.json({ success: true });
      } else {
        res.status(400).json({ error: 'Failed to set default address' });
      }
    } catch (error) {
      res.status(500).json({ error: 'Failed to set default address' });
    }
  });

  app.get('/api/customers', async (req, res) => {
    try {
      const customers = await storage.getAllCustomers();
      res.json(customers);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch customers' });
    }
  });

  // Order placement endpoint
  app.post('/api/orders', async (req, res) => {
    try {
      console.log('Order placement request received:', req.body);
      const { customerId, orderDate, totalAmount, status, shippingAddress, paymentMethod, items } = req.body;
      
      if (!customerId || !items || items.length === 0) {
        console.error('Missing required fields:', { customerId, itemsLength: items?.length });
        return res.status(400).json({ error: 'Missing required fields: customerId and items are required' });
      }
      
      // Generate order ID
      const orderId = `ORD-${Date.now()}`;
      console.log('Generated order ID:', orderId);
      
      // Create order
      const orderData = {
        id: orderId,
        customerId,
        orderDate,
        totalAmount,
        status,
        shippingAddress,
        paymentMethod,
        trackingNumber: `1Z999${customerId.slice(-3)}${Date.now().toString().slice(-6)}`,
        canReturn: status === 'Delivered' || status === 'Processing',
        canCancel: status === 'Pending' || status === 'Processing',
        giftCardCode: paymentMethod === 'Gift Card' ? req.body.giftCardCode : undefined
      };
      
      console.log('Creating order with data:', orderData);
      const order = await storage.createOrder(orderData);
      console.log('Order created successfully:', order);
      
      // Create order items
      console.log('Creating order items for order:', orderId);
      for (const item of items) {
        const orderItemData = {
          orderId,
          productId: item.productId,
          quantity: item.quantity,
          price: item.price
        };
        console.log('Creating order item:', orderItemData);
        await storage.createOrderItem(orderItemData);
      }
      
      console.log('Order placement completed successfully');
      res.status(201).json(order);
    } catch (error: any) {
      console.error('Order creation error:', error);
      res.status(500).json({ error: `Failed to create order: ${error?.message || 'Unknown error'}` });
    }
  });

  // Category routes
  app.post('/api/categories', async (req, res) => {
    try {
      const validatedData = insertCategorySchema.parse(req.body);
      const category = await storage.createCategory(validatedData);
      res.status(201).json(category);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: 'Failed to create category' });
    }
  });

  app.get('/api/categories', async (req, res) => {
    try {
      const categories = await storage.getAllCategories();
      res.json(categories);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch categories' });
    }
  });

  // Product routes
  app.post('/api/products', async (req, res) => {
    try {
      const validatedData = insertProductSchema.parse(req.body);
      const product = await storage.createProduct(validatedData);
      res.status(201).json(product);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: 'Failed to create product' });
    }
  });

  app.get('/api/products', async (req, res) => {
    try {
      const products = await storage.getAllProducts();
      res.json(products);
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch products' });
    }
  });

  app.patch('/api/products/:id', async (req, res) => {
    try {
      const id = req.params.id;
      const validatedData = insertProductSchema.partial().parse(req.body);
      const product = await storage.updateProduct(id, validatedData);
      
      if (!product) {
        return res.status(404).json({ error: 'Product not found' });
      }
      
      res.json(product);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      res.status(500).json({ error: 'Failed to update product' });
    }
  });


  // Return order endpoint
  app.patch('/api/orders/:orderId/return', async (req, res) => {
    try {
      const { orderId } = req.params;
      const { returnReason } = req.body;
      
      if (!returnReason) {
        return res.status(400).json({ error: 'Return reason is required' });
      }

      const order = await storage.getOrderById(orderId);
      if (!order) {
        return res.status(404).json({ error: 'Order not found' });
      }

      if (!order.canReturn) {
        return res.status(400).json({ error: 'This order cannot be returned' });
      }

      const updatedOrder = await storage.returnOrder(orderId, returnReason);
      res.json(updatedOrder);
    } catch (error: any) {
      console.error('Return order error:', error);
      res.status(500).json({ error: `Failed to return order: ${error?.message || 'Unknown error'}` });
    }
  });

  // Cancel order endpoint
  app.patch('/api/orders/:orderId/cancel', async (req, res) => {
    try {
      const { orderId } = req.params;

      const order = await storage.getOrderById(orderId);
      if (!order) {
        return res.status(404).json({ error: 'Order not found' });
      }

      if (!order.canCancel) {
        return res.status(400).json({ error: 'This order cannot be cancelled' });
      }

      const updatedOrder = await storage.cancelOrder(orderId);
      res.json(updatedOrder);
    } catch (error: any) {
      console.error('Cancel order error:', error);
      res.status(500).json({ error: `Failed to cancel order: ${error?.message || 'Unknown error'}` });
    }
  });

  // Gift card validation endpoint
  app.get('/api/gift-cards/:code', async (req, res) => {
    try {
      const { code } = req.params;
      const giftCard = await storage.getGiftCardByCode(code);
      
      if (!giftCard) {
        return res.status(404).json({ error: 'Gift card not found' });
      }

      if (!giftCard.isActive) {
        return res.status(400).json({ error: 'Gift card is not active' });
      }

      res.json({
        code: giftCard.code,
        balance: giftCard.balance,
        isActive: giftCard.isActive
      });
    } catch (error: any) {
      console.error('Gift card validation error:', error);
      res.status(500).json({ error: `Failed to validate gift card: ${error?.message || 'Unknown error'}` });
    }
  });

  // Cart API routes
  
  // Get cart items for a customer
  app.get('/api/customers/:customerId/cart', async (req, res) => {
    try {
      const { customerId } = req.params;
      const cartItems = await storage.getCartByCustomerId(customerId);
      res.json(cartItems);
    } catch (error: any) {
      console.error('Get cart error:', error);
      res.status(500).json({ error: `Failed to get cart: ${error?.message || 'Unknown error'}` });
    }
  });

  // Add item to cart
  app.post('/api/customers/:customerId/cart', async (req, res) => {
    try {
      const { customerId } = req.params;
      const cartItemData = { 
        ...req.body, 
        customerId,
        addedDate: new Date().toISOString().split('T')[0]
      };
      const validatedData = insertCartItemSchema.parse(cartItemData);
      const cartItem = await storage.addToCart(validatedData);
      res.status(201).json(cartItem);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      console.error('Add to cart error:', error);
      res.status(500).json({ error: `Failed to add to cart: ${error?.message || 'Unknown error'}` });
    }
  });

  // Update cart item
  app.patch('/api/cart/:itemId', async (req, res) => {
    try {
      const { itemId } = req.params;
      const validatedData = insertCartItemSchema.partial().parse(req.body);
      const cartItem = await storage.updateCartItem(parseInt(itemId), validatedData);
      
      if (!cartItem) {
        return res.status(404).json({ error: 'Cart item not found' });
      }
      
      res.json(cartItem);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      console.error('Update cart item error:', error);
      res.status(500).json({ error: `Failed to update cart item: ${error?.message || 'Unknown error'}` });
    }
  });

  // Remove item from cart
  app.delete('/api/cart/:itemId', async (req, res) => {
    try {
      const { itemId } = req.params;
      const success = await storage.removeFromCart(parseInt(itemId));
      
      if (!success) {
        return res.status(404).json({ error: 'Cart item not found' });
      }
      
      res.json({ success: true });
    } catch (error: any) {
      console.error('Remove from cart error:', error);
      res.status(500).json({ error: `Failed to remove from cart: ${error?.message || 'Unknown error'}` });
    }
  });

  // Clear entire cart for a customer
  app.delete('/api/customers/:customerId/cart', async (req, res) => {
    try {
      const { customerId } = req.params;
      const success = await storage.clearCart(customerId);
      res.json({ success });
    } catch (error: any) {
      console.error('Clear cart error:', error);
      res.status(500).json({ error: `Failed to clear cart: ${error?.message || 'Unknown error'}` });
    }
  });

  // Chat History API routes
  
  // Create a new chat session
  app.post('/api/customers/:customerId/chat-sessions', async (req, res) => {
    try {
      const { customerId } = req.params;
      const sessionData = { 
        ...req.body, 
        customerId,
        id: req.body.id || crypto.randomUUID(),
        createdDate: new Date().toISOString(),
        updatedDate: new Date().toISOString()
      };
      const validatedData = insertChatSessionSchema.parse(sessionData);
      const session = await storage.createChatSession(validatedData);
      res.status(201).json(session);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      console.error('Create chat session error:', error);
      res.status(500).json({ error: `Failed to create chat session: ${error?.message || 'Unknown error'}` });
    }
  });

  // Get chat sessions for a customer
  app.get('/api/customers/:customerId/chat-sessions', async (req, res) => {
    try {
      const { customerId } = req.params;
      const sessions = await storage.getChatSessionsByCustomerId(customerId);
      res.json(sessions);
    } catch (error: any) {
      console.error('Get chat sessions error:', error);
      res.status(500).json({ error: `Failed to get chat sessions: ${error?.message || 'Unknown error'}` });
    }
  });

  // Get a specific chat session with messages
  app.get('/api/chat-sessions/:sessionId', async (req, res) => {
    try {
      const { sessionId } = req.params;
      const sessionWithMessages = await storage.getChatSessionWithMessages(sessionId);
      
      if (!sessionWithMessages) {
        return res.status(404).json({ error: 'Chat session not found' });
      }
      
      res.json(sessionWithMessages);
    } catch (error: any) {
      console.error('Get chat session error:', error);
      res.status(500).json({ error: `Failed to get chat session: ${error?.message || 'Unknown error'}` });
    }
  });

  // Add a message to a chat session
  app.post('/api/chat-sessions/:sessionId/messages', async (req, res) => {
    try {
      const { sessionId } = req.params;
      const messageData = { 
        ...req.body, 
        sessionId,
        timestamp: new Date().toISOString()
      };
      const validatedData = insertChatMessageSchema.parse(messageData);
      const message = await storage.addChatMessage(validatedData);
      res.status(201).json(message);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      console.error('Add chat message error:', error);
      res.status(500).json({ error: `Failed to add chat message: ${error?.message || 'Unknown error'}` });
    }
  });

  // Get messages for a chat session
  app.get('/api/chat-sessions/:sessionId/messages', async (req, res) => {
    try {
      const { sessionId } = req.params;
      const messages = await storage.getChatMessages(sessionId);
      res.json(messages);
    } catch (error: any) {
      console.error('Get chat messages error:', error);
      res.status(500).json({ error: `Failed to get chat messages: ${error?.message || 'Unknown error'}` });
    }
  });

  // Update a chat session (e.g., title)
  app.patch('/api/chat-sessions/:sessionId', async (req, res) => {
    try {
      const { sessionId } = req.params;
      const validatedData = insertChatSessionSchema.partial().parse(req.body);
      const session = await storage.updateChatSession(sessionId, validatedData);
      
      if (!session) {
        return res.status(404).json({ error: 'Chat session not found' });
      }
      
      res.json(session);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: error.errors });
      }
      console.error('Update chat session error:', error);
      res.status(500).json({ error: `Failed to update chat session: ${error?.message || 'Unknown error'}` });
    }
  });

  // Delete a chat session
  app.delete('/api/chat-sessions/:sessionId', async (req, res) => {
    try {
      const { sessionId } = req.params;
      const success = await storage.deleteChatSession(sessionId);
      
      if (!success) {
        return res.status(404).json({ error: 'Chat session not found' });
      }
      
      res.json({ success: true });
    } catch (error: any) {
      console.error('Delete chat session error:', error);
      res.status(500).json({ error: `Failed to delete chat session: ${error?.message || 'Unknown error'}` });
    }
  });

  // Admin API routes for database management
  
  // Generic GET route for all tables
  app.get('/api/admin/:table', async (req, res) => {
    try {
      const { table } = req.params;
      let data;
      
      switch (table) {
        case 'customers':
          data = await storage.getAllCustomers();
          break;
        case 'products':
          data = await storage.getAllProducts();
          break;
        case 'categories':
          data = await storage.getAllCategories();
          break;
        case 'orders':
          data = await storage.getAllOrders();
          break;
        case 'orderItems':
          data = await storage.getAllOrderItems();
          break;
        case 'giftCards':
          data = await storage.getAllGiftCards();
          break;
        case 'customerAddresses':
          data = await storage.getAllCustomerAddresses();
          break;
        case 'cartItems':
          // For cart items, we need to get all and then fetch product details
          const allCartItems = await db.select().from(cartItems);
          const cartWithProducts = await Promise.all(
            allCartItems.map(async (item: any) => {
              const product = item.productId ? await storage.getProductById(item.productId) : null;
              return { ...item, product };
            })
          );
          data = cartWithProducts;
          break;
        case 'chatSessions':
          data = await db.select().from(chatSessions);
          break;
        case 'chatMessages':
          data = await db.select().from(chatMessages);
          break;
        default:
          return res.status(400).json({ error: 'Invalid table name' });
      }
      
      res.json({ data });
    } catch (error: any) {
      console.error(`Error fetching ${req.params.table}:`, error);
      res.status(500).json({ error: `Failed to fetch ${req.params.table}` });
    }
  });

  // Generic POST route for creating records
  app.post('/api/admin/:table', async (req, res) => {
    try {
      const { table } = req.params;
      let result;
      
      switch (table) {
        case 'customers':
          result = await storage.createCustomer(req.body);
          break;
        case 'products':
          result = await storage.createProduct(req.body);
          break;
        case 'categories':
          result = await storage.createCategory(req.body);
          break;
        case 'orders':
          result = await storage.createOrder(req.body);
          break;
        case 'orderItems':
          result = await storage.createOrderItem(req.body);
          break;
        case 'giftCards':
          result = await storage.createGiftCard(req.body);
          break;
        case 'customerAddresses':
          result = await storage.createCustomerAddress(req.body);
          break;
        case 'cartItems':
          result = await storage.addToCart(req.body);
          break;
        case 'chatSessions':
          result = await storage.createChatSession(req.body);
          break;
        case 'chatMessages':
          result = await storage.addChatMessage(req.body);
          break;
        default:
          return res.status(400).json({ error: 'Invalid table name' });
      }
      
      res.status(201).json(result);
    } catch (error: any) {
      console.error(`Error creating ${req.params.table} record:`, error);
      res.status(500).json({ error: `Failed to create ${req.params.table} record: ${error.message}` });
    }
  });

  // Generic PUT route for updating records
  app.put('/api/admin/:table/:id', async (req, res) => {
    try {
      const { table, id } = req.params;
      let result;
      
      switch (table) {
        case 'customers':
          result = await storage.updateCustomer(id, req.body);
          break;
        case 'products':
          result = await storage.updateProduct(id, req.body);
          break;
        case 'categories':
          result = await storage.updateCategory(parseInt(id), req.body);
          break;
        case 'orders':
          result = await storage.updateOrder(id, req.body);
          break;
        case 'orderItems':
          result = await storage.updateOrderItem(parseInt(id), req.body);
          break;
        case 'giftCards':
          result = await storage.updateGiftCard(parseInt(id), req.body);
          break;
        case 'customerAddresses':
          result = await storage.updateCustomerAddress(parseInt(id), req.body);
          break;
        case 'cartItems':
          result = await storage.updateCartItem(parseInt(id), req.body);
          break;
        case 'chatSessions':
          result = await storage.updateChatSession(id, req.body);
          break;
        case 'chatMessages':
          // Note: Chat messages are typically not updated, but we can support it
          return res.status(400).json({ error: 'Chat messages cannot be updated' });
        default:
          return res.status(400).json({ error: 'Invalid table name' });
      }
      
      if (!result) {
        return res.status(404).json({ error: 'Record not found' });
      }
      
      res.json(result);
    } catch (error: any) {
      console.error(`Error updating ${req.params.table} record:`, error);
      res.status(500).json({ error: `Failed to update ${req.params.table} record: ${error.message}` });
    }
  });

  // Generic DELETE route for deleting records
  app.delete('/api/admin/:table/:id', async (req, res) => {
    try {
      const { table, id } = req.params;
      let result;
      
      switch (table) {
        case 'customers':
          result = await storage.deleteCustomer(id);
          break;
        case 'products':
          result = await storage.deleteProduct(id);
          break;
        case 'categories':
          result = await storage.deleteCategory(parseInt(id));
          break;
        case 'orders':
          result = await storage.deleteOrder(id);
          break;
        case 'orderItems':
          result = await storage.deleteOrderItem(parseInt(id));
          break;
        case 'giftCards':
          result = await storage.deleteGiftCard(parseInt(id));
          break;
        case 'customerAddresses':
          result = await storage.deleteCustomerAddress(parseInt(id));
          break;
        case 'cartItems':
          result = await storage.removeFromCart(parseInt(id));
          break;
        case 'chatSessions':
          result = await storage.deleteChatSession(id);
          break;
        case 'chatMessages':
          result = await storage.deleteChatMessages(id); // This deletes all messages for a session
          break;
        default:
          return res.status(400).json({ error: 'Invalid table name' });
      }
      
      if (!result) {
        return res.status(404).json({ error: 'Record not found' });
      }
      
      res.json({ success: true });
    } catch (error: any) {
      console.error(`Error deleting ${req.params.table} record:`, error);
      res.status(500).json({ error: `Failed to delete ${req.params.table} record: ${error.message}` });
    }
  });

  return httpServer;
}
