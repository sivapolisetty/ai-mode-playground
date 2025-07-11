import { sqliteTable, text, integer, real } from "drizzle-orm/sqlite-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Customer table definition
export const customers = sqliteTable("customers", {
  id: text("id").primaryKey(), // CUST-XXX format
  name: text("name").notNull(),
  email: text("email").notNull(),
  phone: text("phone").notNull(),
  address: text("address").notNull(),
  dob: text("dob").notNull(),
  registrationDate: text("registration_date").notNull(),
  status: text("status").notNull(), // 'Active', 'Inactive', etc.
});

// Categories table definition
export const categories = sqliteTable("categories", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  name: text("name").notNull(), // Electronics, Clothing, Footwear
  description: text("description").notNull(),
  imageUrl: text("image_url"),
});

// Products table definition
export const products = sqliteTable("products", {
  id: text("id").primaryKey(), // PROD-XXX format
  categoryId: integer("category_id").references(() => categories.id, { onDelete: "cascade" }),
  name: text("name").notNull(),
  description: text("description").notNull(),
  price: real("price").notNull(),
  imageUrl: text("image_url"),
  brand: text("brand"),
  model: text("model"),
  color: text("color"),
  size: text("size"), // For clothing and footwear
  specifications: text("specifications"), // JSON string for electronics specs
  stockQuantity: integer("stock_quantity").notNull().default(0),
  isActive: integer("is_active", { mode: "boolean" }).notNull().default(true),
});

// Order items table definition (for multiple products per order)
export const orderItems = sqliteTable("order_items", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  orderId: text("order_id").references(() => orders.id, { onDelete: "cascade" }),
  productId: text("product_id").references(() => products.id, { onDelete: "cascade" }),
  quantity: integer("quantity").notNull(),
  price: real("price").notNull(), // Price at time of order
  selectedSize: text("selected_size"), // For clothing/footwear
  selectedColor: text("selected_color"), // For all products
  selectedConfiguration: text("selected_configuration"), // JSON for electronics (memory, storage, etc.)
});

// Customer addresses table definition
export const customerAddresses = sqliteTable("customer_addresses", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  customerId: text("customer_id").references(() => customers.id, { onDelete: "cascade" }),
  label: text("label").notNull(), // e.g., "Home", "Work", "Billing"
  recipientName: text("recipient_name").notNull(),
  addressLine1: text("address_line1").notNull(),
  addressLine2: text("address_line2"),
  city: text("city").notNull(),
  state: text("state").notNull(),
  zipCode: text("zip_code").notNull(),
  country: text("country").notNull().default("USA"),
  phone: text("phone"),
  isDefault: integer("is_default", { mode: "boolean" }).notNull().default(false),
  isActive: integer("is_active", { mode: "boolean" }).notNull().default(true),
  createdDate: text("created_date").notNull(),
});

// Gift cards table definition
export const giftCards = sqliteTable("gift_cards", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  code: text("code").notNull().unique(),
  balance: real("balance").notNull(),
  originalAmount: real("original_amount").notNull(),
  isActive: integer("is_active", { mode: "boolean" }).notNull().default(true),
  expiryDate: text("expiry_date"),
  createdDate: text("created_date").notNull(),
});

// Cart items table definition
export const cartItems = sqliteTable("cart_items", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  customerId: text("customer_id").references(() => customers.id, { onDelete: "cascade" }),
  productId: text("product_id").references(() => products.id, { onDelete: "cascade" }),
  quantity: integer("quantity").notNull().default(1),
  selectedSize: text("selected_size"),
  selectedColor: text("selected_color"),
  selectedConfiguration: text("selected_configuration"), // JSON for electronics (memory, storage, etc.)
  addedDate: text("added_date").notNull(),
});

// Chat sessions table definition
export const chatSessions = sqliteTable("chat_sessions", {
  id: text("id").primaryKey(), // UUID format
  customerId: text("customer_id").references(() => customers.id, { onDelete: "cascade" }),
  title: text("title"), // Optional session title
  createdDate: text("created_date").notNull(),
  updatedDate: text("updated_date").notNull(),
  isActive: integer("is_active", { mode: "boolean" }).notNull().default(true),
});

