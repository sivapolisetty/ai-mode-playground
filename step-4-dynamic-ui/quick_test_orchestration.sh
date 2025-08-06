#!/bin/bash

# Quick Test Script for Intelligent Orchestration
# Tests 10 diverse queries and shows orchestration results

API_URL="http://localhost:8001/chat"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="quick_test_results_${TIMESTAMP}.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Quick Orchestration Test Suite${NC}"
echo "=============================================="

# Check if server is running
echo "Checking server health..."
if ! curl -s "$API_URL" >/dev/null 2>&1; then
    echo -e "${RED}❌ Cannot connect to server at ${API_URL}${NC}"
    echo "Please ensure the AI backend is running on port 8001"
    exit 1
fi
echo -e "${GREEN}✅ Server is healthy${NC}"
echo

# Test queries array
declare -a queries=(
    "Find laptops under \$2000"
    "Compare iPhone 15 Pro and Samsung Galaxy S24"
    "What's the price and specs of MacBook Air M2?"
    "Show me all Apple products"
    "Find smartphones between \$500 and \$1000"
    "Show me my recent orders"
    "Track my last order"
    "Find alternatives to iPhone 15 Pro under \$900"
    "Compare all smartphones under \$800"
    "I need a laptop for video editing under \$1500 with good graphics"
)

declare -a descriptions=(
    "Simple product search with price constraint"
    "Multi-tool product comparison"
    "Specific product details inquiry"
    "Brand-based filtering"
    "Price range filtering"
    "Customer order history"
    "Order tracking workflow"
    "Alternative product search"
    "Bulk comparison"
    "Complex requirement-based search"
)

# Test each query
total_tests=0
passed_tests=0
orchestration_count=0

echo "{" > "$RESULTS_FILE"
echo "  \"timestamp\": \"$(date -Iseconds)\"," >> "$RESULTS_FILE"
echo "  \"results\": [" >> "$RESULTS_FILE"

for i in "${!queries[@]}"; do
    query="${queries[$i]}"
    description="${descriptions[$i]}"
    test_id="test_$((i+1))"
    
    echo -e "${YELLOW}🧪 Test $((i+1)): ${description}${NC}"
    echo "Query: \"$query\""
    
    # Prepare JSON payload
    payload=$(cat <<EOF
{
    "message": "$query",
    "context": {
        "session_id": "$test_id",
        "customer_id": "cust_001"
    }
}
EOF
)
    
    # Make API call and measure time
    start_time=$(date +%s.%N)
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    end_time=$(date +%s.%N)
    execution_time=$(echo "$end_time - $start_time" | bc)
    
    # Parse response
    if [[ $? -eq 0 && -n "$response" ]]; then
        # Extract key information
        processing_type=$(echo "$response" | jq -r '.debug.processing_type // "unknown"')
        tools_used=$(echo "$response" | jq -r '.debug.tools_used // []' | tr -d '[]" ' | tr ',' ' ')
        ui_count=$(echo "$response" | jq '. .ui_components | length')
        orchestration_reasoning=$(echo "$response" | jq -r '.debug.orchestration.reasoning // "N/A"')
        
        # Determine success
        orchestration_used=false
        if [[ "$processing_type" == "orchestration" ]]; then
            orchestration_used=true
            ((orchestration_count++))
        fi
        
        if [[ "$orchestration_used" == "true" && -n "$tools_used" ]]; then
            echo -e "✅ ${GREEN}PASS${NC} (${execution_time}s)"
            ((passed_tests++))
        else
            echo -e "❌ ${RED}FAIL${NC} (${execution_time}s)"
        fi
        
        echo "   🔧 Tools: $tools_used"
        echo "   🎨 UI Components: $ui_count"
        echo "   🧠 Orchestration: $orchestration_used"
        echo "   💭 Reasoning: $(echo "$orchestration_reasoning" | cut -c1-80)..."
        
        # Add to results file
        if [[ $i -gt 0 ]]; then
            echo "," >> "$RESULTS_FILE"
        fi
        
        echo "    {" >> "$RESULTS_FILE"
        echo "      \"test_id\": \"$test_id\"," >> "$RESULTS_FILE"
        echo "      \"query\": \"$query\"," >> "$RESULTS_FILE"
        echo "      \"description\": \"$description\"," >> "$RESULTS_FILE"
        echo "      \"execution_time\": $execution_time," >> "$RESULTS_FILE"
        echo "      \"orchestration_used\": $orchestration_used," >> "$RESULTS_FILE"
        echo "      \"tools_used\": \"$tools_used\"," >> "$RESULTS_FILE"
        echo "      \"ui_components\": $ui_count," >> "$RESULTS_FILE"
        echo "      \"reasoning\": $(echo "$orchestration_reasoning" | jq -R .)," >> "$RESULTS_FILE"
        echo "      \"success\": $(if [[ "$orchestration_used" == "true" ]]; then echo "true"; else echo "false"; fi)" >> "$RESULTS_FILE"
        echo "    }" >> "$RESULTS_FILE"
        
    else
        echo -e "❌ ${RED}ERROR${NC} - API call failed"
        
        # Add error to results
        if [[ $i -gt 0 ]]; then
            echo "," >> "$RESULTS_FILE"
        fi
        
        echo "    {" >> "$RESULTS_FILE"
        echo "      \"test_id\": \"$test_id\"," >> "$RESULTS_FILE"
        echo "      \"query\": \"$query\"," >> "$RESULTS_FILE"
        echo "      \"error\": \"API call failed\"," >> "$RESULTS_FILE"
        echo "      \"success\": false" >> "$RESULTS_FILE"
        echo "    }" >> "$RESULTS_FILE"
    fi
    
    ((total_tests++))
    echo
    
    # Brief pause between tests
    sleep 1
