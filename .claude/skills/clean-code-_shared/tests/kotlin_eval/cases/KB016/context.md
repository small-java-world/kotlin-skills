Case_ID: KB016
Category: principles
Difficulty: intermediate
Source_Refs: spring-petclinic/spring-petclinic-kotlin

# KB016 Context

E-commerce backend. CartService calculates totals for the shopping cart preview. InvoiceService generates line items for the final invoice. Both apply the same member-tier discount rules independently.

## Review Focus
- Identify knowledge duplication (not just syntax repetition).
- Propose a single source of truth for the discount policy.
