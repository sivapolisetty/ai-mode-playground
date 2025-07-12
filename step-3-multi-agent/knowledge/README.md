# Knowledge Base Management for Product Owners

## Overview

This directory contains the knowledge base files that power the AI assistant's ability to answer customer questions about policies, procedures, and business rules. These files are designed to be easily updated by product owners and business stakeholders without technical knowledge.

## Files Structure

### 📋 `faq.json` - Frequently Asked Questions
Contains common customer questions and their answers. Each entry includes:
- **Question**: The customer's question
- **Answer**: The detailed response
- **Category**: Topic area (shipping, returns, payments, etc.)
- **Tags**: Keywords for better search matching

### 📋 `business_rules.json` - Business Rules and Policies
Contains business rules, policies, and procedures in plain text format. Each entry includes:
- **Title**: Brief rule name
- **Description**: Detailed explanation in business language
- **Keywords**: Important terms for search matching
- **Applies to**: Who or what the rule affects
- **Exceptions**: Any special cases or exclusions

## How to Update the Knowledge Base

### Adding New FAQ Entries

1. Open `faq.json`
2. Add a new entry following this format:

```json
{
  "id": "faq_016",
  "category": "shipping",
  "question": "Do you ship internationally?",
  "answer": "Yes, we ship to over 50 countries worldwide. International shipping costs and delivery times vary by destination. Some items may have shipping restrictions based on local regulations.",
  "tags": ["international", "shipping", "worldwide", "global"],
  "metadata": {
    "last_updated": "2024-01-15",
    "priority": "medium"
  }
}
```

**Fields Explanation**:
- `id`: Unique identifier (increment the number)
- `category`: Topic area (shipping, returns, payments, account, support, discounts, technical, products)
- `question`: Exactly how customers might ask the question
- `answer`: Complete, helpful answer in plain language
- `tags`: Keywords customers might use when searching
- `metadata`: Administrative information

### Adding New Business Rules

1. Open `business_rules.json`
2. Add a new entry following this format:

```json
{
  "id": "rule_013",
  "category": "shipping",
  "title": "Same-Day Delivery Policy",
  "description": "Same-day delivery is available for orders placed before 2 PM in select metropolitan areas. Additional fees apply. Available Monday through Friday only, excluding holidays.",
  "keywords": ["same-day delivery", "2 PM cutoff", "metropolitan areas", "additional fees"],
  "applies_to": "Orders in select cities placed before 2 PM",
  "exceptions": "Not available weekends or holidays",
  "effective_date": "2024-01-01",
  "last_updated": "2024-01-15",
  "created_by": "Shipping Team"
}
```

**Fields Explanation**:
- `id`: Unique identifier (increment the number)
- `category`: Business area (shipping, discounts, returns, security, loyalty, promotions, pricing, payments, warranties, customer_service)
- `title`: Short, descriptive name for the rule
- `description`: Full explanation in business language that customers can understand
- `keywords`: Important terms that customers might search for
- `applies_to`: Clear statement of scope and applicability
- `exceptions`: Any special cases, exclusions, or limitations
- `effective_date`: When the rule became active
- `last_updated`: When it was last modified
- `created_by`: Team or person responsible

### Best Practices

#### Writing Good FAQ Entries
- **Use customer language**: Write questions as customers would ask them
- **Be complete**: Include all relevant information in the answer
- **Stay current**: Update answers when policies change
- **Add context**: Explain not just "what" but "why" when helpful

#### Writing Good Business Rules
- **Use plain language**: Avoid technical jargon or system terminology
- **Be specific**: Include exact thresholds, timeframes, and conditions
- **Explain impact**: Help customers understand what the rule means for them
- **Include examples**: When helpful, add "For example..." scenarios

#### Categories to Use

**FAQ Categories**:
- `shipping` - Delivery, shipping costs, timeframes
- `returns` - Return process, refunds, exchanges
- `payments` - Payment methods, billing, charges
- `account` - Account creation, login, profile management
- `support` - Customer service, contact information
- `discounts` - Coupons, promotions, loyalty programs
- `technical` - Website issues, app problems
- `products` - Product information, warranties, availability

**Business Rule Categories**:
- `shipping` - Shipping policies and procedures
- `discounts` - Discount and promotion rules
- `returns` - Return and refund policies
- `security` - Security and fraud prevention
- `loyalty` - VIP and loyalty program rules
- `promotions` - Sale and promotional policies
- `pricing` - Pricing policies and price matching
- `payments` - Payment processing rules
- `warranties` - Warranty and service policies
- `customer_service` - Support procedures and escalation

## After Making Changes

### Updating the AI System

After adding or modifying entries in either file:

1. **Save the file** with your changes
2. **Re-seed the database** by running:
   ```bash
   cd step-2-rag-integration
   ./setup.sh seed
   ```
3. **Test your changes** by asking the AI assistant questions related to your updates

### Testing Your Updates

Try asking questions that should match your new entries:

```bash
# Test FAQ updates
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Your new FAQ question here"}'

# Test business rule updates  
curl -X POST http://localhost:8002/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Question about your new business rule"}'
```

## Common Scenarios

### Updating Shipping Policies
When shipping policies change:
1. Update relevant entries in `business_rules.json`
2. Update related FAQ entries in `faq.json`
3. Re-seed the database
4. Test with questions like "What's your shipping policy?"

### Adding New Promotions
When running new promotions:
1. Add promotion details to `business_rules.json`
2. Add customer-facing FAQ if needed
3. Set `active: true` to enable, `active: false` to disable
4. Re-seed the database

### Seasonal Updates
For holiday policies or temporary changes:
1. Add entries with clear `effective_date` and end dates in description
2. Use `active: false` to disable expired promotions
3. Update regularly to keep information current

## Support

If you need help with the knowledge base format or have questions about updating entries:

1. **Check examples**: Look at existing entries for formatting guidance
2. **Test changes**: Always test your updates before going live
3. **Ask developers**: Contact the development team for technical assistance
4. **Document changes**: Keep track of what you changed and when

## Version History

- **v1.0** (2024-01-15): Initial business-friendly format
- Added support for plain-language business rules
- Simplified structure for non-technical updates
- Added comprehensive documentation for product owners