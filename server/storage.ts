import {
  customers,
  categories,
  products,
  orders,
  orderItems,
  customerAddresses,
  giftCards,
  cartItems,
  chatSessions,
  chatMessages,
  type Customer,
  type InsertCustomer,
  type CustomerAddress,
  type InsertCustomerAddress,
  type Category,
  type InsertCategory,
  type Product,
  type InsertProduct,
  type Order,
  type InsertOrder,
  type OrderItem,
  type InsertOrderItem,
  type GiftCard,
  type InsertGiftCard,
  type CartItem,
  type InsertCartItem,
  type CartItemWithProduct,
  type ChatSession,
  type InsertChatSession,
  type ChatMessage,
  type InsertChatMessage,
  type ChatSessionWithMessages
} from "@shared/schema";
import { db } from "./db";
import { eq, and, desc } from "drizzle-orm";

// Interface for storage operations
export interface IStorage {
  // Customer methods
  getAllCustomers(): Promise<Customer[]>;
  getCustomerById(id: string): Promise<Customer | undefined>;
  createCustomer(customer: InsertCustomer): Promise<Customer>;
  updateCustomer(id: string, customer: Partial<InsertCustomer>): Promise<Customer | undefined>;
  deleteCustomer(id: string): Promise<boolean>;

  // Customer address methods
  getAllCustomerAddresses(): Promise<CustomerAddress[]>;
  getCustomerAddresses(customerId: string): Promise<CustomerAddress[]>;
  getCustomerAddressById(id: number): Promise<CustomerAddress | undefined>;
  createCustomerAddress(address: InsertCustomerAddress): Promise<CustomerAddress>;
  updateCustomerAddress(id: number, address: Partial<InsertCustomerAddress>): Promise<CustomerAddress | undefined>;
  deleteCustomerAddress(id: number): Promise<boolean>;
  setDefaultAddress(customerId: string, addressId: number): Promise<boolean>;

  // Category methods
  getAllCategories(): Promise<Category[]>;
  getCategoryById(id: number): Promise<Category | undefined>;
  createCategory(category: InsertCategory): Promise<Category>;

  // Product methods
  getAllProducts(): Promise<Product[]>;
  getProductById(id: string): Promise<Product | undefined>;
  getProductsByCategory(categoryId: number): Promise<Product[]>;
  createProduct(product: InsertProduct): Promise<Product>;
  updateProduct(id: string, product: Partial<InsertProduct>): Promise<Product | undefined>;

  // Order methods
  getAllOrders(): Promise<Order[]>;
  getOrdersByCustomerId(customerId: string): Promise<Order[]>;
  getOrdersByCustomerIdWithItems(customerId: string): Promise<any[]>;
  getOrderById(id: string): Promise<Order | undefined>;
  createOrder(order: InsertOrder): Promise<Order>;
  updateOrder(id: string, order: Partial<InsertOrder>): Promise<Order | undefined>;
  deleteOrder(id: string): Promise<boolean>;

  // Order Item methods
  getAllOrderItems(): Promise<OrderItem[]>;
  getOrderItemsByOrderId(orderId: string): Promise<OrderItem[]>;
  createOrderItem(orderItem: InsertOrderItem): Promise<OrderItem>;
  updateOrderItem(id: number, orderItem: Partial<InsertOrderItem>): Promise<OrderItem | undefined>;
  deleteOrderItem(id: number): Promise<boolean>;

  // Full customer data with orders
  getCustomerWithRelations(id: string): Promise<any | undefined>;

  // Gift card methods
  getAllGiftCards(): Promise<GiftCard[]>;
  getGiftCardByCode(code: string): Promise<GiftCard | undefined>;
  createGiftCard(giftCard: InsertGiftCard): Promise<GiftCard>;
  updateGiftCard(id: number, giftCard: Partial<InsertGiftCard>): Promise<GiftCard | undefined>;
  updateGiftCardBalance(code: string, newBalance: number): Promise<GiftCard | undefined>;
  deleteGiftCard(id: number): Promise<boolean>;

  // Category methods - additional
  updateCategory(id: number, category: Partial<InsertCategory>): Promise<Category | undefined>;
  deleteCategory(id: number): Promise<boolean>;

