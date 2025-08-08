import * as React from "react"
import { cn } from "@/lib/utils"

// Import all available UI components
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "./card"
import { Button } from "./button"
import { Input } from "./input"
import { Badge } from "./badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./select"
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "./pagination"
import { Textarea } from "./textarea"
import { Checkbox } from "./checkbox"
import { RadioGroup, RadioGroupItem } from "./radio-group"
import { Switch } from "./switch"
import { Label } from "./label"
import { Progress } from "./progress"
import { Separator } from "./separator"
import { Alert, AlertDescription, AlertTitle } from "./alert"
import { Avatar, AvatarFallback, AvatarImage } from "./avatar"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "./dialog"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./table"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./tabs"
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "./accordion"

// Import business components - these are shared between traditional and dynamic UI
import { ProductCard, ProductList, OrderCard, AddressCard, AddressForm, AddressList, CartItem } from "../business"

// Component specification types
export interface UIComponentSpec {
  type: string
  props?: Record<string, any>
  children?: React.ReactNode | string
  actions?: UIAction[]
  layout?: {
    position?: "inline" | "modal" | "sidebar"
    priority?: "high" | "medium" | "low"
  }
  validation?: {
    required?: boolean
    pattern?: string
    minLength?: number
    maxLength?: number
  }
}

export interface UIAction {
  event: string
  action: string
  payload?: Record<string, any>
}

export interface DynamicUISpec {
  ui_components: UIComponentSpec[]
  layout_strategy: "single_component" | "composition" | "workflow" | "text_only"
  user_intent: string
  success_criteria?: string
  validation?: {
    total_requested: number
    validated: number
    success: boolean
  }
}

// Action handler type
export type UIActionHandler = (action: string, payload?: Record<string, any>) => void | Promise<void>

// Component mapping registry
const COMPONENT_REGISTRY: Record<string, React.ComponentType<any>> = {
  // Business components (shared between traditional and dynamic UI)
  productcard: ProductCard,
  productlist: ProductList,
  ordercard: OrderCard,
  addresscard: AddressCard,
  addressform: AddressForm,
  addresslist: AddressList,
  cartitem: CartItem,
  
  // Layout components
  card: Card,
  cardheader: CardHeader,
  cardcontent: CardContent,
  cardfooter: CardFooter,
  cardtitle: CardTitle,
  carddescription: CardDescription,
  
  // Input components
  button: Button,
  input: Input,
  textarea: Textarea,
  checkbox: Checkbox,
  radiogroup: RadioGroup,
  radiogroupitem: RadioGroupItem,
  switch: Switch,
  label: Label,
  
  // Selection components
  select: Select,
  selectcontent: SelectContent,
  selectitem: SelectItem,
  selecttrigger: SelectTrigger,
  selectvalue: SelectValue,
  
  // Navigation components
  pagination: Pagination,
  paginationcontent: PaginationContent,
  paginationitem: PaginationItem,
  paginationlink: PaginationLink,
  paginationnext: PaginationNext,
  paginationprevious: PaginationPrevious,
  
  // Display components
  badge: Badge,
  progress: Progress,
  separator: Separator,
  alert: Alert,
  alertdescription: AlertDescription,
  alerttitle: AlertTitle,
  avatar: Avatar,
  avatarfallback: AvatarFallback,
  avatarimage: AvatarImage,
  
  // Dialog components
  dialog: Dialog,
  dialogcontent: DialogContent,
  dialogdescription: DialogDescription,
  dialogfooter: DialogFooter,
  dialogheader: DialogHeader,
  dialogtitle: DialogTitle,
  dialogtrigger: DialogTrigger,
  
  // Data components
  table: Table,
  tablebody: TableBody,
  tablecell: TableCell,
  tablehead: TableHead,
  tableheader: TableHeader,
  tablerow: TableRow,
  
  // Navigation/Organization  
  tabs: ({ children, defaultSelected, ...props }: any) => {
    return (
      <Tabs defaultValue={defaultSelected} {...props}>
        <TabsList>
          {children}
        </TabsList>
      </Tabs>
    )
  },
  tabscontent: TabsContent,
  tabslist: TabsList,
  tabstrigger: TabsTrigger,
  TabsTrigger: ({ id, children, ...props }: any) => (
    <TabsTrigger value={id} {...props}>
      {children}
    </TabsTrigger>
  ),
  accordion: Accordion,
  accordioncontent: AccordionContent,
  accordionitem: AccordionItem,
  accordiontrigger: AccordionTrigger,
  
  // List components (generic HTML elements)
  list: ({ className, children, ...props }: any) => (
    <ul className={`space-y-2 ${className || ''}`} {...props}>
      {children}
    </ul>
  ),
  listitem: ({ className, children, ...props }: any) => (
    <li className={`${className || ''}`} {...props}>
      {children}
    </li>
  ),
  
  // Generic div wrapper
  div: ({ className, children, ...props }: any) => (
    <div className={className} {...props}>
      {children}
    </div>
  ),
}

