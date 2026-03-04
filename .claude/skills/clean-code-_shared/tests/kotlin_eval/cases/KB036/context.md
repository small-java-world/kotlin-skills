case_id: KB036
category: kotlin
difficulty: intermediate
source_refs: kotlinlang/scope-functions, jetbrains/kotlin-idioms

# Scenario
A request builder chains three scope functions (`apply`, `also`, `let`) in sequence, making the receiver context ambiguous and the code difficult to follow.

# Goal
Detect CC-K004 (excessive scope function chaining) and CC-P001 (ambiguous implicit receiver adds accidental complexity).
