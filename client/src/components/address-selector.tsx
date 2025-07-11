import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';

interface CustomerAddress {
  id: number;
  customerId: string;
  label: string;
  recipientName: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  phone?: string;
  isDefault: boolean;
  isActive: boolean;
}

interface AddressSelectorProps {
  customerId: string;
  selectedAddressId?: number;
  onAddressSelect: (address: CustomerAddress) => void;
}

export const AddressSelector: React.FC<AddressSelectorProps> = ({
  customerId,
  selectedAddressId,
  onAddressSelect,
}) => {
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newAddress, setNewAddress] = useState({
    label: '',
    recipientName: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'USA',
    phone: ''
  });
  const { toast } = useToast();

  const { data: addresses = [], refetch } = useQuery({
    queryKey: [`/api/customers/${customerId}/addresses`],
    enabled: !!customerId
  });

  // Auto-select default address on load
  useEffect(() => {
    if (addresses.length > 0 && !selectedAddressId) {
      const defaultAddress = addresses.find((addr: CustomerAddress) => addr.isDefault) || addresses[0];
      onAddressSelect(defaultAddress);
    }
  }, [addresses, selectedAddressId, onAddressSelect]);

  const handleAddressChange = (addressId: string) => {
    const address = addresses.find((addr: CustomerAddress) => addr.id === parseInt(addressId));
    if (address) {
      onAddressSelect(address);
    }
  };

  const handleAddNewAddress = async () => {
    try {
      const response = await fetch(`/api/customers/${customerId}/addresses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newAddress,
          isDefault: addresses.length === 0, // Make first address default
          isActive: true,
          createdDate: new Date().toISOString().split('T')[0]
        }),
      });

      if (response.ok) {
        const newAddr = await response.json();
        toast({
          title: "Success",
          description: "Address added successfully"
        });
        setShowAddDialog(false);
        setNewAddress({
          label: '',
          recipientName: '',
          addressLine1: '',
          addressLine2: '',
          city: '',
          state: '',
          zipCode: '',
          country: 'USA',
          phone: ''
        });
        refetch();
        onAddressSelect(newAddr);
      } else {
        throw new Error('Failed to add address');
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to add address",
        variant: "destructive"
      });
    }
  };

  const formatAddress = (address: CustomerAddress) => {
    const lines = [
      address.addressLine1,
      address.addressLine2,
      `${address.city}, ${address.state} ${address.zipCode}`,
      address.country !== 'USA' ? address.country : ''
    ].filter(Boolean);
    
    return lines.join(', ');
  };

  const selectedAddress = addresses.find((addr: CustomerAddress) => addr.id === selectedAddressId);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Delivery Address</h3>
        <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <i className="ri-add-line mr-1"></i>
              Add Address
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Add New Address</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="label">Label</Label>
                  <Input
                    id="label"
                    placeholder="Home, Work, etc."
                    value={newAddress.label}
                    onChange={(e) => setNewAddress({ ...newAddress, label: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="recipientName">Recipient Name</Label>
                  <Input
                    id="recipientName"
                    value={newAddress.recipientName}
                    onChange={(e) => setNewAddress({ ...newAddress, recipientName: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="addressLine1">Address Line 1</Label>
                <Input
                  id="addressLine1"
                  value={newAddress.addressLine1}
                  onChange={(e) => setNewAddress({ ...newAddress, addressLine1: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="addressLine2">Address Line 2 (Optional)</Label>
                <Input
                  id="addressLine2"
                  value={newAddress.addressLine2}
                  onChange={(e) => setNewAddress({ ...newAddress, addressLine2: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label htmlFor="city">City</Label>
                  <Input
                    id="city"
                    value={newAddress.city}
                    onChange={(e) => setNewAddress({ ...newAddress, city: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="state">State</Label>
                  <Input
                    id="state"
                    value={newAddress.state}
                    onChange={(e) => setNewAddress({ ...newAddress, state: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="zipCode">ZIP Code</Label>
                  <Input
                    id="zipCode"
                    value={newAddress.zipCode}
                    onChange={(e) => setNewAddress({ ...newAddress, zipCode: e.target.value })}
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="phone">Phone (Optional)</Label>
                <Input
                  id="phone"
                  value={newAddress.phone}
                  onChange={(e) => setNewAddress({ ...newAddress, phone: e.target.value })}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAddNewAddress} className="flex-1">
                  Add Address
                </Button>
                <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                  Cancel
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {addresses.length > 0 ? (
        <div className="space-y-3">
          <Select 
            value={selectedAddressId?.toString() || ''} 
            onValueChange={handleAddressChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select delivery address" />
            </SelectTrigger>
            <SelectContent>
              {addresses.map((address: CustomerAddress) => (
                <SelectItem key={address.id} value={address.id.toString()}>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">{address.label}</span>
                    {address.isDefault && (
                      <Badge variant="secondary" className="text-xs">Default</Badge>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedAddress && (
            <Card>
              <CardContent className="p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium">{selectedAddress.label}</h4>
                      {selectedAddress.isDefault && (
                        <Badge variant="secondary" className="text-xs">Default</Badge>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 space-y-1">
                      <div className="font-medium">{selectedAddress.recipientName}</div>
                      <div>{selectedAddress.addressLine1}</div>
                      {selectedAddress.addressLine2 && <div>{selectedAddress.addressLine2}</div>}
                      <div>{selectedAddress.city}, {selectedAddress.state} {selectedAddress.zipCode}</div>
                      {selectedAddress.phone && <div>{selectedAddress.phone}</div>}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      ) : (
        <Card>
          <CardContent className="p-6 text-center">
            <div className="text-gray-500 mb-4">
              <i className="ri-map-pin-line text-2xl mb-2 block"></i>
              No addresses found
            </div>
            <p className="text-sm text-gray-600 mb-4">
              Add a delivery address to continue with your order
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};