Case_ID: KB027
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/java-interop, jetbrains/kotlin-null-safety

# Scenario
A Kotlin service wraps a legacy Java DAO whose method returns String without @Nullable annotation. Kotlin imports this as a platform type (String!) and treats it as non-null — but the Java side may return null at runtime. The service uses the return value directly without establishing a null boundary, risking NullPointerException.

# Goal
Detect CC-K003 (null safety boundary leak from Java platform type) and propose explicit nullable typing at the interop boundary.
