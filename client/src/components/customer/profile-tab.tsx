import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { queryClient, apiRequest } from '@/lib/queryClient';

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
  createdDate: string;
}

interface ProfileTabProps {
  customerId: string;
  customer: {
    id: string;
    name: string;
    email: string;
    phone: string;
    address: string;
    dob: string;
    registrationDate: string;
    accountType: string;
    status: string;
  };
}

const ProfileTab: React.FC<ProfileTabProps> = ({ customerId, customer }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [addresses, setAddresses] = useState<CustomerAddress[]>([]);
  const [loadingAddresses, setLoadingAddresses] = useState(false);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [editingAddressId, setEditingAddressId] = useState<number | null>(null);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    dob: '',
    address: '',
    accountType: ''
  });

  const [addressFormData, setAddressFormData] = useState({
    label: '',
    recipientName: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    state: '',
    zipCode: '',
    country: 'USA',
    phone: '',
    isDefault: false
  });

  // Initialize form data when customer data is available
  useEffect(() => {
    if (customer) {
      setFormData({
        name: customer.name,
        email: customer.email,
        phone: customer.phone,
        dob: customer.dob,
        address: customer.address,
        accountType: customer.accountType
      });
    }
  }, [customer]);

  // Fetch customer addresses
  const fetchAddresses = async () => {
    if (!customerId) return;
    
    setLoadingAddresses(true);
    try {
      const fetchedAddresses = await apiRequest('GET', `/api/customers/${customerId}/addresses`);
      setAddresses(fetchedAddresses);
    } catch (error) {
      console.error('Failed to fetch addresses:', error);
      toast({
        title: "Error",
        description: "Failed to load customer addresses",
        variant: "destructive"
      });
    } finally {
      setLoadingAddresses(false);
    }
  };

  useEffect(() => {
    fetchAddresses();
  }, [customerId]);

  const formatAddress = (address: CustomerAddress) => {
    const parts = [
      address.addressLine1,
      address.addressLine2,
      `${address.city}, ${address.state} ${address.zipCode}`,
      address.country !== 'USA' ? address.country : ''
    ].filter(Boolean);
    return parts.join(', ');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSelectChange = (value: string) => {
    setFormData(prev => ({ ...prev, accountType: value }));
  };

  const handleAddressInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setAddressFormData(prev => ({ 
      ...prev, 
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value 
    }));
  };

  const resetAddressForm = () => {
    setAddressFormData({
      label: '',
      recipientName: '',
      addressLine1: '',
      addressLine2: '',
      city: '',
      state: '',
      zipCode: '',
      country: 'USA',
      phone: '',
      isDefault: false
    });
    setEditingAddressId(null);
    setShowAddressForm(false);
  };

  const handleAddAddress = () => {
    setAddressFormData({
      ...addressFormData,
      recipientName: customer.name,
      phone: customer.phone
    });
    setShowAddressForm(true);
  };

  const handleEditAddress = (address: CustomerAddress) => {
    setAddressFormData({
      label: address.label,
      recipientName: address.recipientName,
      addressLine1: address.addressLine1,
      addressLine2: address.addressLine2 || '',
      city: address.city,
      state: address.state,
      zipCode: address.zipCode,
      country: address.country,
      phone: address.phone || '',
      isDefault: address.isDefault
    });
    setEditingAddressId(address.id);
    setShowAddressForm(true);
  };

  const handleSaveAddress = async () => {
    try {
      const addressData = {
        ...addressFormData,
        customerId,
        isActive: true,
        createdDate: new Date().toISOString()
      };

      if (editingAddressId) {
        // Update existing address
        await apiRequest('PUT', `/api/admin/customerAddresses/${editingAddressId}`, addressData);
        toast({
          title: "Success",
          description: "Address updated successfully",
        });
      } else {
        // Create new address
        await apiRequest('POST', `/api/customers/${customerId}/addresses`, addressData);
        toast({
          title: "Success",
          description: "Address added successfully",
        });
      }

      await fetchAddresses();
      resetAddressForm();
    } catch (error) {
      toast({
        title: "Error",
        description: `Failed to ${editingAddressId ? 'update' : 'add'} address`,
        variant: "destructive"
      });
    }
  };

  const handleDeleteAddress = async (addressId: number) => {
    if (!confirm('Are you sure you want to delete this address?')) return;

    try {
      await apiRequest('DELETE', `/api/admin/customerAddresses/${addressId}`);
      toast({
        title: "Success",
        description: "Address deleted successfully",
      });
      await fetchAddresses();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete address",
        variant: "destructive"
      });
    }
  };

  const handleSetDefaultAddress = async (addressId: number) => {
    try {
      await apiRequest('PUT', `/api/customers/${customerId}/addresses/${addressId}/default`);
      toast({
        title: "Success",
        description: "Default address updated successfully",
      });
      await fetchAddresses();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to set default address",
        variant: "destructive"
      });
    }
  };

  const handleSave = async () => {
    try {
      await apiRequest('PATCH', `/api/customers/${customerId}`, formData);
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: [`/api/customers/${customerId}`] });
      
      toast({
        title: "Success",
        description: "Customer profile updated successfully",
      });
      
      setIsEditing(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update customer profile",
        variant: "destructive"
      });
    }
  };

  if (!customer) {
    return <div className="p-6">No customer data available</div>;
  }

  return (
    <div className="px-4 py-5 sm:p-6">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <h3 className="text-base font-semibold leading-6 text-slate-900">Customer Information</h3>
        <button 
          type="button" 
          onClick={() => setIsEditing(!isEditing)}
          className="mt-3 inline-flex items-center text-sm font-medium text-primary sm:mt-0"
        >
          <i className={`${isEditing ? 'ri-eye-line' : 'ri-edit-line'} mr-1`}></i>
          {isEditing ? 'View' : 'Edit'}
        </button>
      </div>

      {!isEditing ? (
        // View mode
        <div className="grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
          <div className="sm:col-span-3">
            <div className="text-sm font-medium text-slate-500">Full Name</div>
            <div className="mt-1 text-sm text-slate-900">{customer.name}</div>
          </div>

          <div className="sm:col-span-3">
            <div className="text-sm font-medium text-slate-500">Email Address</div>
            <div className="mt-1 text-sm text-slate-900">{customer.email}</div>
          </div>

          <div className="sm:col-span-3">
            <div className="text-sm font-medium text-slate-500">Phone Number</div>
            <div className="mt-1 text-sm text-slate-900">{customer.phone}</div>
          </div>

          <div className="sm:col-span-3">
            <div className="text-sm font-medium text-slate-500">Date of Birth</div>
            <div className="mt-1 text-sm text-slate-900">{customer.dob}</div>
          </div>

          <div className="sm:col-span-full">
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium text-slate-500">Addresses</div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleAddAddress}
                className="text-xs"
              >
                <i className="ri-add-line mr-1"></i>
                Add Address
              </Button>
            </div>
            {loadingAddresses ? (
              <div className="text-sm text-slate-500">Loading addresses...</div>
            ) : addresses.length > 0 ? (
              <div className="space-y-3">
                {addresses.map((address) => (
                  <div key={address.id} className="border rounded-lg p-3 bg-slate-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-slate-900">{address.label}</span>
                          {address.isDefault && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                              Default
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-slate-700 mb-1">{address.recipientName}</div>
                        <div className="text-sm text-slate-600">{formatAddress(address)}</div>
                        {address.phone && (
                          <div className="text-sm text-slate-600 mt-1">Phone: {address.phone}</div>
                        )}
                      </div>
                      <div className="flex items-center gap-1 ml-3">
                        {!address.isDefault && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => handleSetDefaultAddress(address.id)}
                            className="text-xs h-7 px-2"
                          >
                            Set Default
                          </Button>
                        )}
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleEditAddress(address)}
                          className="text-xs h-7 px-2"
                        >
                          <i className="ri-edit-line"></i>
                        </Button>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteAddress(address.id)}
                          className="text-xs h-7 px-2 text-red-600 hover:text-red-700"
                        >
                          <i className="ri-delete-bin-line"></i>
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-slate-500">No addresses found</div>
            )}
          </div>

          <div className="sm:col-span-3">
            <div className="text-sm font-medium text-slate-500">Customer Since</div>
            <div className="mt-1 text-sm text-slate-900">{customer.registrationDate}</div>
          </div>

          <div className="sm:col-span-3">
            <div className="text-sm font-medium text-slate-500">Account Type</div>
            <div className="mt-1 text-sm text-slate-900">{customer.accountType}</div>
          </div>
        </div>
      ) : (
        // Edit mode
        <form className="grid grid-cols-1 gap-x-6 gap-y-4 sm:grid-cols-6">
          <div className="sm:col-span-3">
            <label htmlFor="name" className="block text-sm font-medium leading-6 text-slate-900">
              Full Name
            </label>
            <div className="mt-2">
              <Input
                type="text"
                name="name"
                id="name"
                value={formData.name}
                onChange={handleInputChange}
                className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          <div className="sm:col-span-3">
            <label htmlFor="email" className="block text-sm font-medium leading-6 text-slate-900">
              Email Address
            </label>
            <div className="mt-2">
              <Input
                type="email"
                name="email"
                id="email"
                value={formData.email}
                onChange={handleInputChange}
                className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          <div className="sm:col-span-3">
            <label htmlFor="phone" className="block text-sm font-medium leading-6 text-slate-900">
              Phone Number
            </label>
            <div className="mt-2">
              <Input
                type="tel"
                name="phone"
                id="phone"
                value={formData.phone}
                onChange={handleInputChange}
                className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          <div className="sm:col-span-3">
            <label htmlFor="dob" className="block text-sm font-medium leading-6 text-slate-900">
              Date of Birth
            </label>
            <div className="mt-2">
              <Input
                type="text"
                name="dob"
                id="dob"
                value={formData.dob}
                onChange={handleInputChange}
                className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          <div className="sm:col-span-full">
            <label htmlFor="address" className="block text-sm font-medium leading-6 text-slate-900">
              Address
            </label>
            <div className="mt-2">
              <Textarea
                id="address"
                name="address"
                rows={3}
                value={formData.address}
                onChange={handleInputChange}
                className="block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-primary sm:text-sm sm:leading-6"
              />
            </div>
          </div>

          <div className="sm:col-span-3">
            <label htmlFor="account-type" className="block text-sm font-medium leading-6 text-slate-900">
              Account Type
            </label>
            <div className="mt-2">
              <Select value={formData.accountType} onValueChange={handleSelectChange}>
                <SelectTrigger id="account-type">
                  <SelectValue placeholder="Select account type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Standard">Standard</SelectItem>
                  <SelectItem value="Premium">Premium</SelectItem>
                  <SelectItem value="Business">Business</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="sm:col-span-full mt-4">
            <div className="flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsEditing(false)}
                className="rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50"
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleSave}
                className="rounded-md bg-primary px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              >
                Save Changes
              </Button>
            </div>
          </div>
        </form>
      )}
      
      {/* Address Form Modal */}
      {showAddressForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <div className="px-6 py-4 border-b">
              <h3 className="text-lg font-semibold text-slate-900">
                {editingAddressId ? 'Edit Address' : 'Add New Address'}
              </h3>
            </div>
            
            <div className="px-6 py-4">
              <form className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="sm:col-span-1">
                  <label htmlFor="label" className="block text-sm font-medium text-slate-700">
                    Address Label
                  </label>
                  <Input
                    type="text"
                    name="label"
                    id="label"
                    placeholder="e.g., Home, Work, Billing"
                    value={addressFormData.label}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="recipientName" className="block text-sm font-medium text-slate-700">
                    Recipient Name
                  </label>
                  <Input
                    type="text"
                    name="recipientName"
                    id="recipientName"
                    value={addressFormData.recipientName}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-2">
                  <label htmlFor="addressLine1" className="block text-sm font-medium text-slate-700">
                    Address Line 1
                  </label>
                  <Input
                    type="text"
                    name="addressLine1"
                    id="addressLine1"
                    placeholder="Street address"
                    value={addressFormData.addressLine1}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-2">
                  <label htmlFor="addressLine2" className="block text-sm font-medium text-slate-700">
                    Address Line 2 (Optional)
                  </label>
                  <Input
                    type="text"
                    name="addressLine2"
                    id="addressLine2"
                    placeholder="Apt, suite, unit, building, floor, etc."
                    value={addressFormData.addressLine2}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="city" className="block text-sm font-medium text-slate-700">
                    City
                  </label>
                  <Input
                    type="text"
                    name="city"
                    id="city"
                    value={addressFormData.city}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="state" className="block text-sm font-medium text-slate-700">
                    State
                  </label>
                  <Input
                    type="text"
                    name="state"
                    id="state"
                    value={addressFormData.state}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="zipCode" className="block text-sm font-medium text-slate-700">
                    ZIP Code
                  </label>
                  <Input
                    type="text"
                    name="zipCode"
                    id="zipCode"
                    value={addressFormData.zipCode}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="country" className="block text-sm font-medium text-slate-700">
                    Country
                  </label>
                  <Input
                    type="text"
                    name="country"
                    id="country"
                    value={addressFormData.country}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1">
                  <label htmlFor="phone" className="block text-sm font-medium text-slate-700">
                    Phone (Optional)
                  </label>
                  <Input
                    type="tel"
                    name="phone"
                    id="phone"
                    value={addressFormData.phone}
                    onChange={handleAddressInputChange}
                    className="mt-1"
                  />
                </div>
                
                <div className="sm:col-span-1 flex items-center mt-6">
                  <input
                    type="checkbox"
                    name="isDefault"
                    id="isDefault"
                    checked={addressFormData.isDefault}
                    onChange={handleAddressInputChange}
                    className="h-4 w-4 text-primary focus:ring-primary border-slate-300 rounded"
                  />
                  <label htmlFor="isDefault" className="ml-2 block text-sm text-slate-700">
                    Set as default address
                  </label>
                </div>
              </form>
            </div>
            
            <div className="px-6 py-4 border-t flex justify-end space-x-3">
              <Button
                type="button"
                variant="outline"
                onClick={resetAddressForm}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleSaveAddress}
              >
                {editingAddressId ? 'Update Address' : 'Add Address'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileTab;
