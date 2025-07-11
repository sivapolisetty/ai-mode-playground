import React from 'react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { queryClient, apiRequest } from '@/lib/queryClient';

interface Device {
  id: number;
  customerId: string;
  name: string;
  type: string;
  status: string;
  lastActive: string;
  ipAddress?: string;
}

interface DevicesTabProps {
  customerId: string;
  devices?: Device[];
}

const DevicesTab: React.FC<DevicesTabProps> = ({ customerId, devices = [] }) => {
  const { toast } = useToast();

  const handleAddDevice = () => {
    toast({
      title: "Not implemented",
      description: "Add device functionality is not implemented in this demo.",
    });
  };

  const handleEditDevice = (deviceId: number) => {
    toast({
      title: "Not implemented",
      description: `Edit device functionality is not implemented in this demo. Device ID: ${deviceId}`,
    });
  };

  // Render device type icon based on type
  const renderDeviceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'mobile':
        return <i className="ri-smartphone-line text-lg text-slate-600"></i>;
      case 'laptop':
        return <i className="ri-macbook-line text-lg text-slate-600"></i>;
      case 'tablet':
        return <i className="ri-tablet-line text-lg text-slate-600"></i>;
      default:
        return <i className="ri-device-line text-lg text-slate-600"></i>;
    }
  };

  return (
    <div className="px-4 py-5 sm:p-6">
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <h3 className="text-base font-semibold leading-6 text-slate-900">Device Information</h3>
        <Button
          variant="outline"
          onClick={handleAddDevice}
          className="mt-3 inline-flex items-center text-sm font-medium text-primary sm:mt-0"
        >
          <i className="ri-add-line mr-1"></i> Add Device
        </Button>
      </div>

      <div className="mt-4 flow-root">
        <div className="-mx-4 -my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
          <div className="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
            <table className="min-w-full divide-y divide-slate-200">
              <thead>
                <tr>
                  <th scope="col" className="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-slate-900 sm:pl-0">Device</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Status</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">Last Active</th>
                  <th scope="col" className="px-3 py-3.5 text-left text-sm font-semibold text-slate-900">IP Address</th>
                  <th scope="col" className="relative py-3.5 pl-3 pr-4 sm:pr-0">
                    <span className="sr-only">Edit</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {devices.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-4 text-center text-sm text-slate-500">
                      No devices found for this customer.
                    </td>
                  </tr>
                ) : (
                  devices.map((device: any) => (
                    <tr key={device.id}>
                      <td className="whitespace-nowrap py-4 pl-4 pr-3 text-sm sm:pl-0">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-md bg-slate-100">
                            {renderDeviceIcon(device.type)}
                          </div>
                          <div className="ml-4">
                            <div className="font-medium text-slate-900">{device.name}</div>
                            <div className="text-slate-500">{device.type}</div>
                          </div>
                        </div>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">
                        <span className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-medium ${
                          device.status === 'Online' 
                            ? 'bg-green-50 text-green-700' 
                            : 'bg-gray-50 text-gray-700'
                        }`}>
                          {device.status}
                        </span>
                      </td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">{device.lastActive}</td>
                      <td className="whitespace-nowrap px-3 py-4 text-sm text-slate-500">{device.ipAddress || 'N/A'}</td>
                      <td className="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                        <Button
                          variant="link"
                          onClick={() => handleEditDevice(device.id)}
                          className="text-primary hover:text-primary-700"
                        >
                          Edit
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DevicesTab;
