import { storage } from "../storage";

export const resolvers = {
  Query: {
    customers: async () => {
      return storage.getAllCustomers();
    },
    customer: async (_: any, { id }: { id: string }) => {
      return storage.getCustomerById(id);
    },
    customerPlans: async (_: any, { customerId }: { customerId: string }) => {
      return storage.getPlanByCustomerId(customerId);
    },
    customerDevices: async (_: any, { customerId }: { customerId: string }) => {
      return storage.getDevicesByCustomerId(customerId);
    },
    customerOrders: async (_: any, { customerId }: { customerId: string }) => {
      return storage.getOrdersByCustomerId(customerId);
    },
    customerWithRelations: async (_: any, { id }: { id: string }) => {
      return storage.getCustomerWithRelations(id);
    }
  },
  Customer: {
    plan: async (parent: { id: string }) => {
      return storage.getPlanWithFeaturesByCustomerId(parent.id);
    },
    devices: async (parent: { id: string }) => {
      return storage.getDevicesByCustomerId(parent.id);
    },
    orders: async (parent: { id: string }) => {
      return storage.getOrdersByCustomerId(parent.id);
    }
  },
  Plan: {
    features: async (parent: { id: number }) => {
      return storage.getPlanFeaturesByPlanId(parent.id);
    }
  },
  Order: {
    orderItems: async (parent: { id: string }) => {
      return storage.getOrderItemsByOrderId(parent.id);
    }
  },
  OrderItem: {
    product: async (parent: { productId: string }) => {
      return storage.getProductById(parent.productId);
    }
  }
};
