import React, { useState } from 'react'
import { DynamicUIRenderer, useDynamicUI, type DynamicUISpec } from './dynamic-ui-renderer'
import { Button } from './button'
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { Badge } from './badge'

// Sample UI specifications for testing
const sampleSpecs: Record<string, DynamicUISpec> = {
  productSearch: {
    ui_components: [
      {
        type: "card",
        props: {
          className: "product-search-container"
        },
        children: "Product Search Results",
        layout: {
          position: "inline",
          priority: "high"
        }
      },
      {
        type: "input",
        props: {
          placeholder: "Search products...",
          type: "search",
          className: "w-full"
        },
        actions: [
          {
            event: "onChange",
            action: "filter_products",
            payload: {
              query: "{{event.value}}"
            }
          }
        ],
        layout: {
          position: "inline",
          priority: "high"
        }
      },
      {
        type: "select",
        props: {
          placeholder: "Filter by category"
        },
        actions: [
          {
            event: "onValueChange",
            action: "filter_category",
            payload: {
              category: "{{event.value}}"
            }
          }
        ],
        layout: {
          position: "inline",
          priority: "medium"
        }
      },
      {
        type: "button",
        props: {
          variant: "default",
          className: "w-full"
        },
        children: "Search Products",
        actions: [
          {
            event: "onClick",
            action: "execute_search",
            payload: {
              timestamp: "{{Date.now()}}"
            }
          }
        ],
        layout: {
          position: "inline",
          priority: "medium"
        }
      }
    ],
    layout_strategy: "composition",
    user_intent: "product_discovery_and_browsing",
    success_criteria: "User can search and filter products effectively"
  },

  orderTracking: {
    ui_components: [
      {
        type: "card",
        props: {
          className: "order-status-card"
        },
        children: "Order #12345 Status",
        layout: {
          position: "inline",
          priority: "high"
        }
      },
      {
        type: "badge",
        props: {
          variant: "secondary",
          className: "mb-2"
        },
        children: "Shipped",
        layout: {
          position: "inline",
          priority: "high"
        }
      },
      {
        type: "button",
        props: {
          variant: "outline",
          className: "mt-2"
        },
        children: "Track Package",
        actions: [
          {
            event: "onClick",
            action: "open_tracking",
            payload: {
              trackingNumber: "1Z999AA1234567890",
              orderId: "12345"
            }
          }
        ],
        layout: {
          position: "inline",
          priority: "medium"
        }
      }
    ],
    layout_strategy: "workflow",
    user_intent: "order_status_inquiry",
    success_criteria: "User can view order status and access tracking"
  },

  checkout: {
    ui_components: [
      {
        type: "card",
        props: {
          className: "checkout-form"
        },
        children: "Complete Your Purchase",
        layout: {
          position: "inline",
          priority: "high"
        }
      },
      {
        type: "input",
        props: {
          placeholder: "Enter shipping address",
          className: "w-full mb-2"
        },
        actions: [
          {
            event: "onChange",
            action: "update_address",
            payload: {
              field: "shipping",
              value: "{{event.value}}"
            }
          }
        ]
      },
      {
        type: "select",
        props: {
          placeholder: "Payment method"
        },
        actions: [
          {
            event: "onValueChange",
            action: "select_payment",
            payload: {
              method: "{{event.value}}"
            }
          }
        ]
      },
      {
        type: "button",
        props: {
          variant: "default",
          className: "w-full mt-4",
          size: "lg"
        },
        children: "Complete Order",
        actions: [
          {
            event: "onClick",
            action: "submit_order",
            payload: {
              total: 299.99,
              currency: "USD"
            }
          }
        ],
        layout: {
          position: "inline",
          priority: "high"
        }
      }
    ],
    layout_strategy: "workflow",
    user_intent: "checkout_completion",
    success_criteria: "User successfully completes purchase"
  },

  customerProfile: {
    ui_components: [
      {
        type: "card",
        props: {
          className: "profile-card"
        },
        children: "Customer Profile",
        layout: {
          position: "inline",
          priority: "high"
        }
      },
      {
        type: "input",
        props: {
          placeholder: "Full Name",
          value: "John Doe",
          className: "mb-2"
        },
        actions: [
          {
            event: "onChange",
            action: "update_profile",
            payload: {
              field: "name",
              value: "{{event.value}}"
            }
          }
        ]
      },
      {
        type: "input",
        props: {
          placeholder: "Email Address",
          value: "john@example.com",
          type: "email",
          className: "mb-2"
        },
        actions: [
          {
            event: "onChange",
            action: "update_profile",
            payload: {
              field: "email",
              value: "{{event.value}}"
            }
          }
        ]
      },
      {
        type: "textarea",
        props: {
          placeholder: "Additional notes",
          className: "mb-4"
        },
        actions: [
          {
            event: "onChange",
            action: "update_profile",
            payload: {
              field: "notes",
              value: "{{event.value}}"
            }
          }
        ]
      },
      {
        type: "button",
        props: {
          variant: "default"
        },
        children: "Save Changes",
        actions: [
          {
            event: "onClick",
            action: "save_profile",
            payload: {
              timestamp: "{{Date.now()}}"
            }
          }
        ]
      }
    ],
    layout_strategy: "single_component",
    user_intent: "profile_management",
    success_criteria: "User can update and save profile information"
  }
}

