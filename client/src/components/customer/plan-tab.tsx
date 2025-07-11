import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { queryClient, apiRequest } from '@/lib/queryClient';
import { CheckIcon } from 'lucide-react';

// Define the Plan and Feature types
interface PlanFeature {
  id: number;
  planId: number;
  name: string;
}

interface Plan {
  id: number;
  customerId: string;
  name: string;
  description: string;
  billingCycle: string;
  renewalDate: string;
  monthlyPrice: number;
  autoRenewal: boolean;
  status: string;
  features: PlanFeature[];
}

interface PlanTabProps {
  customerId: string;
  plan?: Plan;
}

const PlanTab: React.FC<PlanTabProps> = ({ customerId, plan }) => {
  const { toast } = useToast();
  const [autoRenewal, setAutoRenewal] = useState(true);
  
  // Set initial auto-renewal state based on plan data
  React.useEffect(() => {
    if (plan) {
      setAutoRenewal(plan.autoRenewal);
    }
  }, [plan]);

  const handleAutoRenewalChange = async (checked: boolean) => {
    try {
      if (!plan) return;
      
      setAutoRenewal(checked);
      await apiRequest('PATCH', `/api/plans/${plan.id}`, { autoRenewal: checked });
      
      toast({
        title: "Auto-renewal updated",
        description: checked ? "Auto-renewal has been enabled" : "Auto-renewal has been disabled",
      });
      
      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: [`/api/plans/${plan.id}`] });
    } catch (error) {
      // Revert UI state on error
      setAutoRenewal(!checked);
      toast({
        title: "Error",
        description: "Failed to update auto-renewal setting",
        variant: "destructive"
      });
    }
  };

  const handleChangePlan = () => {
    toast({
      title: "Not implemented",
      description: "Plan change functionality is not implemented in this demo.",
    });
  };

  if (!plan) {
    return <div className="p-6">No plan information available</div>;
  }

  return (
    <div className="px-4 py-5 sm:p-6">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <h3 className="text-base font-semibold leading-6 text-slate-900">Plan Information</h3>
        <Button
          variant="outline"
          onClick={handleChangePlan}
          className="mt-3 inline-flex items-center text-sm font-medium text-primary sm:mt-0"
        >
          <i className="ri-exchange-line mr-1"></i> Change Plan
        </Button>
      </div>

      <div className="overflow-hidden bg-white shadow sm:rounded-lg">
        <div className="border-b border-slate-200 bg-slate-50 px-4 py-5 sm:px-6">
          <div className="flex items-center">
            <div className="flex-shrink-0 rounded-md bg-primary-100 p-2">
              <i className="ri-vip-diamond-line text-lg text-primary"></i>
            </div>
            <div className="ml-4">
              <h4 className="text-lg font-medium text-slate-900">{plan.name}</h4>
              <p className="text-sm text-slate-500">{plan.description}</p>
            </div>
            <div className="ml-auto">
              <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                plan.status === 'Active' 
                  ? 'bg-green-50 text-green-700' 
                  : 'bg-gray-50 text-gray-700'
              }`}>
                {plan.status}
              </span>
            </div>
          </div>
        </div>

        <div className="px-4 py-5 sm:px-6">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-slate-500">Billing Cycle</dt>
              <dd className="mt-1 text-sm text-slate-900">{plan.billingCycle}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-slate-500">Renewal Date</dt>
              <dd className="mt-1 text-sm text-slate-900">{plan.renewalDate}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-slate-500">Monthly Price</dt>
              <dd className="mt-1 text-sm text-slate-900">${plan.monthlyPrice.toFixed(2)}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-slate-500">Auto-Renewal</dt>
              <dd className="mt-1 text-sm text-slate-900">
                <div className="flex items-center">
                  <span>{autoRenewal ? 'Enabled' : 'Disabled'}</span>
                  <div className="ml-2 flex h-6 items-center">
                    <Switch
                      id="auto-renewal"
                      checked={autoRenewal}
                      onCheckedChange={handleAutoRenewalChange}
                    />
                  </div>
                </div>
              </dd>
            </div>
          </dl>
        </div>

        <div className="px-4 py-5 sm:px-6 border-t border-slate-200">
          <h5 className="text-sm font-medium text-slate-900 mb-4">Plan Features</h5>
          <ul className="space-y-2">
            {plan.features.map((feature: any) => (
              <li key={feature.id} className="flex items-start">
                <div className="flex-shrink-0 text-green-500">
                  <CheckIcon className="h-4 w-4" />
                </div>
                <p className="ml-2 text-sm text-slate-700">{feature.name}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default PlanTab;