// Template variable replacement utility
const replaceTemplateVariables = (value: any, context: Record<string, any> = {}): any => {
  if (typeof value === 'string') {
    // Replace template variables like {{product.id}}
    return value.replace(/\{\{([^}]+)\}\}/g, (match, path) => {
      const keys = path.split('.')
      let result = context
      for (const key of keys) {
        result = result?.[key]
        if (result === undefined) break
      }
      return result !== undefined ? String(result) : match
    })
  }
  
  if (Array.isArray(value)) {
    return value.map(item => replaceTemplateVariables(item, context))
  }
  
  if (value && typeof value === 'object') {
    const result: Record<string, any> = {}
    for (const [key, val] of Object.entries(value)) {
      result[key] = replaceTemplateVariables(val, context)
    }
    return result
  }
  
  return value
}

// Individual component renderer
interface DynamicComponentProps {
  spec: UIComponentSpec
  onAction: UIActionHandler
  context?: Record<string, any>
  index?: number
}

const DynamicComponent: React.FC<DynamicComponentProps> = ({ 
  spec, 
  onAction, 
  context = {}, 
  index = 0 
}) => {
  const componentType = spec.type.toLowerCase().replace(/[-_]/g, '')
  const Component = COMPONENT_REGISTRY[componentType]
  
  if (!Component) {
    console.warn(`Unknown component type: ${spec.type}`)
    return (
      <div className="p-4 border border-dashed border-gray-300 rounded-lg bg-gray-50">
        <p className="text-sm text-gray-600">
          Unknown component: <code>{spec.type}</code>
        </p>
      </div>
    )
  }
  
  // Process props with template variable replacement
  const processedProps = React.useMemo(() => {
    const props = replaceTemplateVariables(spec.props || {}, context)
    
    // Add action handlers
    if (spec.actions) {
      spec.actions.forEach(action => {
        const eventHandler = (event: any) => {
          event.preventDefault?.()
          
          // Process payload with template variables and event data
          const payload = replaceTemplateVariables(action.payload || {}, {
            ...context,
            event: {
              value: event.target?.value,
              checked: event.target?.checked,
              type: event.type,
            }
          })
          
          onAction(action.action, payload)
        }
        
        // Map common events
        switch (action.event) {
          case 'onClick':
            props.onClick = eventHandler
            break
          case 'onChange':
            props.onChange = eventHandler
            break
          case 'onValueChange':
            props.onValueChange = eventHandler
            break
          case 'onSubmit':
            props.onSubmit = eventHandler
            break
          case 'onSelect':
            props.onSelect = eventHandler
            break
          default:
            props[action.event] = eventHandler
        }
      })
    }
    
    return props
  }, [spec.props, spec.actions, context, onAction])
  
  // Process children with template replacement and nested component rendering
  const processedChildren = React.useMemo(() => {
    const children = replaceTemplateVariables(spec.children, context)
    
    // If children is an array of component specifications, render them recursively
    if (Array.isArray(children)) {
      return children.map((child, index) => {
        if (child && typeof child === 'object' && child.type) {
          // This is a nested component specification
          return (
            <DynamicComponent
              key={`nested-${index}`}
              spec={child}
              onAction={onAction}
              context={context}
              index={index}
            />
          )
        }
        // Regular content
        return child
      })
    }
    
    // If children is a single component specification, render it
    if (children && typeof children === 'object' && children.type) {
      return (
        <DynamicComponent
          key="nested-single"
          spec={children}
          onAction={onAction}
          context={context}
          index={0}
        />
      )
    }
    
    // Regular string or element content
    return children
  }, [spec.children, context, onAction])
  
  // Add layout classes based on position and priority
  const layoutClasses = React.useMemo(() => {
    const classes: string[] = []
    
    if (spec.layout?.position === 'modal') {
      classes.push('fixed', 'inset-0', 'z-50')
    } else if (spec.layout?.position === 'sidebar') {
      classes.push('w-64', 'h-full')
    }
    
    if (spec.layout?.priority === 'high') {
      classes.push('order-first')
    } else if (spec.layout?.priority === 'low') {
      classes.push('order-last')
    }
    
    return classes.join(' ')
  }, [spec.layout])
  
  const finalClassName = cn(processedProps.className, layoutClasses)
  
  // Handle special props for specific components
  const finalProps = { ...processedProps, className: finalClassName }
  
  // Handle special children patterns
  let finalChildren = processedChildren
  
  // For buttons, if there's a 'text' prop, use it as children
  if (processedProps.text) {
    finalChildren = processedProps.text
  }
  
  // Smart component detection - use business components when appropriate
  if (componentType === 'card' && processedProps.title && processedProps.price) {
    // This looks like a product card - use the shared ProductCard component
    return (
      <ProductCard
        {...processedProps}
        actions={spec.actions}
        onAction={onAction}
        className={cn(processedProps.className, layoutClasses)}
        key={`dynamic-product-card-${index}`}
      />
    )
  }

  // Detect OrderCard based on order-specific props or explicit type
  if ((componentType === 'card' || componentType === 'ordercard' || componentType === 'order_card') && 
      (processedProps.id && processedProps.status && processedProps.total || 
       processedProps.order_id || componentType === 'order_card')) {
    // This looks like an order card - use the shared OrderCard component
    const orderProps = {
      id: processedProps.id || processedProps.order_id,
      status: processedProps.status,
      total: processedProps.total,
      createdAt: processedProps.createdAt || processedProps.date,
      trackingNumber: processedProps.trackingNumber,
      items: processedProps.items || [],
      ...processedProps
    }
    
    return (
      <OrderCard
        {...orderProps}
        actions={spec.actions}
        onAction={onAction}
        className={cn(processedProps.className, layoutClasses)}
        key={`dynamic-order-card-${index}`}
      />
    )
  }

  // Detect AddressCard based on address-specific props or explicit type
  if ((componentType === 'card' || componentType === 'addresscard' || componentType === 'address_card') && 
      (processedProps.street && processedProps.city || componentType === 'addresscard' || componentType === 'address_card')) {
    // This looks like an address card - use the shared AddressCard component
    return (
      <AddressCard
        {...processedProps}
        actions={spec.actions}
        onAction={onAction}
        className={cn(processedProps.className, layoutClasses)}
        key={`dynamic-address-card-${index}`}
      />
    )
  }

  // Detect AddressForm based on form-specific props or explicit type
  if (componentType === 'addressform' || componentType === 'address_form') {
    // This is an address form - use the shared AddressForm component
    return (
      <AddressForm
        {...processedProps}
        onSubmit={(data) => onAction('submit_address', data)}
        onCancel={() => onAction('cancel_address', {})}
        className={cn(processedProps.className, layoutClasses)}
        key={`dynamic-address-form-${index}`}
      />
    )
  }

  // Detect CartItem based on cart-specific props or explicit type
  if (componentType === 'cartitem' || componentType === 'cart_item' || 
      (processedProps.name && processedProps.price && processedProps.quantity && processedProps.brand)) {
    // This looks like a cart item - use the shared CartItem component
    return (
      <CartItem
        {...processedProps}
        onAction={onAction}
        className={cn(processedProps.className, layoutClasses)}
        key={`dynamic-cart-item-${index}`}
      />
    )
  }
  
  // For regular cards with title prop, wrap children in CardHeader + CardContent
  if (componentType === 'card' && processedProps.title) {
    const CardHeader = COMPONENT_REGISTRY['cardheader']
    const CardTitle = COMPONENT_REGISTRY['cardtitle'] 
    const CardDescription = COMPONENT_REGISTRY['carddescription']
    const CardContent = COMPONENT_REGISTRY['cardcontent']
    
    finalChildren = (
      <>
        <CardHeader>
          <CardTitle>{processedProps.title}</CardTitle>
          {processedProps.description && (
            <CardDescription>{processedProps.description}</CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {processedChildren}
        </CardContent>
      </>
    )
    
    // Remove title from props since we handled it
    delete finalProps.title
    delete finalProps.description
  }
  
  
  return (
    <Component
      {...finalProps}
      key={`dynamic-component-${index}`}
    >
      {finalChildren}
    </Component>
  )
}

// Main Dynamic UI Renderer component
export interface DynamicUIRendererProps {
  uiSpec: DynamicUISpec
  onAction: UIActionHandler
  context?: Record<string, any>
  className?: string
}

export const DynamicUIRenderer: React.FC<DynamicUIRendererProps> = ({
  uiSpec,
  onAction,
  context = {},
  className
}) => {
  // Handle empty or invalid specs
  if (!uiSpec.ui_components || uiSpec.ui_components.length === 0) {
    return null
  }
  
  // Apply layout strategy classes
  const getLayoutClasses = () => {
    switch (uiSpec.layout_strategy) {
      case 'single_component':
        return 'flex flex-col items-center'
      case 'composition':
        return 'grid gap-4 md:grid-cols-2 lg:grid-cols-3'
      case 'workflow':
        return 'flex flex-col space-y-4'
      default:
        return 'space-y-4'
    }
  }
  
  return (
    <div 
      className={cn(
        "dynamic-ui-container",
        getLayoutClasses(),
        className
      )}
      data-layout-strategy={uiSpec.layout_strategy}
      data-user-intent={uiSpec.user_intent}
    >
      {uiSpec.ui_components.map((componentSpec, index) => (
        <DynamicComponent
          key={`ui-component-${index}`}
          spec={componentSpec}
          onAction={onAction}
          context={context}
          index={index}
        />
      ))}
      
      {/* Validation indicator */}
      {uiSpec.validation && !uiSpec.validation.success && (
        <div className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded border">
          ⚠️ Some UI components may not render correctly 
          ({uiSpec.validation.validated}/{uiSpec.validation.total_requested} validated)
        </div>
      )}
    </div>
  )
}

// Hook for managing UI state and actions
export const useDynamicUI = () => {
  const [currentSpec, setCurrentSpec] = React.useState<DynamicUISpec | null>(null)
  const [actionHistory, setActionHistory] = React.useState<Array<{action: string, payload?: any, timestamp: number}>>([])
  
  const handleAction: UIActionHandler = React.useCallback(async (action: string, payload?: Record<string, any>) => {
    console.log('Dynamic UI Action:', action, payload)
    
    // Log action
    setActionHistory(prev => [...prev, {
      action,
      payload,
      timestamp: Date.now()
    }])
    
    // Handle common actions
    switch (action) {
      case 'view_product':
        console.log('View product:', payload?.productId)
        // Implement product view logic
        break
        
      case 'add_to_cart':
        console.log('Add to cart:', payload)
        // Implement add to cart logic
        break
        
      case 'filter_products':
        console.log('Filter products:', payload?.query)
        // Implement product filtering
        break
        
      case 'navigate_page':
        console.log('Navigate to page:', payload?.page)
        // Implement pagination
        break
        
      case 'open_tracking':
        console.log('Open tracking:', payload?.trackingNumber)
        // Implement order tracking
        break
        
      default:
        console.log('Unhandled action:', action, payload)
    }
  }, [])
  
  const updateUISpec = React.useCallback((spec: DynamicUISpec) => {
    setCurrentSpec(spec)
  }, [])
  
  const clearUI = React.useCallback(() => {
    setCurrentSpec(null)
  }, [])
  
  return {
    currentSpec,
    actionHistory,
    handleAction,
    updateUISpec,
    clearUI
  }
}

// Export component registry for external use
export { COMPONENT_REGISTRY }