// Chat messages table definition
export const chatMessages = sqliteTable("chat_messages", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  sessionId: text("session_id").references(() => chatSessions.id, { onDelete: "cascade" }),
  messageType: text("message_type").notNull(), // 'user' | 'assistant'
  content: text("content").notNull(),
  timestamp: text("timestamp").notNull(),
  metadata: text("metadata"), // JSON for additional data like tool calls, debug info, etc.
});

// Orders table definition
export const orders = sqliteTable("orders", {
  id: text("id").primaryKey(), // ORD-YYYY-XXXX format
  customerId: text("customer_id").references(() => customers.id, { onDelete: "cascade" }),
  orderDate: text("order_date").notNull(),
  totalAmount: real("total_amount").notNull(),
  status: text("status").notNull(), // 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned'
  shippingAddress: text("shipping_address").notNull(),
  paymentMethod: text("payment_method").notNull(), // 'Credit Card', 'PayPal', 'Cash on Delivery', 'Gift Card'
  trackingNumber: text("tracking_number"),
  giftCardCode: text("gift_card_code"), // For gift card payments
  returnReason: text("return_reason"), // For returned orders
  returnDate: text("return_date"), // When the return was processed
  canReturn: integer("can_return", { mode: "boolean" }).notNull(), // Whether order can be returned
  canCancel: integer("can_cancel", { mode: "boolean" }).notNull(), // Whether order can be cancelled
});

// Insert schemas for each table
export const insertCustomerSchema = createInsertSchema(customers);
export const insertCategorySchema = createInsertSchema(categories);
export const insertProductSchema = createInsertSchema(products);
export const insertOrderSchema = createInsertSchema(orders);
export const insertOrderItemSchema = createInsertSchema(orderItems);
export const insertCustomerAddressSchema = createInsertSchema(customerAddresses);
export const insertGiftCardSchema = createInsertSchema(giftCards);
export const insertCartItemSchema = createInsertSchema(cartItems);
export const insertChatSessionSchema = createInsertSchema(chatSessions);
export const insertChatMessageSchema = createInsertSchema(chatMessages);

// Types for each table
export type InsertCustomer = z.infer<typeof insertCustomerSchema>;
export type Customer = typeof customers.$inferSelect;

export type InsertCategory = z.infer<typeof insertCategorySchema>;
export type Category = typeof categories.$inferSelect;

export type InsertProduct = z.infer<typeof insertProductSchema>;
export type Product = typeof products.$inferSelect;

export type InsertOrder = z.infer<typeof insertOrderSchema>;
export type Order = typeof orders.$inferSelect;

export type InsertOrderItem = z.infer<typeof insertOrderItemSchema>;
export type OrderItem = typeof orderItems.$inferSelect;

export type InsertCustomerAddress = z.infer<typeof insertCustomerAddressSchema>;
export type CustomerAddress = typeof customerAddresses.$inferSelect;

export type InsertGiftCard = z.infer<typeof insertGiftCardSchema>;
export type GiftCard = typeof giftCards.$inferSelect;

export type InsertCartItem = z.infer<typeof insertCartItemSchema>;
export type CartItem = typeof cartItems.$inferSelect;

export type InsertChatSession = z.infer<typeof insertChatSessionSchema>;
export type ChatSession = typeof chatSessions.$inferSelect;

export type InsertChatMessage = z.infer<typeof insertChatMessageSchema>;
export type ChatMessage = typeof chatMessages.$inferSelect;

// Customer with relationships
export type CustomerWithRelations = Customer & {
  orders?: (Order & { items?: (OrderItem & { product?: Product })[] })[];
  addresses?: CustomerAddress[];
};

// Order with relationships
export type OrderWithItems = Order & {
  items: (OrderItem & { product: Product })[];
};

// Cart item with product relationship
export type CartItemWithProduct = CartItem & {
  product: Product;
};

// Chat session with messages relationship
export type ChatSessionWithMessages = ChatSession & {
  messages: ChatMessage[];
};