  // Product methods - additional
  deleteProduct(id: string): Promise<boolean>;

  // Order return and cancel methods
  returnOrder(orderId: string, returnReason: string): Promise<Order | undefined>;
  cancelOrder(orderId: string): Promise<Order | undefined>;

  // Plan and device methods (for GraphQL compatibility)
  getPlanByCustomerId(customerId: string): Promise<any>;
  getPlanWithFeaturesByCustomerId(customerId: string): Promise<any>;
  getDevicesByCustomerId(customerId: string): Promise<any[]>;
  getPlanFeaturesByPlanId(planId: number): Promise<any[]>;

  // Cart methods
  getCartByCustomerId(customerId: string): Promise<CartItemWithProduct[]>;
  addToCart(cartItem: InsertCartItem): Promise<CartItem>;
  updateCartItem(id: number, cartItem: Partial<InsertCartItem>): Promise<CartItem | undefined>;
  removeFromCart(id: number): Promise<boolean>;
  clearCart(customerId: string): Promise<boolean>;
  getCartItemById(id: number): Promise<CartItem | undefined>;

  // Chat session methods
  createChatSession(session: InsertChatSession): Promise<ChatSession>;
  getChatSession(sessionId: string): Promise<ChatSession | undefined>;
  getChatSessionsByCustomerId(customerId: string): Promise<ChatSession[]>;
  updateChatSession(sessionId: string, session: Partial<InsertChatSession>): Promise<ChatSession | undefined>;
  deleteChatSession(sessionId: string): Promise<boolean>;

  // Chat message methods
  addChatMessage(message: InsertChatMessage): Promise<ChatMessage>;
  getChatMessages(sessionId: string): Promise<ChatMessage[]>;
  getChatSessionWithMessages(sessionId: string): Promise<ChatSessionWithMessages | undefined>;
  deleteChatMessages(sessionId: string): Promise<boolean>;
}

// SQLite storage implementation
export class SQLiteStorage implements IStorage {
  async getAllCustomers(): Promise<Customer[]> {
    return await db.select().from(customers);
  }

  async getCustomerById(id: string): Promise<Customer | undefined> {
    const result = await db.select().from(customers).where(eq(customers.id, id));
    return result[0];
  }

  async createCustomer(customer: InsertCustomer): Promise<Customer> {
    const result = await db.insert(customers).values(customer).returning();
    return result[0];
  }

  async updateCustomer(id: string, customer: Partial<InsertCustomer>): Promise<Customer | undefined> {
    const result = await db.update(customers).set(customer).where(eq(customers.id, id)).returning();
    return result[0];
  }

  async deleteCustomer(id: string): Promise<boolean> {
    const result = await db.delete(customers).where(eq(customers.id, id));
    return result.changes > 0;
  }

  async getAllCustomerAddresses(): Promise<CustomerAddress[]> {
    return await db.select().from(customerAddresses);
  }

  async getCustomerAddresses(customerId: string): Promise<CustomerAddress[]> {
    return await db.select().from(customerAddresses).where(eq(customerAddresses.customerId, customerId));
  }

  async getCustomerAddressById(id: number): Promise<CustomerAddress | undefined> {
    const result = await db.select().from(customerAddresses).where(eq(customerAddresses.id, id));
    return result[0];
  }

  async createCustomerAddress(address: InsertCustomerAddress): Promise<CustomerAddress> {
    const result = await db.insert(customerAddresses).values(address).returning();
    return result[0];
  }

  async updateCustomerAddress(id: number, address: Partial<InsertCustomerAddress>): Promise<CustomerAddress | undefined> {
    const result = await db.update(customerAddresses).set(address).where(eq(customerAddresses.id, id)).returning();
    return result[0];
  }

  async deleteCustomerAddress(id: number): Promise<boolean> {
    const result = await db.delete(customerAddresses).where(eq(customerAddresses.id, id));
    return result.changes > 0;
  }

  async setDefaultAddress(customerId: string, addressId: number): Promise<boolean> {
    try {
      // First, unset all other default addresses for this customer
      await db.update(customerAddresses)
        .set({ isDefault: false })
        .where(eq(customerAddresses.customerId, customerId));
      
      // Then set the specified address as default
      const result = await db.update(customerAddresses)
        .set({ isDefault: true })
        .where(eq(customerAddresses.id, addressId));
      
      return result.changes > 0;
    } catch (error) {
      console.error('Error setting default address:', error);
      return false;
    }
  }

