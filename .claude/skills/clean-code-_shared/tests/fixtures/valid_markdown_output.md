## Findings

1. SRP violation in OrderService
Severity: high
Rule_ID: CC-P004
File: src/OrderService.kt
Line_Range: 10-45
Evidence: `OrderService.process` handles validation, persistence, and notification in a single method.
Minimal_Fix: Extract `OrderValidator`, `OrderRepository`, and `NotificationSender` as separate classes.
Verification: Add unit tests for each extracted class and verify `OrderService` delegates correctly.

2. Missing regression test
Severity: medium
Rule_ID: CC-T001
Evidence: No tests cover the failure path when `OrderRepository.save()` throws.
Minimal_Fix: Add a test that stubs `OrderRepository.save()` to throw and asserts the error is propagated.
Verification: Run the new test and assert `OrderService.process()` surfaces the repository exception.
