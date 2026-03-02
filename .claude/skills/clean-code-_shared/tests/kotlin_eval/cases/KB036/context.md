Case_ID: KB036
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/scope-functions, jetbrains/kotlin-idioms

# Scenario
A request builder chains three scope functions (`apply`, `also`, `let`) in sequence, making the receiver context ambiguous and the code difficult to follow.

# Goal
Detect CC-K004 (excessive scope function chaining) and CC-P006 (ambiguous `it` receiver).
