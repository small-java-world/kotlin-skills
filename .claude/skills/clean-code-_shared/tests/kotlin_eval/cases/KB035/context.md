Case_ID: KB035
Category: kotlin
Difficulty: advanced
Source_Refs: kotlinlang/typecasts, jetbrains/kotlin-null-safety

# Scenario
A JSON response parser uses unsafe `as` casts to convert parsed data, bypassing Kotlin's null safety system. The casts throw ClassCastException at runtime when the actual types don't match expectations.

# Goal
Detect CC-K003 (unsafe `as` cast breaking null safety) and CC-P001 (unsafe type conversion).