done

# Close results file
echo "  ]," >> "$RESULTS_FILE"
echo "  \"summary\": {" >> "$RESULTS_FILE"
echo "    \"total_tests\": $total_tests," >> "$RESULTS_FILE"
echo "    \"passed_tests\": $passed_tests," >> "$RESULTS_FILE"
echo "    \"orchestration_count\": $orchestration_count," >> "$RESULTS_FILE"
echo "    \"pass_rate\": \"$passed_tests/$total_tests ($(echo "scale=1; $passed_tests*100/$total_tests" | bc)%)\"," >> "$RESULTS_FILE"
echo "    \"orchestration_rate\": \"$orchestration_count/$total_tests ($(echo "scale=1; $orchestration_count*100/$total_tests" | bc)%)\"" >> "$RESULTS_FILE"
echo "  }" >> "$RESULTS_FILE"
echo "}" >> "$RESULTS_FILE"

# Print summary
echo "=============================================="
echo -e "${BLUE}📊 SUMMARY REPORT${NC}"
echo "=============================================="
echo -e "✅ Pass Rate: $passed_tests/$total_tests ($(echo "scale=1; $passed_tests*100/$total_tests" | bc)%)"
echo -e "🎭 Orchestration Usage: $orchestration_count/$total_tests ($(echo "scale=1; $orchestration_count*100/$total_tests" | bc)%)"
echo

if [[ $orchestration_count -eq $total_tests ]]; then
    echo -e "${GREEN}🎉 Perfect! All queries used intelligent orchestration${NC}"
elif [[ $orchestration_count -gt $((total_tests/2)) ]]; then
    echo -e "${YELLOW}✨ Good! Most queries used intelligent orchestration${NC}"
else
    echo -e "${RED}⚠️  Some queries fell back to traditional processing${NC}"
fi

echo
echo -e "💾 Detailed results saved to: ${GREEN}$RESULTS_FILE${NC}"
echo

# Show a sample of the orchestration reasoning
echo -e "${BLUE}🧠 Sample Orchestration Reasoning:${NC}"
echo "=============================================="
sample_reasoning=$(jq -r '.results[0].reasoning // "No reasoning captured"' "$RESULTS_FILE" 2>/dev/null)
echo "$sample_reasoning" | fold -w 60 -s
echo "=============================================="