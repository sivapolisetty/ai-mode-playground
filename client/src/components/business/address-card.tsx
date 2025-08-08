import React from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export interface AddressCardProps {
  id?: string | number;
  label?: string;
  recipientName?: string;
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country?: string;
  phone?: string;
  isDefault?: boolean;
  type?: 'shipping' | 'billing' | 'both';
  actions?: Array<{
    label: string;
    action: string;
    data?: Record<string, any>;
    variant?: 'default' | 'outline' | 'destructive';
  }>;
  onAction?: (action: string, data?: Record<string, any>) => void;
  className?: string;
}

export const AddressCard: React.FC<AddressCardProps> = ({
  id,
  label,
  recipientName,
  street,
  city,
  state,
  zipCode,
  country = 'United States',
  phone,
  isDefault = false,
  type = 'both',
  actions = [],
  onAction,
  className = ''
}) => {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'shipping': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'billing': return 'bg-green-100 text-green-800 border-green-200';
      case 'both': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold">
            <i className="ri-map-pin-line mr-2"></i>
            {label || 'Address'}
            {recipientName && (
              <span className="text-sm font-normal text-gray-600 ml-2">
                ({recipientName})
              </span>
            )}
          </CardTitle>
          <div className="flex gap-2">
            <Badge className={getTypeColor(type)}>
              {type === 'both' ? 'Shipping & Billing' : type.charAt(0).toUpperCase() + type.slice(1)}
            </Badge>
            {isDefault && (
              <Badge variant="default">
                <i className="ri-star-fill mr-1"></i>
                Default
              </Badge>
            )}
          </div>
        </div>
        <CardDescription className="text-sm text-gray-600">
          {city}, {state} {zipCode}
          {country && country !== 'United States' && `, ${country}`}
        </CardDescription>
      </CardHeader>
      
      {/* Map Preview (optional) */}
      <CardContent>
        <div className="bg-gray-100 rounded-md p-4 mb-3">
          <div className="flex items-center text-sm text-gray-600">
            <i className="ri-map-2-line mr-2 text-lg"></i>
            <div>
              <div className="font-medium text-gray-900">{street}</div>
              <div>{city}, {state} {zipCode}</div>
              {country && <div>{country}</div>}
            </div>
          </div>
        </div>
        
        {/* Address Details */}
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">Address ID:</span>
            <span className="font-medium">#{id || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">Type:</span>
            <span className="font-medium capitalize">{type === 'both' ? 'Shipping & Billing' : type}</span>
          </div>
          {recipientName && (
            <div className="flex justify-between">
              <span className="text-gray-500">Recipient:</span>
              <span className="font-medium">{recipientName}</span>
            </div>
          )}
          {phone && (
            <div className="flex justify-between">
              <span className="text-gray-500">Phone:</span>
              <span className="font-medium">{phone}</span>
            </div>
          )}
        </div>
      </CardContent>
      
      {/* Action Buttons */}
      {actions.length > 0 && (
        <CardFooter className="flex gap-2 pt-4">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.variant || 'outline'}
              size="sm"
              className="flex-1"
              onClick={() => onAction?.(action.action, action.data)}
            >
              {action.action === 'edit' && <i className="ri-edit-line mr-1"></i>}
              {action.action === 'delete' && <i className="ri-delete-bin-line mr-1"></i>}
              {action.action === 'set_default' && <i className="ri-star-line mr-1"></i>}
              {action.label}
            </Button>
          ))}
        </CardFooter>
      )}
    </Card>
  );
};

export default AddressCard;