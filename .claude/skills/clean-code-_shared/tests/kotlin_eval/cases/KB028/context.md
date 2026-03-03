case_id: KB028
category: kotlin
difficulty: intermediate
source_refs: kotlinlang/scope-functions, jetbrains/kotlin-idioms

# Scenario
A request processing pipeline chains four scope functions (let, run, also, let) in a single expression. The nested receivers make it impossible to determine which object `it` or `this` refers to at any given level.

# Goal
Detect CC-K004 (excessive scope function chaining) and propose splitting into readable intermediate steps.
