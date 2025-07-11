import React, { useState } from 'react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Smartphone, Shirt, ShoppingBag } from 'lucide-react';

interface Product {
  id: string;
  categoryId: number;
  name: string;
  description: string;
  price: number;
  imageUrl?: string;
  brand?: string;
  model?: string;
  color?: string;
  size?: string;
  specifications?: string;
}

interface ProductConfigurationProps {
  product: Product;
  onConfigurationChange: (config: {
    selectedSize?: string;
    selectedColor?: string;
    selectedConfiguration?: string;
  }) => void;
}

export function ProductConfiguration({ product, onConfigurationChange }: ProductConfigurationProps) {
  const [selectedSize, setSelectedSize] = useState<string>('');
  const [selectedColor, setSelectedColor] = useState<string>('');
  const [selectedConfiguration, setSelectedConfiguration] = useState<string>('');

  // Parse specifications for electronics
  const parseElectronicsSpecs = (specs: string) => {
    try {
      return JSON.parse(specs);
    } catch {
      return {};
    }
  };

  // Get available options based on product category
  const getProductOptions = () => {
    switch (product.categoryId) {
      case 1: // Electronics
        const specs = product.specifications ? parseElectronicsSpecs(product.specifications) : {};
        return {
          type: 'electronics',
          colors: ['Space Gray', 'Silver', 'Gold', 'Blue', 'Red', 'Purple'],
          configurations: [
            { label: '128GB', value: '128gb', price: 0 },
            { label: '256GB', value: '256gb', price: 100 },
            { label: '512GB', value: '512gb', price: 200 },
            { label: '1TB', value: '1tb', price: 400 }
          ]
        };
      case 2: // Clothing
        return {
          type: 'clothing',
          sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
          colors: ['Black', 'White', 'Navy', 'Gray', 'Red', 'Blue', 'Green']
        };
      case 3: // Footwear
        return {
          type: 'footwear',
          sizes: ['6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12'],
          colors: ['Black', 'White', 'Brown', 'Gray', 'Navy', 'Red']
        };
      default:
        return { type: 'other' };
    }
  };

  const options = getProductOptions();

  const handleSizeChange = (size: string) => {
    setSelectedSize(size);
    onConfigurationChange({
      selectedSize: size,
      selectedColor,
      selectedConfiguration
    });
  };

  const handleColorChange = (color: string) => {
    setSelectedColor(color);
    onConfigurationChange({
      selectedSize,
      selectedColor: color,
      selectedConfiguration
    });
  };

  const handleConfigurationChange = (config: string) => {
    setSelectedConfiguration(config);
    onConfigurationChange({
      selectedSize,
      selectedColor,
      selectedConfiguration: config
    });
  };

  const getIcon = () => {
    switch (options.type) {
      case 'electronics':
        return <Smartphone className="h-4 w-4" />;
      case 'clothing':
        return <Shirt className="h-4 w-4" />;
      case 'footwear':
        return <ShoppingBag className="h-4 w-4" />;
      default:
        return null;
    }
  };

  if (options.type === 'other') {
    return null;
  }

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm">
          {getIcon()}
          Product Options
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Size Selection for Clothing and Footwear */}
        {(options.type === 'clothing' || options.type === 'footwear') && options.sizes && (
          <div className="space-y-2">
            <Label className="text-sm font-medium">
              {options.type === 'clothing' ? 'Size' : 'Shoe Size'}
            </Label>
            <Select value={selectedSize} onValueChange={handleSizeChange}>
              <SelectTrigger>
                <SelectValue placeholder={`Select ${options.type === 'clothing' ? 'size' : 'shoe size'}`} />
              </SelectTrigger>
              <SelectContent>
                {options.sizes.map((size) => (
                  <SelectItem key={size} value={size}>
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Color Selection for All Categories */}
        {options.colors && (
          <div className="space-y-2">
            <Label className="text-sm font-medium">Color</Label>
            <Select value={selectedColor} onValueChange={handleColorChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select color" />
              </SelectTrigger>
              <SelectContent>
                {options.colors.map((color) => (
                  <SelectItem key={color} value={color}>
                    {color}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Configuration Selection for Electronics */}
        {options.type === 'electronics' && options.configurations && (
          <div className="space-y-2">
            <Label className="text-sm font-medium">Storage</Label>
            <Select value={selectedConfiguration} onValueChange={handleConfigurationChange}>
              <SelectTrigger>
                <SelectValue placeholder="Select storage capacity" />
              </SelectTrigger>
              <SelectContent>
                {options.configurations.map((config) => (
                  <SelectItem key={config.value} value={config.value}>
                    <div className="flex items-center justify-between w-full">
                      <span>{config.label}</span>
                      {config.price > 0 && (
                        <Badge variant="secondary" className="ml-2">
                          +${config.price}
                        </Badge>
                      )}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}

        {/* Current Selection Summary */}
        {(selectedSize || selectedColor || selectedConfiguration) && (
          <div className="pt-2 border-t">
            <Label className="text-xs font-medium text-gray-600">Selected Options:</Label>
            <div className="flex flex-wrap gap-1 mt-1">
              {selectedSize && (
                <Badge variant="outline" className="text-xs">
                  {options.type === 'footwear' ? `Size ${selectedSize}` : selectedSize}
                </Badge>
              )}
              {selectedColor && (
                <Badge variant="outline" className="text-xs">
                  {selectedColor}
                </Badge>
              )}
              {selectedConfiguration && (
                <Badge variant="outline" className="text-xs">
                  {options.configurations?.find(c => c.value === selectedConfiguration)?.label}
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}