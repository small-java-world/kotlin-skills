Case_ID: KB027
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/java-interop, jetbrains/kotlin-null-safety

# Scenario
A Kotlin service calls a Java library that returns a @Nullable String. The platform type is accepted without null annotation and immediately accessed without a null check, risking a NullPointerException at runtime.

# Goal
Detect CC-K003 (null safety boundary leak from Java platform type) and propose explicit nullable handling.