export const DynamicUITest: React.FC = () => {
  const [currentSpec, setCurrentSpec] = useState<string>('productSearch')
  const [actionLog, setActionLog] = useState<Array<{action: string, payload?: any, timestamp: number}>>([])
  const { handleAction } = useDynamicUI()

  const customActionHandler = (action: string, payload?: Record<string, any>) => {
    const logEntry = {
      action,
      payload,
      timestamp: Date.now()
    }
    
    setActionLog(prev => [...prev.slice(-9), logEntry]) // Keep last 10 actions
    
    // Call the default handler
    handleAction(action, payload)
    
    // Custom test logging
    console.log('🧪 Test Action:', logEntry)
  }

  const currentSpecData = sampleSpecs[currentSpec]

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dynamic UI Renderer Test
        </h1>
        <p className="text-gray-600">
          Testing various UI component specifications and interactions
        </p>
      </div>

      {/* Test Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Test Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2 mb-4">
            {Object.keys(sampleSpecs).map((specKey) => (
              <Button
                key={specKey}
                variant={currentSpec === specKey ? "default" : "outline"}
                onClick={() => setCurrentSpec(specKey)}
                size="sm"
              >
                {specKey.replace(/([A-Z])/g, ' $1').toLowerCase()}
              </Button>
            ))}
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <Badge variant="secondary">
                {currentSpecData.ui_components.length} components
              </Badge>
              <Badge variant="outline">
                {currentSpecData.layout_strategy}
              </Badge>
              <Badge variant="outline">
                {currentSpecData.user_intent}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* UI Renderer Test Area */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <div className="w-5 h-5 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <i className="text-white text-xs">🎨</i>
            </div>
            Dynamic UI Renderer Output
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-6">
            <DynamicUIRenderer
              uiSpec={currentSpecData}
              onAction={customActionHandler}
              context={{
                customerId: "TEST-001",
                sessionId: "test-session",
                product: { id: "product-123", name: "Test Product" },
                user: { name: "Test User", email: "test@example.com" }
              }}
              className="test-dynamic-ui"
            />
          </div>
        </CardContent>
      </Card>

      {/* Action Log */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Action Log
            <Button
              variant="outline"
              size="sm"
              onClick={() => setActionLog([])}
            >
              Clear Log
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {actionLog.length === 0 ? (
            <p className="text-gray-500 text-sm">
              No actions logged yet. Interact with the UI components above to see actions here.
            </p>
          ) : (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {actionLog.map((entry, index) => (
                <div
                  key={index}
                  className="bg-gray-50 rounded border p-3 text-sm font-mono"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-semibold text-blue-600">
                      {entry.action}
                    </span>
                    <span className="text-gray-500 text-xs">
                      {new Date(entry.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {entry.payload && (
                    <pre className="text-gray-700 whitespace-pre-wrap">
                      {JSON.stringify(entry.payload, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Specification Details */}
      <Card>
        <CardHeader>
          <CardTitle>Current Specification</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-50 rounded p-4">
            <pre className="text-sm overflow-x-auto">
              {JSON.stringify(currentSpecData, null, 2)}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default DynamicUITest