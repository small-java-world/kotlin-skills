// KB045: False-positive resistance case — correct data class design.
// Immutable val-only properties, validation in init block, no inheritance.

package eval.kb045

data class EmailAddress private constructor(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email: $value" }
        require(value.length <= 254) { "Email too long: ${value.length}" }
    }

    companion object {
        fun of(value: String): EmailAddress = EmailAddress(value)
    }
}

data class Money(val amount: Long, val currency: String) {
    init {
        require(amount >= 0) { "Amount must be non-negative: $amount" }
        require(currency.length == 3) { "Currency must be ISO 4217: $currency" }
    }
}
