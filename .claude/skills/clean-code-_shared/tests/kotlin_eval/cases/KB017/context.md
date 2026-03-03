case_id: KB017
category: principles
difficulty: intermediate
source_refs: ktorio/ktor

# KB017 Context

Banking domain service. AccountService manages account balances. Methods combine state mutation with query return values, making it hard to reason about side effects.

## Review Focus
- Identify CQS violations where commands return values.
- Propose separation while keeping the API practical.