  async getAllCategories(): Promise<Category[]> {
    return await db.select().from(categories);
  }

  async getCategoryById(id: number): Promise<Category | undefined> {
    const result = await db.select().from(categories).where(eq(categories.id, id));
    return result[0];
  }

  async createCategory(category: InsertCategory): Promise<Category> {
    const result = await db.insert(categories).values(category).returning();
    return result[0];
  }

  async getAllProducts(): Promise<Product[]> {
    return await db.select().from(products);
  }

  async getProductById(id: string): Promise<Product | undefined> {
    const result = await db.select().from(products).where(eq(products.id, id));
    return result[0];
  }

  async getProductsByCategory(categoryId: number): Promise<Product[]> {
    return await db.select().from(products).where(eq(products.categoryId, categoryId));
  }

  async createProduct(product: InsertProduct): Promise<Product> {
    const result = await db.insert(products).values(product).returning();
    return result[0];
  }

  async updateProduct(id: string, product: Partial<InsertProduct>): Promise<Product | undefined> {
    const result = await db.update(products).set(product).where(eq(products.id, id)).returning();
    return result[0];
  }

  async getAllOrders(): Promise<Order[]> {
    return await db.select().from(orders);
  }

  async getOrdersByCustomerId(customerId: string): Promise<Order[]> {
    return await db.select().from(orders).where(eq(orders.customerId, customerId));
  }

  async getOrdersByCustomerIdWithItems(customerId: string): Promise<any[]> {
    const customerOrders = await this.getOrdersByCustomerId(customerId);
    
    // Get order items for each order
    const ordersWithItems = await Promise.all(
      customerOrders.map(async (order) => {
        const items = await this.getOrderItemsByOrderId(order.id);
        
        // Get product details for each item
        const itemsWithProducts = await Promise.all(
          items.map(async (item) => {
            const product = item.productId ? await this.getProductById(item.productId) : null;
            return { ...item, product };
          })
        );
        
        return { ...order, orderItems: itemsWithProducts };
      })
    );
    
    return ordersWithItems;
  }

  async getOrderById(id: string): Promise<Order | undefined> {
    const result = await db.select().from(orders).where(eq(orders.id, id));
    return result[0];
  }

  async createOrder(order: InsertOrder): Promise<Order> {
    const result = await db.insert(orders).values(order).returning();
    return result[0];
  }

  async updateOrder(id: string, order: Partial<InsertOrder>): Promise<Order | undefined> {
    const result = await db.update(orders).set(order).where(eq(orders.id, id)).returning();
    return result[0];
  }

  async deleteOrder(id: string): Promise<boolean> {
    const result = await db.delete(orders).where(eq(orders.id, id));
    return result.changes > 0;
  }

  async getAllOrderItems(): Promise<OrderItem[]> {
    return await db.select().from(orderItems);
  }

  async getOrderItemsByOrderId(orderId: string): Promise<OrderItem[]> {
    return await db.select().from(orderItems).where(eq(orderItems.orderId, orderId));
  }

  async createOrderItem(orderItem: InsertOrderItem): Promise<OrderItem> {
    const result = await db.insert(orderItems).values(orderItem).returning();
    return result[0];
  }

  async updateOrderItem(id: number, orderItem: Partial<InsertOrderItem>): Promise<OrderItem | undefined> {
    const result = await db.update(orderItems).set(orderItem).where(eq(orderItems.id, id)).returning();
    return result[0];
  }

  async deleteOrderItem(id: number): Promise<boolean> {
    const result = await db.delete(orderItems).where(eq(orderItems.id, id));
    return result.changes > 0;
  }

