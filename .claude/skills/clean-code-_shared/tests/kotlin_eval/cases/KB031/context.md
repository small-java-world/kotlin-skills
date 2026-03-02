Case_ID: KB031
Category: kotlin
Difficulty: advanced
Source_Refs: kotlinlang/coroutines, google/structured-concurrency

# Scenario
A cache warming service creates its own `CoroutineScope(Dispatchers.IO)` internally and launches background work. The scope is never cancelled, leaks coroutines, and the hardcoded dispatcher makes testing impossible.

# Goal
Detect CC-K001 (internal unmanaged CoroutineScope) and CC-T005 (hardcoded Dispatchers.IO prevents test control).
