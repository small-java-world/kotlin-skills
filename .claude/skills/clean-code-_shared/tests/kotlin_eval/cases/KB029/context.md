Case_ID: KB029
Category: kotlin
Difficulty: intermediate
Source_Refs: kotlinlang/data-classes, kotlinlang/sealed-classes

# Scenario
A base data class with a mutable var property is inherited by another data class. This breaks the equals/hashCode contract: parent and child instances with the same fields are not equal, and mutable state in a Map key causes silent map corruption.

# Goal
Detect CC-K005 (data class contract violation via var and inheritance) and propose sealed class replacement.