  async getCustomerWithRelations(id: string): Promise<any | undefined> {
    const customer = await this.getCustomerById(id);
    if (!customer) return undefined;

    const customerOrders = await this.getOrdersByCustomerId(id);
    
    // Get order items for each order
    const ordersWithItems = await Promise.all(
      customerOrders.map(async (order) => {
        const items = await this.getOrderItemsByOrderId(order.id);
        
        // Get product details for each item
        const itemsWithProducts = await Promise.all(
          items.map(async (item) => {
            const product = item.productId ? await this.getProductById(item.productId) : null;
            return { ...item, product };
          })
        );
        
        return { ...order, items: itemsWithProducts };
      })
    );

    return {
      ...customer,
      orders: ordersWithItems
    };
  }

  async getAllGiftCards(): Promise<GiftCard[]> {
    return await db.select().from(giftCards);
  }

  async getGiftCardByCode(code: string): Promise<GiftCard | undefined> {
    try {
      const result = await db.select().from(giftCards).where(eq(giftCards.code, code));
      return result[0];
    } catch (error) {
      console.error('Error fetching gift card:', error);
      return undefined;
    }
  }

  async createGiftCard(giftCard: InsertGiftCard): Promise<GiftCard> {
    const result = await db.insert(giftCards).values(giftCard).returning();
    return result[0];
  }

  async updateGiftCard(id: number, giftCard: Partial<InsertGiftCard>): Promise<GiftCard | undefined> {
    const result = await db.update(giftCards).set(giftCard).where(eq(giftCards.id, id)).returning();
    return result[0];
  }

  async updateGiftCardBalance(code: string, newBalance: number): Promise<GiftCard | undefined> {
    try {
      await db.update(giftCards).set({ balance: newBalance }).where(eq(giftCards.code, code));
      return await this.getGiftCardByCode(code);
    } catch (error) {
      console.error('Error updating gift card balance:', error);
      return undefined;
    }
  }

  async deleteGiftCard(id: number): Promise<boolean> {
    const result = await db.delete(giftCards).where(eq(giftCards.id, id));
    return result.changes > 0;
  }

  async updateCategory(id: number, category: Partial<InsertCategory>): Promise<Category | undefined> {
    const result = await db.update(categories).set(category).where(eq(categories.id, id)).returning();
    return result[0];
  }

  async deleteCategory(id: number): Promise<boolean> {
    const result = await db.delete(categories).where(eq(categories.id, id));
    return result.changes > 0;
  }

  async deleteProduct(id: string): Promise<boolean> {
    const result = await db.delete(products).where(eq(products.id, id));
    return result.changes > 0;
  }

  async returnOrder(orderId: string, returnReason: string): Promise<Order | undefined> {
    try {
      await db.update(orders).set({ 
        status: 'Returned',
        returnReason,
        returnDate: new Date().toISOString().split('T')[0],
        canReturn: false,
        canCancel: false
      }).where(eq(orders.id, orderId));
      return await this.getOrderById(orderId);
    } catch (error) {
      console.error('Error returning order:', error);
      return undefined;
    }
  }

  async cancelOrder(orderId: string): Promise<Order | undefined> {
    try {
      await db.update(orders).set({ 
        status: 'Cancelled',
        canReturn: false,
        canCancel: false
      }).where(eq(orders.id, orderId));
      return await this.getOrderById(orderId);
    } catch (error) {
      console.error('Error cancelling order:', error);
      return undefined;
    }
  }

  // Placeholder methods for GraphQL compatibility
  async getPlanByCustomerId(customerId: string): Promise<any> {
    return null; // Plans are not implemented in this database
  }

  async getPlanWithFeaturesByCustomerId(customerId: string): Promise<any> {
    return null; // Plans are not implemented in this database
  }

  async getDevicesByCustomerId(customerId: string): Promise<any[]> {
    return []; // Devices are not implemented in this database
  }

  async getPlanFeaturesByPlanId(planId: number): Promise<any[]> {
    return []; // Plan features are not implemented in this database
  }

  async getCartByCustomerId(customerId: string): Promise<CartItemWithProduct[]> {
    const cartData = await db.select().from(cartItems).where(eq(cartItems.customerId, customerId));
    
    const cartWithProducts = await Promise.all(
      cartData.map(async (item) => {
        const product = item.productId ? await this.getProductById(item.productId) : null;
        return { ...item, product } as CartItemWithProduct;
      })
    );
    
    return cartWithProducts.filter(item => item.product !== null);
  }

