Case_ID: KB038
Category: kotlin
Difficulty: advanced
Source_Refs: kotlinlang/data-classes, kotlinlang/sealed-classes

# Scenario
A data class extends an open class, breaking the equals/hashCode contract. The parent class fields are excluded from the generated equals/hashCode, causing asymmetric equality. A sealed class hierarchy should be used instead.

# Goal
Detect CC-K005 (data class inheritance breaks equals contract) and CC-P001 (sealed class should replace open class hierarchy).
