import { db } from './index.js';
import { categories, products, customers, orders, orderItems, giftCards, customerAddresses } from '../../shared/schema.js';
import type { InsertCategory, InsertProduct, InsertCustomer, InsertOrder, InsertOrderItem, InsertGiftCard, InsertCustomerAddress } from '../../shared/schema.js';

export async function seedEcommerceDatabase() {
  console.log("Seeding ecommerce database with products and orders...");

  // Create 3 categories
  const categoriesData: InsertCategory[] = [
    {
      id: 1,
      name: "Electronics",
      description: "Latest technology and gadgets"
    },
    {
      id: 2,
      name: "Clothing",
      description: "Fashion and apparel for all occasions"
    },
    {
      id: 3,
      name: "Footwear",
      description: "Shoes and sneakers for every style"
    }
  ];

  // Insert categories
  for (const category of categoriesData) {
    await db.insert(categories).values(category);
  }

  const electronicsCategory = categoriesData[0];
  const clothingCategory = categoriesData[1];
  const footwearCategory = categoriesData[2];

  // Create 15 products (5 per category)
  const productsData: InsertProduct[] = [
    // Electronics
    {
      id: "PROD-001",
      categoryId: electronicsCategory.id,
      name: "iPhone 15 Pro",
      description: "Latest iPhone with titanium design and A17 Pro chip",
      price: 999.99,
      imageUrl: "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop",
      brand: "Apple",
      model: "iPhone 15 Pro",
      color: "Natural Titanium",
      specifications: JSON.stringify({
        display: "6.1-inch Super Retina XDR",
        processor: "A17 Pro chip",
        storage: "128GB",
        camera: "48MP Main + 12MP Ultra Wide + 12MP Telephoto"
      }),
      stockQuantity: 50,
      isActive: true
    },
    {
      id: "PROD-002",
      categoryId: electronicsCategory.id,
      name: "MacBook Air M2",
      description: "Supercharged by M2 chip with 13.6-inch Liquid Retina display",
      price: 1199.99,
      imageUrl: "https://images.unsplash.com/photo-1541807084-5c52b6b3adef?w=400&h=400&fit=crop",
      brand: "Apple",
      model: "MacBook Air",
      color: "Space Gray",
      specifications: JSON.stringify({
        display: "13.6-inch Liquid Retina",
        processor: "Apple M2 chip",
        memory: "8GB unified memory",
        storage: "256GB SSD"
      }),
      stockQuantity: 25,
      isActive: true
    },
    {
      id: "PROD-003",
      categoryId: electronicsCategory.id,
      name: "Samsung Galaxy S24",
      description: "AI-powered smartphone with advanced camera system",
      price: 799.99,
      imageUrl: "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400&h=400&fit=crop",
      brand: "Samsung",
      model: "Galaxy S24",
      color: "Phantom Black",
      specifications: JSON.stringify({
        display: "6.2-inch Dynamic AMOLED 2X",
        processor: "Snapdragon 8 Gen 3",
        storage: "128GB",
        camera: "50MP Triple Camera",
        battery: "3900mAh"
      }),
      stockQuantity: 35,
      isActive: true
    },
    {
      id: "PROD-004",
      categoryId: electronicsCategory.id,
      name: "iPad Pro 11-inch",
      description: "Professional tablet with M2 chip and Liquid Retina display",
      price: 799.99,
      imageUrl: "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop",
      brand: "Apple",
      model: "iPad Pro",
      color: "Silver",
      specifications: JSON.stringify({
        display: "11-inch Liquid Retina",
        processor: "Apple M2 chip",
        storage: "128GB",
        camera: "12MP Wide + 10MP Ultra Wide"
      }),
      stockQuantity: 20,
      isActive: true
    },
    {
      id: "PROD-005",
      categoryId: electronicsCategory.id,
      name: "Sony WH-1000XM4",
      description: "Industry-leading noise canceling wireless headphones",
      price: 349.99,
      imageUrl: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop",
      brand: "Sony",
      model: "WH-1000XM4",
      color: "Black",
      specifications: JSON.stringify({
        battery: "30 hours",
        connectivity: "Bluetooth 5.0",
        features: "Active Noise Cancellation",
        weight: "254g"
      }),
      stockQuantity: 40,
      isActive: true
    },
    // Clothing
    {
      id: "PROD-006",
      categoryId: clothingCategory.id,
      name: "Levi's 501 Original Jeans",
      description: "Classic straight fit jeans with authentic details",
      price: 89.99,
      imageUrl: "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop",
      brand: "Levi's",
      color: "Indigo Blue",
      size: "32W x 32L",
      stockQuantity: 60,
      isActive: true
    },
    {
      id: "PROD-007",
      categoryId: clothingCategory.id,
      name: "Nike Dri-FIT T-Shirt",
      description: "Moisture-wicking athletic t-shirt for active lifestyle",
      price: 29.99,
      imageUrl: "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop",
      brand: "Nike",
      color: "Black",
      size: "Large",
      stockQuantity: 100,
      isActive: true
    },
    {
      id: "PROD-008",
      categoryId: clothingCategory.id,
      name: "Adidas Hoodie",
      description: "Comfortable cotton blend hoodie with kangaroo pocket",
      price: 69.99,
      imageUrl: "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop",
      brand: "Adidas",
      color: "Navy Blue",
      size: "Medium",
      stockQuantity: 45,
      isActive: true
    },
    {
      id: "PROD-009",
      categoryId: clothingCategory.id,
      name: "H&M Dress Shirt",
      description: "Professional cotton dress shirt for business attire",
      price: 39.99,
      imageUrl: "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=400&fit=crop",
      brand: "H&M",
      color: "White",
      size: "Large",
      stockQuantity: 30,
      isActive: true
    },
    {
      id: "PROD-010",
      categoryId: clothingCategory.id,
      name: "Zara Blazer",
      description: "Elegant blazer perfect for formal occasions",
      price: 129.99,
      imageUrl: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=400&h=400&fit=crop",
      brand: "Zara",
      color: "Navy",
      size: "Medium",
      stockQuantity: 25,
      isActive: true
    },
    // Footwear
    {
      id: "PROD-011",
      categoryId: footwearCategory.id,
      name: "Nike Air Max 270",
      description: "Lifestyle shoes with visible Max Air cushioning",
      price: 149.99,
      imageUrl: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop",
      brand: "Nike",
      color: "Black/White",
      size: "10",
      stockQuantity: 40,
      isActive: true
    },
    {
      id: "PROD-012",
      categoryId: footwearCategory.id,
      name: "Adidas Ultraboost 22",
      description: "High-performance running shoes with Boost midsole",
      price: 189.99,
      imageUrl: "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=400&h=400&fit=crop",
      brand: "Adidas",
      color: "Core Black",
      size: "9.5",
      stockQuantity: 35,
      isActive: true
    },
    {
      id: "PROD-013",
      categoryId: footwearCategory.id,
      name: "Converse Chuck Taylor",
      description: "Classic canvas sneakers with iconic design",
      price: 59.99,
      imageUrl: "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop",
      brand: "Converse",
      color: "White",
      size: "8.5",
      stockQuantity: 55,
      isActive: true
    },
    {
      id: "PROD-014",
      categoryId: footwearCategory.id,
      name: "Dr. Martens 1460 Boots",
      description: "Iconic leather boots with air-cushioned sole",
      price: 169.99,
      imageUrl: "https://images.unsplash.com/photo-1544966503-7cc5ac882d5e?w=400&h=400&fit=crop",
      brand: "Dr. Martens",
      color: "Black",
      size: "9",
      stockQuantity: 30,
      isActive: true
    },
    {
      id: "PROD-015",
      categoryId: footwearCategory.id,
      name: "Vans Old Skool",
      description: "Classic skate shoes with signature side stripe",
      price: 64.99,
      imageUrl: "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&h=400&fit=crop",
      brand: "Vans",
      color: "Black/White",
      size: "10.5",
      stockQuantity: 50,
      isActive: true
    }
  ];

  // Insert products
  for (const product of productsData) {
    await db.insert(products).values(product);
  }

  // Create 5 customers
  const customersData: InsertCustomer[] = [
    {
      id: "CUST-001",
      name: "Sarah Johnson",
      email: "sarah.johnson@email.com",
      phone: "+1 (555) 123-4567",
      address: "123 Oak Street, San Francisco, CA 94102",
      dob: "March 15, 1990",
      registrationDate: "January 12, 2023",
      status: "Active"
    },
    {
      id: "CUST-002",
      name: "Michael Chen",
      email: "michael.chen@email.com",
      phone: "+1 (555) 234-5678",
      address: "456 Pine Avenue, Seattle, WA 98101",
      dob: "July 22, 1988",
      registrationDate: "February 8, 2023",
      status: "Active"
    },
    {
      id: "CUST-003",
      name: "Emily Rodriguez",
      email: "emily.rodriguez@email.com",
      phone: "+1 (555) 345-6789",
      address: "789 Maple Drive, Austin, TX 78701",
      dob: "November 5, 1992",
      registrationDate: "March 20, 2023",
      status: "Active"
    },
    {
      id: "CUST-004",
      name: "David Thompson",
      email: "david.thompson@email.com",
      phone: "+1 (555) 456-7890",
      address: "321 Cedar Lane, Denver, CO 80201",
      dob: "September 12, 1985",
      registrationDate: "April 15, 2023",
      status: "Active"
    },
    {
      id: "CUST-005",
      name: "Jessica Wilson",
      email: "jessica.wilson@email.com",
      phone: "+1 (555) 567-8901",
      address: "654 Elm Street, Miami, FL 33101",
      dob: "December 28, 1991",
      registrationDate: "May 10, 2023",
      status: "Active"
    }
  ];

  // Insert customers
  for (const customer of customersData) {
    await db.insert(customers).values(customer);
  }

  // Create customer addresses - multiple addresses per customer
  const customerAddressesData: InsertCustomerAddress[] = [
    // Sarah Johnson (CUST-001) addresses
    {
      customerId: "CUST-001",
      label: "Home",
      recipientName: "Sarah Johnson",
      addressLine1: "123 Oak Street",
      addressLine2: "Apartment 4B",
      city: "San Francisco",
      state: "CA",
      zipCode: "94102",
      country: "USA",
      phone: "+1 (555) 123-4567",
      isDefault: true,
      isActive: true,
      createdDate: "2023-01-12"
    },
    {
      customerId: "CUST-001",
      label: "Work",
      recipientName: "Sarah Johnson",
      addressLine1: "456 Market Street",
      addressLine2: "Suite 1200",
      city: "San Francisco",
      state: "CA",
      zipCode: "94105",
      country: "USA",
      phone: "+1 (555) 987-6543",
      isDefault: false,
      isActive: true,
      createdDate: "2023-02-15"
    },
    // Michael Chen (CUST-002) addresses
    {
      customerId: "CUST-002",
      label: "Home",
      recipientName: "Michael Chen",
      addressLine1: "456 Pine Avenue",
      addressLine2: "",
      city: "Seattle",
      state: "WA",
      zipCode: "98101",
      country: "USA",
      phone: "+1 (555) 234-5678",
      isDefault: true,
      isActive: true,
      createdDate: "2023-02-08"
    },
    {
      customerId: "CUST-002",
      label: "Parents House",
      recipientName: "Michael Chen",
      addressLine1: "789 Cherry Blossom Lane",
      addressLine2: "",
      city: "Bellevue",
      state: "WA",
      zipCode: "98004",
      country: "USA",
      phone: "+1 (555) 234-5678",
      isDefault: false,
      isActive: true,
      createdDate: "2023-03-01"
    },
    // Emily Rodriguez (CUST-003) addresses
    {
      customerId: "CUST-003",
      label: "Home",
      recipientName: "Emily Rodriguez",
      addressLine1: "789 Maple Drive",
      addressLine2: "",
      city: "Austin",
      state: "TX",
      zipCode: "78701",
      country: "USA",
      phone: "+1 (555) 345-6789",
      isDefault: true,
      isActive: true,
      createdDate: "2023-03-20"
    },
    {
      customerId: "CUST-003",
      label: "Office",
      recipientName: "Emily Rodriguez",
      addressLine1: "321 Business Plaza",
      addressLine2: "Floor 8",
      city: "Austin",
      state: "TX",
      zipCode: "78702",
      country: "USA",
      phone: "+1 (555) 345-6789",
      isDefault: false,
      isActive: true,
      createdDate: "2023-04-05"
    },
    // David Thompson (CUST-004) addresses
    {
      customerId: "CUST-004",
      label: "Home",
      recipientName: "David Thompson",
      addressLine1: "321 Cedar Lane",
      addressLine2: "",
      city: "Denver",
      state: "CO",
      zipCode: "80201",
      country: "USA",
      phone: "+1 (555) 456-7890",
      isDefault: true,
      isActive: true,
      createdDate: "2023-04-15"
    },
    {
      customerId: "CUST-004",
      label: "Office",
      recipientName: "David Thompson",
      addressLine1: "1500 17th Street",
      addressLine2: "Suite 900",
      city: "Denver",
      state: "CO",
      zipCode: "80202",
      country: "USA",
      phone: "+1 (555) 456-7890",
      isDefault: false,
      isActive: true,
      createdDate: "2023-05-01"
    },
    // Jessica Wilson (CUST-005) addresses
    {
      customerId: "CUST-005",
      label: "Home",
      recipientName: "Jessica Wilson",
      addressLine1: "654 Elm Street",
      addressLine2: "",
      city: "Miami",
      state: "FL",
      zipCode: "33101",
      country: "USA",
      phone: "+1 (555) 567-8901",
      isDefault: true,
      isActive: true,
      createdDate: "2023-05-10"
    },
    {
      customerId: "CUST-005",
      label: "Beach House",
      recipientName: "Jessica Wilson",
      addressLine1: "987 Ocean Drive",
      addressLine2: "",
      city: "Miami Beach",
      state: "FL",
      zipCode: "33139",
      country: "USA",
      phone: "+1 (555) 567-8901",
      isDefault: false,
      isActive: true,
      createdDate: "2023-06-01"
    }
  ];

  // Insert customer addresses
  for (const address of customerAddressesData) {
    await db.insert(customerAddresses).values(address);
  }

  // Create gift cards for testing
  const giftCardsData = [
    {
      code: "GC-HOLIDAY2024",
      balance: 250.00,
      originalAmount: 250.00,
      isActive: true,
      expiryDate: "2025-12-31",
      createdDate: "2024-11-01"
    },
    {
      code: "GC-SNEAKER50",
      balance: 75.00,
      originalAmount: 100.00,
      isActive: true,
      expiryDate: "2025-06-30",
      createdDate: "2024-10-15"
    }
  ];

  // Insert gift cards
  for (const giftCard of giftCardsData) {
    await db.insert(giftCards).values(giftCard as InsertGiftCard);
  }

  // Create realistic ecommerce orders with actual products
  const ordersData: InsertOrder[] = [
    // Sarah Johnson's orders (CUST-001) - Tech enthusiast
    {
      id: "ORD-2024-001",
      customerId: "CUST-001",
      orderDate: "2024-12-15",
      totalAmount: 1349.98,
      status: "Delivered",
      shippingAddress: "123 Oak Street, San Francisco, CA 94102",
      paymentMethod: "Credit Card",
      trackingNumber: "1Z999AA1234567890",
      canReturn: true,
      canCancel: false
    },
    {
      id: "ORD-2024-002",
      customerId: "CUST-001",
      orderDate: "2024-11-20",
      totalAmount: 349.99,
      status: "Delivered",
      shippingAddress: "123 Oak Street, San Francisco, CA 94102",
      paymentMethod: "PayPal",
      trackingNumber: "1Z999AA1234567891",
      canReturn: true,
      canCancel: false
    },
    // Michael Chen's orders (CUST-002) - Mixed interests
    {
      id: "ORD-2024-003",
      customerId: "CUST-002",
      orderDate: "2024-12-10",
      totalAmount: 999.99,
      status: "Delivered",
      shippingAddress: "456 Pine Avenue, Seattle, WA 98101",
      paymentMethod: "Credit Card",
      trackingNumber: "1Z999BB1234567893",
      canReturn: true,
      canCancel: false
    },
    {
      id: "ORD-2024-004",
      customerId: "CUST-002",
      orderDate: "2024-11-28",
      totalAmount: 69.99,
      status: "Delivered",
      shippingAddress: "456 Pine Avenue, Seattle, WA 98101",
      paymentMethod: "PayPal",
      trackingNumber: "1Z999BB1234567894",
      canReturn: true,
      canCancel: false
    },
    {
      id: "ORD-2024-005",
      customerId: "CUST-003",
      orderDate: "2024-12-05",
      totalAmount: 219.98,
      status: "Delivered",
      shippingAddress: "789 Maple Drive, Austin, TX 78701",
      paymentMethod: "Credit Card",
      trackingNumber: "1Z999CC1234567895",
      canReturn: true,
      canCancel: false
    },
    {
      id: "ORD-2024-006",
      customerId: "CUST-004",
      orderDate: "2024-11-15",
      totalAmount: 149.99,
      status: "Delivered",
      shippingAddress: "321 Cedar Lane, Denver, CO 80201",
      paymentMethod: "Gift Card",
      trackingNumber: "1Z999DD1234567901",
      giftCardCode: "GC-SNEAKER50",
      canReturn: true,
      canCancel: false
    },
    {
      id: "ORD-2024-007",
      customerId: "CUST-005",
      orderDate: "2024-12-01",
      totalAmount: 999.99,
      status: "Delivered",
      shippingAddress: "654 Elm Street, Miami, FL 33101",
      paymentMethod: "Credit Card",
      trackingNumber: "1Z999EE1234567904",
      canReturn: true,
      canCancel: false
    }
  ];

  // Insert orders
  for (const order of ordersData) {
    await db.insert(orders).values(order);
  }

  // Create realistic order items matching actual products
  const orderItemsData: InsertOrderItem[] = [
    // Order ORD-2024-001 (Sarah): iPhone 15 Pro + Sony Headphones
    { orderId: "ORD-2024-001", productId: "PROD-001", quantity: 1, price: 999.99 },
    { orderId: "ORD-2024-001", productId: "PROD-005", quantity: 1, price: 349.99 },
    
    // Order ORD-2024-002 (Sarah): Sony Headphones
    { orderId: "ORD-2024-002", productId: "PROD-005", quantity: 1, price: 349.99 },
    
    // Order ORD-2024-003 (Michael): iPhone 15 Pro
    { orderId: "ORD-2024-003", productId: "PROD-001", quantity: 1, price: 999.99 },
    
    // Order ORD-2024-004 (Michael): Adidas Hoodie  
    { orderId: "ORD-2024-004", productId: "PROD-008", quantity: 1, price: 69.99 },
    
    // Order ORD-2024-005 (Emily): Levi's Jeans + Zara Blazer
    { orderId: "ORD-2024-005", productId: "PROD-006", quantity: 1, price: 89.99 },
    { orderId: "ORD-2024-005", productId: "PROD-010", quantity: 1, price: 129.99 },
    
    // Order ORD-2024-006 (David): Nike Air Max
    { orderId: "ORD-2024-006", productId: "PROD-011", quantity: 1, price: 149.99 },
    
    // Order ORD-2024-007 (Jessica): iPhone 15 Pro
    { orderId: "ORD-2024-007", productId: "PROD-001", quantity: 1, price: 999.99 }
  ];

  // Insert order items
  for (const orderItem of orderItemsData) {
    await db.insert(orderItems).values(orderItem);
  }

  console.log("Ecommerce database seeded successfully!");
  console.log("- 3 categories (Electronics, Clothing, Footwear)");
  console.log("- 15 products across all categories");
  console.log("- 5 customers");
  console.log("- 7 realistic orders with actual products");
  console.log("- 9 order items");
}