  async addToCart(cartItem: InsertCartItem): Promise<CartItem> {
    const existingItem = await db.select().from(cartItems)
      .where(and(
        eq(cartItems.customerId, cartItem.customerId!),
        eq(cartItems.productId, cartItem.productId!)
      ));

    if (existingItem.length > 0) {
      const updatedQuantity = existingItem[0].quantity + (cartItem.quantity || 1);
      const result = await db.update(cartItems)
        .set({ quantity: updatedQuantity })
        .where(eq(cartItems.id, existingItem[0].id))
        .returning();
      return result[0];
    } else {
      const cartItemWithDate = {
        ...cartItem,
        addedDate: cartItem.addedDate || new Date().toISOString().split('T')[0]
      };
      const result = await db.insert(cartItems).values(cartItemWithDate).returning();
      return result[0];
    }
  }

  async updateCartItem(id: number, cartItem: Partial<InsertCartItem>): Promise<CartItem | undefined> {
    const result = await db.update(cartItems).set(cartItem).where(eq(cartItems.id, id)).returning();
    return result[0];
  }

  async removeFromCart(id: number): Promise<boolean> {
    const result = await db.delete(cartItems).where(eq(cartItems.id, id));
    return result.changes > 0;
  }

  async clearCart(customerId: string): Promise<boolean> {
    const result = await db.delete(cartItems).where(eq(cartItems.customerId, customerId));
    return result.changes > 0;
  }

  async getCartItemById(id: number): Promise<CartItem | undefined> {
    const result = await db.select().from(cartItems).where(eq(cartItems.id, id));
    return result[0];
  }

  // Chat session methods implementation
  async createChatSession(session: InsertChatSession): Promise<ChatSession> {
    const sessionWithDates = {
      ...session,
      createdDate: session.createdDate || new Date().toISOString(),
      updatedDate: session.updatedDate || new Date().toISOString()
    };
    const result = await db.insert(chatSessions).values(sessionWithDates).returning();
    return result[0];
  }

  async getChatSession(sessionId: string): Promise<ChatSession | undefined> {
    const result = await db.select().from(chatSessions).where(eq(chatSessions.id, sessionId));
    return result[0];
  }

  async getChatSessionsByCustomerId(customerId: string): Promise<ChatSession[]> {
    return await db.select().from(chatSessions)
      .where(eq(chatSessions.customerId, customerId))
      .orderBy(desc(chatSessions.updatedDate));
  }

  async updateChatSession(sessionId: string, session: Partial<InsertChatSession>): Promise<ChatSession | undefined> {
    const sessionWithUpdatedDate = {
      ...session,
      updatedDate: new Date().toISOString()
    };
    const result = await db.update(chatSessions)
      .set(sessionWithUpdatedDate)
      .where(eq(chatSessions.id, sessionId))
      .returning();
    return result[0];
  }

  async deleteChatSession(sessionId: string): Promise<boolean> {
    const result = await db.delete(chatSessions).where(eq(chatSessions.id, sessionId));
    return result.changes > 0;
  }

  // Chat message methods implementation
  async addChatMessage(message: InsertChatMessage): Promise<ChatMessage> {
    const messageWithTimestamp = {
      ...message,
      timestamp: message.timestamp || new Date().toISOString()
    };
    const result = await db.insert(chatMessages).values(messageWithTimestamp).returning();
    
    // Update session's updated date
    await this.updateChatSession(message.sessionId!, {});
    
    return result[0];
  }

  async getChatMessages(sessionId: string): Promise<ChatMessage[]> {
    return await db.select().from(chatMessages)
      .where(eq(chatMessages.sessionId, sessionId))
      .orderBy(chatMessages.timestamp);
  }

  async getChatSessionWithMessages(sessionId: string): Promise<ChatSessionWithMessages | undefined> {
    const session = await this.getChatSession(sessionId);
    if (!session) return undefined;

    const messages = await this.getChatMessages(sessionId);
    return { ...session, messages };
  }

  async deleteChatMessages(sessionId: string): Promise<boolean> {
    const result = await db.delete(chatMessages).where(eq(chatMessages.sessionId, sessionId));
    return result.changes > 0;
  }
}

export const storage = new SQLiteStorage();