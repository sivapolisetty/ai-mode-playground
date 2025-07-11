import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface AdminFormProps {
  tableName: string;
  columns: string[];
  editItem?: any;
  onSubmit: (data: any) => void;
  onCancel: () => void;
}

const AdminForm: React.FC<AdminFormProps> = ({
  tableName,
  columns,
  editItem,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<any>({});

  useEffect(() => {
    if (editItem) {
      setFormData({ ...editItem });
    } else {
      // Initialize form with empty values
      const initialData: any = {};
      columns.forEach(column => {
        initialData[column] = getDefaultValue(column, tableName);
      });
      setFormData(initialData);
    }
  }, [editItem, columns, tableName]);

  const getDefaultValue = (column: string, table: string) => {
    const columnLower = column.toLowerCase();
    
    // Boolean fields
    if (columnLower.includes('active')) {
      return true; // Default to active for most entities
    }
    
    if (columnLower.includes('renewal') || 
        columnLower.includes('return') || 
        columnLower.includes('cancel')) {
      return false;
    }
    
    // Numeric fields
    if (columnLower.includes('id') && columnLower !== 'id' && !columnLower.includes('customer') && !columnLower.includes('product') && !columnLower.includes('order')) {
      return 0;
    }
    
    if (columnLower.includes('price') || 
        columnLower.includes('amount') || 
        columnLower.includes('balance')) {
      return 0;
    }
    
    if (columnLower.includes('quantity')) {
      return 1; // Default quantity to 1
    }
    
    // Date fields
    if (columnLower.includes('date')) {
      return new Date().toISOString().split('T')[0];
    }
    
    // Status fields
    if (columnLower === 'status') {
      if (table === 'customers') return 'Active';
      if (table === 'orders') return 'Pending';
      return 'Active';
    }
    
    // Payment method
    if (columnLower === 'paymentmethod') {
      return 'Credit Card';
    }
    
    // Default to empty string
    return '';
  };

  const getFieldType = (column: string, value: any) => {
    const columnLower = column.toLowerCase();
    
    if (typeof value === 'boolean' || 
        columnLower.includes('active') || 
        columnLower.includes('renewal') || 
        columnLower.includes('return') || 
        columnLower.includes('cancel')) {
      return 'boolean';
    }
    
    if (typeof value === 'number' || 
        columnLower.includes('price') || 
        columnLower.includes('amount') || 
        columnLower.includes('balance') || 
        columnLower.includes('quantity') ||
        (columnLower.includes('id') && columnLower !== 'id' && !columnLower.includes('customer') && !columnLower.includes('product') && !columnLower.includes('order'))) {
      return 'number';
    }
    
    if (columnLower.includes('date')) {
      return 'date';
    }
    
    if (columnLower.includes('description') || 
        columnLower.includes('address') || 
        columnLower.includes('reason') ||
        columnLower.includes('specifications')) {
      return 'textarea';
    }
    
    if (columnLower === 'status') {
      return 'select-status';
    }
    
    if (columnLower === 'paymentmethod') {
      return 'select-payment';
    }
    
    return 'text';
  };

  const handleInputChange = (column: string, value: any) => {
    setFormData((prev: any) => ({
      ...prev,
      [column]: value
    }));
    
    // Clear error for this field when user starts typing
    if (errors[column]) {
      setErrors((prev: any) => {
        const newErrors = { ...prev };
        delete newErrors[column];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors: any = {};
    
    columns.forEach(column => {
      const value = formData[column];
      const columnLower = column.toLowerCase();
      
      // Required field validation
      if (columnLower === 'name' || columnLower === 'email') {
        if (!value || value.toString().trim() === '') {
          newErrors[column] = `${column} is required`;
        }
      }
      
      // Email validation
      if (columnLower === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          newErrors[column] = 'Invalid email format';
        }
      }
      
      // Price/amount validation
      if ((columnLower.includes('price') || columnLower.includes('amount') || columnLower.includes('balance')) && value < 0) {
        newErrors[column] = 'Value cannot be negative';
      }
      
      // Phone validation (basic)
      if (columnLower === 'phone' && value) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(value.replace(/[\s\-\(\)]/g, ''))) {
          newErrors[column] = 'Invalid phone format';
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form before submitting
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    try {
      // Clean up form data
      const cleanData = { ...formData };
      
      // Remove auto-increment IDs for new records (except for tables that need them)
      if (!editItem && (cleanData.id || cleanData.id === 0)) {
        if (tableName === 'categories' || tableName === 'orderItems' || tableName === 'giftCards' || tableName === 'users') {
          delete cleanData.id;
        }
      }
      
      // Convert string numbers to actual numbers for numeric fields
      columns.forEach(column => {
        const columnLower = column.toLowerCase();
        if (columnLower.includes('price') || 
            columnLower.includes('amount') || 
            columnLower.includes('balance') || 
            columnLower.includes('quantity') ||
            (columnLower.includes('id') && columnLower !== 'id' && !columnLower.includes('customer') && !columnLower.includes('product') && !columnLower.includes('order'))) {
          if (cleanData[column] !== undefined && cleanData[column] !== '') {
            cleanData[column] = parseFloat(cleanData[column]) || 0;
          }
        }
      });
      
      await onSubmit(cleanData);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderField = (column: string) => {
    const fieldType = getFieldType(column, formData[column]);
    const value = formData[column];
    const isReadOnly = !editItem && column.toLowerCase() === 'id' && (tableName === 'categories' || tableName === 'orderItems');

    switch (fieldType) {
      case 'boolean':
        return (
          <div className="flex items-center space-x-2">
            <Checkbox
              id={column}
              checked={!!value}
              onCheckedChange={(checked) => handleInputChange(column, checked)}
            />
            <Label htmlFor={column}>{column}</Label>
          </div>
        );

      case 'number':
        return (
          <div className="space-y-2">
            <Label htmlFor={column}>{column}</Label>
            <Input
              id={column}
              type="number"
              value={value || ''}
              onChange={(e) => handleInputChange(column, parseFloat(e.target.value) || 0)}
              readOnly={isReadOnly}
              className={errors[column] ? 'border-red-500' : ''}
            />
            {errors[column] && (
              <p className="text-sm text-red-500">{errors[column]}</p>
            )}
          </div>
        );

      case 'date':
        return (
          <div className="space-y-2">
            <Label htmlFor={column}>{column}</Label>
            <Input
              id={column}
              type="date"
              value={value || ''}
              onChange={(e) => handleInputChange(column, e.target.value)}
              className={errors[column] ? 'border-red-500' : ''}
            />
            {errors[column] && (
              <p className="text-sm text-red-500">{errors[column]}</p>
            )}
          </div>
        );

      case 'textarea':
        return (
          <div className="space-y-2">
            <Label htmlFor={column}>{column}</Label>
            <Textarea
              id={column}
              value={value || ''}
              onChange={(e) => handleInputChange(column, e.target.value)}
              rows={3}
              className={errors[column] ? 'border-red-500' : ''}
            />
            {errors[column] && (
              <p className="text-sm text-red-500">{errors[column]}</p>
            )}
          </div>
        );

      case 'select-status':
        return (
          <div className="space-y-2">
            <Label htmlFor={column}>{column}</Label>
            <Select value={value || ''} onValueChange={(val) => handleInputChange(column, val)}>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Active">Active</SelectItem>
                <SelectItem value="Inactive">Inactive</SelectItem>
                <SelectItem value="Pending">Pending</SelectItem>
                <SelectItem value="Processing">Processing</SelectItem>
                <SelectItem value="Shipped">Shipped</SelectItem>
                <SelectItem value="Delivered">Delivered</SelectItem>
                <SelectItem value="Cancelled">Cancelled</SelectItem>
                <SelectItem value="Returned">Returned</SelectItem>
                <SelectItem value="Completed">Completed</SelectItem>
                <SelectItem value="Failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        );

      case 'select-payment':
        return (
          <div className="space-y-2">
            <Label htmlFor={column}>{column}</Label>
            <Select value={value || ''} onValueChange={(val) => handleInputChange(column, val)}>
              <SelectTrigger>
                <SelectValue placeholder="Select payment method" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Credit Card">Credit Card</SelectItem>
                <SelectItem value="PayPal">PayPal</SelectItem>
                <SelectItem value="Cash on Delivery">Cash on Delivery</SelectItem>
                <SelectItem value="Gift Card">Gift Card</SelectItem>
              </SelectContent>
            </Select>
          </div>
        );

      default:
        return (
          <div className="space-y-2">
            <Label htmlFor={column}>{column}</Label>
            <Input
              id={column}
              type="text"
              value={value || ''}
              onChange={(e) => handleInputChange(column, e.target.value)}
              readOnly={isReadOnly}
              className={errors[column] ? 'border-red-500' : ''}
            />
            {errors[column] && (
              <p className="text-sm text-red-500">{errors[column]}</p>
            )}
          </div>
        );
    }
  };

  return (
    <Dialog open={true} onOpenChange={onCancel}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {editItem ? 'Edit' : 'Add New'} {tableName.slice(0, -1)}
          </DialogTitle>
          <DialogDescription>
            {editItem ? 'Update the record details below.' : 'Fill in the details to create a new record.'}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {columns.map((column) => (
              <div key={column}>
                {renderField(column)}
              </div>
            ))}
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : editItem ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default AdminForm;