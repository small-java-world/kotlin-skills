Case_ID: KB025
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/coroutines, google/structured-concurrency

# Scenario
A service class starts a coroutine using GlobalScope in its init block, causing the coroutine to live beyond any lifecycle boundary and making it impossible to cancel or test.

# Goal
Detect CC-K001 (structured concurrency violation) and propose injecting a CoroutineScope tied to the lifecycle.
