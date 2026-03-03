case_id: KB029
category: kotlin
difficulty: intermediate
source_refs: kotlinlang/data-classes, kotlinlang/sealed-classes

# Scenario
A data class with a mutable `var` property is used as a map key, causing silent map corruption when the field is mutated after insertion. Separately, a data class extends an open class, breaking the equals/hashCode contract because the data class only considers its own properties, not the parent's.

# Goal
Detect CC-K005 (data class contract violations: var in data class + inheritance breaking equals/hashCode) and propose val-only data class + sealed class replacement.
