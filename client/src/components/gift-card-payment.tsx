import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useMutation } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
import { useToast } from '@/hooks/use-toast';
import { CreditCard, Gift } from 'lucide-react';

interface GiftCardPaymentProps {
  totalAmount: number;
  onGiftCardApplied: (giftCardCode: string, discountAmount: number) => void;
  onRemoveGiftCard: () => void;
  appliedGiftCard?: {
    code: string;
    discountAmount: number;
  };
}

export function GiftCardPayment({
  totalAmount,
  onGiftCardApplied,
  onRemoveGiftCard,
  appliedGiftCard
}: GiftCardPaymentProps) {
  const [giftCardCode, setGiftCardCode] = useState('');
  const { toast } = useToast();

  const validateGiftCardMutation = useMutation({
    mutationFn: async (code: string) => {
      return await apiRequest('GET', `/api/gift-cards/${code}`);
    },
    onSuccess: (data: any) => {
      const discountAmount = Math.min(data.balance, totalAmount);
      onGiftCardApplied(data.code, discountAmount);
      setGiftCardCode('');
      toast({
        title: "Gift card applied successfully",
        description: `$${discountAmount.toFixed(2)} discount applied`,
      });
    },
    onError: (error: any) => {
      toast({
        title: "Invalid gift card",
        description: error.message || "Please check the gift card code and try again.",
        variant: "destructive",
      });
    }
  });

  const handleApplyGiftCard = (e: React.FormEvent) => {
    e.preventDefault();
    if (!giftCardCode.trim()) {
      toast({
        title: "Gift card code required",
        description: "Please enter a gift card code.",
        variant: "destructive",
      });
      return;
    }
    validateGiftCardMutation.mutate(giftCardCode.trim().toUpperCase());
  };

  const handleRemoveGiftCard = () => {
    onRemoveGiftCard();
    toast({
      title: "Gift card removed",
      description: "Gift card discount has been removed from your order.",
    });
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gift className="h-5 w-5 text-purple-600" />
          Gift Card Payment
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {appliedGiftCard ? (
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="bg-purple-100 text-purple-800">
                  {appliedGiftCard.code}
                </Badge>
                <span className="text-sm text-gray-600">
                  Discount: ${appliedGiftCard.discountAmount.toFixed(2)}
                </span>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleRemoveGiftCard}
              >
                Remove
              </Button>
            </div>
            <div className="text-sm text-gray-500">
              Gift card applied successfully! The discount will be deducted from your total.
            </div>
          </div>
        ) : (
          <form onSubmit={handleApplyGiftCard} className="space-y-3">
            <div>
              <Label htmlFor="giftCardCode">Gift Card Code</Label>
              <Input
                id="giftCardCode"
                placeholder="Enter gift card code (e.g., GC-HOLIDAY2024)"
                value={giftCardCode}
                onChange={(e) => setGiftCardCode(e.target.value)}
                className="uppercase"
              />
            </div>
            <Button
              type="submit"
              disabled={validateGiftCardMutation.isPending || !giftCardCode.trim()}
              className="w-full"
            >
              {validateGiftCardMutation.isPending ? 'Validating...' : 'Apply Gift Card'}
            </Button>
            <div className="text-xs text-gray-500">
              Sample gift cards: GC-HOLIDAY2024 ($250), GC-SNEAKER50 ($75)
            </div>
          </form>
        )}
      </CardContent>
    </Card>
  );
}