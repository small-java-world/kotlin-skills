## Findings

1. Missing severity field
Rule_ID: CC-C001
Evidence: OrderService change updates inventory and billing modules in one patch without impact map.
Minimal_Fix: Split into staged changes and add a seam interface for inventory updates.
Verification: Run billing and inventory integration tests after each stage.

