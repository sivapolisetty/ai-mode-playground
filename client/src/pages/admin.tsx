import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import AdminTable from '@/components/admin/admin-table';

const AdminPage: React.FC = () => {
  const [activeTable, setActiveTable] = useState('customers');

  const tables = [
    { id: 'customers', name: 'Customers', icon: '👥' },
    { id: 'customerAddresses', name: 'Addresses', icon: '📍' },
    { id: 'products', name: 'Products', icon: '📦' },
    { id: 'categories', name: 'Categories', icon: '🏷️' },
    { id: 'orders', name: 'Orders', icon: '🛍️' },
    { id: 'orderItems', name: 'Order Items', icon: '📋' },
    { id: 'giftCards', name: 'Gift Cards', icon: '🎁' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="border-b bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Database Administration</h1>
              <p className="text-gray-600">Manage all database tables and records</p>
            </div>
            <Badge variant="outline" className="bg-red-50 text-red-700 border-red-200">
              Admin Access
            </Badge>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        <Tabs value={activeTable} onValueChange={setActiveTable} className="w-full">
          <TabsList className="grid w-full grid-cols-8 mb-6">
            {tables.map((table) => (
              <TabsTrigger key={table.id} value={table.id} className="flex items-center gap-2">
                <span>{table.icon}</span>
                <span className="hidden sm:inline">{table.name}</span>
              </TabsTrigger>
            ))}
          </TabsList>

          {tables.map((table) => (
            <TabsContent key={table.id} value={table.id}>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span>{table.icon}</span>
                    {table.name} Management
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <AdminTable tableName={table.id} />
                </CardContent>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPage;