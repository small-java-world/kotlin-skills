Case_ID: KB034
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/properties, jetbrains/kotlin-null-safety

# Scenario
A configuration service uses `lateinit var` for properties that may legitimately not be initialized, treating it as a substitute for nullable types. Access before initialization throws `UninitializedPropertyAccessException` at runtime instead of being handled safely at compile time.

# Goal
Detect CC-K003 (lateinit var misused as null-safety alternative).
