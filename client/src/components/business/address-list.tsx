import React from 'react';
import { AddressCard, AddressCardProps } from './address-card';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export interface AddressListProps {
  addresses: Array<AddressCardProps & { id: string | number }>;
  onAction?: (action: string, data?: Record<string, any>) => void;
  title?: string;
  description?: string;
  showAddButton?: boolean;
  className?: string;
}

export const AddressList: React.FC<AddressListProps> = ({
  addresses,
  onAction,
  title = 'Addresses',
  description,
  showAddButton = true,
  className = ''
}) => {
  const defaultActions = (address: AddressCardProps & { id: string | number }) => [
    {
      label: 'Edit',
      action: 'edit_address',
      data: { addressId: address.id },
      variant: 'outline' as const
    },
    ...(!address.isDefault ? [{
      label: 'Set Default',
      action: 'set_default_address',
      data: { addressId: address.id },
      variant: 'outline' as const
    }] : []),
    {
      label: 'Delete',
      action: 'delete_address',
      data: { addressId: address.id },
      variant: 'destructive' as const
    }
  ];

  return (
    <div className={className}>
      {/* List Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          {description && (
            <p className="text-gray-600 mt-1">{description}</p>
          )}
        </div>
        
        {showAddButton && (
          <Button
            onClick={() => onAction?.('add_address', {})}
            className="flex items-center"
          >
            <i className="ri-add-line mr-2"></i>
            Add Address
          </Button>
        )}
      </div>
      
      {/* Addresses Grid/List */}
      {addresses.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {addresses.map((address) => (
            <AddressCard
              key={address.id}
              {...address}
              actions={address.actions || defaultActions(address)}
              onAction={onAction}
            />
          ))}
        </div>
      ) : (
        <Card className="text-center py-12">
          <CardContent className="pt-6">
            <div className="text-gray-400 mb-4">
              <i className="ri-map-pin-line text-6xl"></i>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No addresses found
            </h3>
            <p className="text-gray-500 mb-4">
              Add your first address to get started with faster checkout.
            </p>
            {showAddButton && (
              <Button
                onClick={() => onAction?.('add_address', {})}
                className="flex items-center mx-auto"
              >
                <i className="ri-add-line mr-2"></i>
                Add Your First Address
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AddressList;