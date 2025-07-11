import React from 'react';
import { cn } from '@/lib/utils';

export type TabKey = 'profile' | 'plan' | 'devices' | 'orders' | 'billing';

interface Tab {
  key: TabKey;
  label: string;
}

interface CustomerTabsProps {
  activeTab: TabKey;
  setActiveTab: (tab: TabKey) => void;
}

const CustomerTabs: React.FC<CustomerTabsProps> = ({ activeTab, setActiveTab }) => {
  const tabs: Tab[] = [
    { key: 'profile', label: 'Profile' },
    { key: 'plan', label: 'Plan' },
    { key: 'devices', label: 'Devices' },
    { key: 'orders', label: 'Orders' },
    { key: 'billing', label: 'Billing' },
  ];

  return (
    <div className="border-b border-slate-200">
      <nav className="-mb-px flex" aria-label="Tabs">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "whitespace-nowrap border-b-2 py-4 px-4 text-sm font-medium",
              activeTab === tab.key
                ? "border-primary text-primary"
                : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700"
            )}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

export default CustomerTabs;
