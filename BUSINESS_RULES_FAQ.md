# Business Rules FAQ - ShopHub E-commerce Platform

## Table of Contents
1. [Customer Management](#customer-management)
2. [Product Catalog](#product-catalog)
3. [Order Management](#order-management)
4. [Address Management](#address-management)
5. [Gift Cards](#gift-cards)
6. [Payment Processing](#payment-processing)
7. [Inventory Management](#inventory-management)
8. [Returns and Cancellations](#returns-and-cancellations)
9. [System Administration](#system-administration)
10. [Technical Limitations](#technical-limitations)

---

## Customer Management

### Q: What information is required to create a customer account?
**A:** The following fields are mandatory for customer registration:
- Full Name
- Email Address (must be valid format)
- Phone Number
- Physical Address
- Date of Birth
- Registration Date (automatically set)
- Account Status (Active/Inactive)

### Q: What customer ID format is used?
**A:** Customer IDs follow the format `CUST-XXX` (e.g., `CUST-001`, `CUST-002`). These are assigned automatically during registration.

### Q: Can customers update their profile information?
**A:** Yes, customers can update most profile fields including name, email, phone, and date of birth. Updates are validated against the system schema to ensure data integrity.

### Q: What account statuses are available?
**A:** Customers can have two statuses:
- **Active**: Customer can place orders and access all features
- **Inactive**: Customer account is disabled

### Q: Can a customer have multiple email addresses?
**A:** No, each customer account is associated with a single email address that serves as the primary identifier.

---

## Product Catalog

### Q: What product categories are available?
**A:** The system supports three main categories:
1. **Electronics** - Computers, phones, gadgets
2. **Clothing** - Apparel and accessories
3. **Footwear** - Shoes and related items

### Q: How are product IDs assigned?
**A:** Product IDs use the format `PROD-XXX` (e.g., `PROD-001`) and are automatically generated when products are added to the catalog.

### Q: What product information is tracked?
**A:** Each product includes:
- **Required**: Category, Name, Description, Price
- **Optional**: Brand, Model, Color, Size, Image URL
- **Inventory**: Stock Quantity, Active Status
- **Specifications**: JSON format for detailed specs (electronics)

### Q: How is product pricing handled?
**A:** Prices are stored as real numbers (decimals) and must be positive values. The system doesn't currently support multiple currencies - USD is assumed.

### Q: Can products be temporarily disabled?
**A:** Yes, products have an `isActive` flag. When set to `false`, the product is effectively disabled without being deleted from the system.

### Q: How are product variations handled?
**A:** The system supports:
- **Size**: Text field for clothing/footwear (e.g., "Large", "32W x 32L", "10")
- **Color**: Available for all product types
- **Specifications**: JSON format for electronics (memory, storage, processor, etc.)

---

## Order Management

### Q: How are order IDs generated?
**A:** Order IDs use the format `ORD-{timestamp}` (e.g., `ORD-1734567890123`) and are automatically generated when orders are created.

### Q: What information is required to place an order?
**A:** Orders require:
- **Customer ID** (must be valid customer)
- **Items Array** (cannot be empty)
- Order Date
- Total Amount
- Status
- Shipping Address
- Payment Method

### Q: What order statuses are available?
**A:** Orders can have the following statuses:
- **Pending**: Order received, awaiting processing
- **Processing**: Order being prepared
- **Shipped**: Order dispatched to customer
- **Delivered**: Order received by customer
- **Cancelled**: Order cancelled
- **Returned**: Order returned by customer

### Q: How are tracking numbers assigned?
**A:** Tracking numbers are automatically generated using the pattern: `1Z999{last3CustomerID}{last6Timestamp}` (e.g., `1Z999001567890`)

### Q: Can orders be modified after creation?
**A:** No, orders cannot be modified after creation. Customers must cancel and reorder if changes are needed.

### Q: What payment methods are supported?
**A:** The system accepts:
- Credit Card
- PayPal
- Cash on Delivery
- Gift Card

---

## Address Management

### Q: Can customers have multiple addresses?
**A:** Yes, customers can maintain multiple addresses with different labels (Home, Work, Office, Billing, etc.).

### Q: What information is required for an address?
**A:** Required address fields:
- Address Label (e.g., "Home", "Work")
- Recipient Name
- Address Line 1
- City
- State
- ZIP Code
- Country (defaults to "USA")

Optional fields:
- Address Line 2
- Phone Number

### Q: How does the default address system work?
**A:** Each customer can have one default address. When a new address is set as default, the previous default address is automatically updated. This ensures only one default address per customer.

### Q: Can addresses be deleted?
**A:** Yes, addresses can be deleted, but the system uses soft deletion by marking them as inactive (`isActive = false`) rather than removing them completely.

### Q: Are there restrictions on address labels?
**A:** No, address labels are free-text fields, but common labels include "Home", "Work", "Office", "Billing", etc.

---

## Gift Cards

### Q: What gift card formats are supported?
**A:** Gift card codes follow patterns like:
- `GC-HOLIDAY2024`
- `GC-SNEAKER50`
- `GC-WELCOME100`

### Q: How is gift card validation performed?
**A:** Gift cards are validated by checking:
1. **Code exists** in the system
2. **Active status** (`isActive = true`)
3. **Sufficient balance** for the purchase
4. **Not expired** (if expiry date is set)

### Q: Can gift cards be used for partial payments?
**A:** Yes, gift cards can be used for partial payments. The system calculates the discount as the minimum of the gift card balance and the order total.

### Q: How is gift card balance managed?
**A:** Each gift card tracks:
- **Current Balance**: Amount available for use
- **Original Amount**: Initial gift card value
- **Status**: Active/Inactive flag
- **Expiry Date**: Optional expiration date

### Q: What happens to gift card balance after use?
**A:** Currently, the system stores the gift card code with the order but doesn't automatically reduce the balance. Balance management would need to be implemented separately.

---

## Payment Processing

### Q: How are payments validated?
**A:** Payment validation includes:
- **Amount validation**: Total must be positive
- **Payment method validation**: Must be supported method
- **Gift card validation**: If using gift card, it must be valid and have sufficient balance

### Q: Is there actual payment processing?
**A:** No, the current system is a demo/prototype. It stores payment method information but doesn't integrate with actual payment gateways.

### Q: How are payment failures handled?
**A:** The system validates payment information during order creation. Invalid payments result in order creation failure with appropriate error messages.

---

## Inventory Management

### Q: How is product inventory tracked?
**A:** Each product has a `stockQuantity` field that tracks available inventory. However, stock is not automatically reduced when orders are placed.

### Q: Can inventory go negative?
**A:** The system doesn't prevent negative inventory in the current implementation. Stock management is manual through the admin interface.

### Q: How are low stock situations handled?
**A:** There's no automatic low stock alerting. Inventory monitoring must be done manually through the admin interface.

### Q: Can inventory be reserved during checkout?
**A:** No, there's no inventory reservation system. Stock is available on a first-come, first-served basis.

---

## Returns and Cancellations

### Q: Which orders can be cancelled?
**A:** Orders can be cancelled if they have status:
- **Pending**
- **Processing**

Orders with status Shipped, Delivered, Cancelled, or Returned cannot be cancelled.

### Q: Which orders can be returned?
**A:** Orders can be returned if they have status:
- **Delivered**
- **Processing**

### Q: What information is required for returns?
**A:** Returns require:
- **Return Reason**: Mandatory explanation for the return
- **Return Date**: Automatically set to current date

### Q: What happens when an order is cancelled or returned?
**A:** When cancelled or returned:
- Order status is updated accordingly
- Both `canReturn` and `canCancel` flags are set to `false`
- Return date and reason are recorded (for returns)

### Q: Are refunds automatically processed?
**A:** No, the system tracks return/cancellation status but doesn't automatically process refunds. Refund processing would need to be handled separately.

---

## System Administration

### Q: What admin capabilities are available?
**A:** Administrators have full CRUD (Create, Read, Update, Delete) access to all system entities:
- Customers
- Products
- Categories
- Orders
- Order Items
- Gift Cards
- Customer Addresses

### Q: Is there user authentication?
**A:** No, the current system doesn't implement user authentication or authorization. All admin functions are accessible without login.

### Q: Can admin users modify order status?
**A:** Yes, admin users can update order status through the admin interface, but should follow business rules about valid status transitions.

### Q: How are data changes tracked?
**A:** The system doesn't currently implement audit trails or change logging. All modifications are immediate and not tracked.

---

## Technical Limitations

### Q: What are the current system limitations?
**A:** Key limitations include:

**Security:**
- No user authentication or authorization
- No role-based access control
- No data encryption

**Business Logic:**
- No automatic inventory deduction
- No shipping cost calculation
- No tax calculation
- No actual payment processing
- No multi-currency support

**Functionality:**
- No order modification after creation
- No automatic refund processing
- No promotion/discount system (except gift cards)
- No audit trail or change logging
- No email notifications
- No delivery date estimation

### Q: Is the system production-ready?
**A:** No, this is a demo/prototype system. It would need significant enhancements for production use, including security, payment integration, and business logic completion.

### Q: Can the system handle multiple currencies?
**A:** No, the system assumes USD and doesn't support currency conversion or multiple currencies.

### Q: Are there data backup procedures?
**A:** The system uses SQLite database with no automated backup procedures. Data backup would need to be implemented separately.

### Q: How does the system handle concurrent users?
**A:** The system doesn't implement concurrency controls. In a multi-user environment, data conflicts could occur without proper locking mechanisms.

---

## Best Practices

### Q: What are recommended practices for order management?
**A:** 
- Always validate customer and product information before order creation
- Check gift card validity before processing gift card payments
- Monitor order status transitions carefully
- Implement proper error handling for failed operations

### Q: How should inventory be managed?
**A:**
- Regularly update stock quantities through admin interface
- Monitor low stock situations manually
- Consider implementing automatic stock deduction for production use
- Use product active/inactive status to manage product availability

### Q: What should be considered for production deployment?
**A:**
- Implement proper authentication and authorization
- Add payment gateway integration
- Implement inventory management automation
- Add audit trails and logging
- Implement proper error handling and validation
- Add backup and recovery procedures
- Consider scalability and performance requirements

---

*This FAQ covers the current business rules and limitations of the ShopHub e-commerce platform. For technical implementation details, refer to the codebase documentation.*