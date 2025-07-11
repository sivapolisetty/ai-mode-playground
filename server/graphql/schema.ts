import { gql } from 'apollo-server-express';

export const typeDefs = gql`
  type Customer {
    id: String!
    name: String!
    email: String!
    phone: String!
    address: String!
    dob: String!
    registrationDate: String!
    accountType: String!
    status: String!
    plan: Plan
    devices: [Device!]
    orders: [Order!]
  }

  type Plan {
    id: Int!
    customerId: String!
    name: String!
    description: String!
    billingCycle: String!
    renewalDate: String!
    monthlyPrice: Float!
    autoRenewal: Boolean!
    status: String!
    features: [PlanFeature!]
  }

  type PlanFeature {
    id: Int!
    planId: Int!
    name: String!
  }

  type Device {
    id: Int!
    customerId: String!
    name: String!
    type: String!
    status: String!
    lastActive: String!
    ipAddress: String
  }

  type Product {
    id: String!
    categoryId: Int!
    name: String!
    description: String!
    price: Float!
    imageUrl: String
    brand: String
    model: String
    color: String
    size: String
    specifications: String
    stockQuantity: Int!
    isActive: Boolean!
  }

  type OrderItem {
    id: Int!
    orderId: String!
    productId: String!
    quantity: Int!
    price: Float!
    selectedSize: String
    selectedColor: String
    selectedConfiguration: String
    product: Product
  }

  type Order {
    id: String!
    customerId: String!
    date: String!
    items: String!
    amount: Float!
    status: String!
    orderItems: [OrderItem!]
  }

  type Query {
    customers: [Customer!]!
    customer(id: String!): Customer
    customerPlans(customerId: String!): Plan
    customerDevices(customerId: String!): [Device!]
    customerOrders(customerId: String!): [Order!]
    customerWithRelations(id: String!): Customer
  }
`;
