"""
Simple test to isolate the regex issue
"""
import re

# Test the regex patterns that might be causing issues
test_content = """
import * as React from "react"
import { cn } from "@/lib/utils"

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border bg-card text-card-foreground shadow-sm",
      className
    )}
    {...props}
  />
))
Card.displayName = "Card"

export { Card }
"""

print("Testing regex patterns...")

try:
    # Test patterns from the AST parser
    patterns_to_test = [
        (r'export\s+default\s+(\w+)', "default export pattern"),
        (r'(?:const|function)\s+(\w+).*=.*React\.forwardRef', "forwardRef pattern"),
        (r'export\s*\{\s*([^}]+)\s*\}', "named exports pattern"),
        (r'import\s*\{\s*([^}]+)\s*\}\s*from\s*[\'"]@/components', "import pattern 1"),
        (r'from\s*[\'"]@/components/ui/(\w+)', "import pattern 2"),
        (r'interface\s+(\w+)Props\s*\{([^}]+)\}', "interface pattern"),
        (r'(\w+)(\?)?:\s*([^;]+);?', "prop pattern"),
        (r'\(\{\s*([^}]+)\s*\}:[^)]*\)', "function prop pattern"),
        (r'<\w+', "jsx element pattern"),
        (r'<[A-Z]\w+', "component reference pattern"),
        (r'useState|useReducer|this\.state', "state pattern"),
        (r'useEffect|useLayoutEffect|componentDidMount', "effects pattern"),
        (r'useContext|createContext|Context\.Provider', "context pattern")
    ]
    
    for pattern, description in patterns_to_test:
        try:
            matches = re.findall(pattern, test_content)
            print(f"✅ {description}: {len(matches)} matches")
            if matches:
                print(f"   Matches: {matches[:3]}")  # Show first 3 matches
        except re.error as e:
            print(f"❌ {description}: REGEX ERROR - {e}")
            print(f"   Pattern: {pattern}")
    
    print("\nTesting workflow keyword extraction...")
    workflow_text = "Display product information with pricing and add to cart"
    try:
        words = re.findall(r'\b\w{3,}\b', workflow_text.lower())
        print(f"✅ Workflow keywords: {words}")
    except re.error as e:
        print(f"❌ Workflow keyword extraction: REGEX ERROR - {e}")

except Exception as e:
    print(f"General error: {e}")
    import traceback
    traceback.print_exc()