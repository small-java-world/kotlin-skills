Case_ID: KB030
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/coroutines, google/structured-concurrency

# Scenario
A batch notification service uses `coroutineScope` to launch multiple child coroutines for sending notifications in parallel. When one child fails, all siblings are cancelled, losing partially-sent notifications. The service should use `supervisorScope` to isolate failures.

# Goal
Detect CC-K001 (structured concurrency violation) where missing `supervisorScope` causes cascading cancellation, and CC-T001 (missing partial-failure test).
