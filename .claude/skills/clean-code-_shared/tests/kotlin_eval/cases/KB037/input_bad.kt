package eval.kb037

// BUG: copy() bypasses the companion factory validation
// A caller can do: validEmail.copy(address = "not-an-email") and get an invalid Email
data class Email(val address: String) {
    companion object {
        fun of(address: String): Email {
            require(address.contains("@")) { "Invalid email: $address" }
            require(address.length <= 254) { "Email too long: ${address.length}" }
            return Email(address)
        }
    }
}

// Same issue: copy() can set negative amount or empty currency
data class Money(val amount: Long, val currency: String) {
    companion object {
        fun of(amount: Long, currency: String): Money {
            require(amount >= 0) { "Amount must be non-negative: $amount" }
            require(currency.length == 3) { "Currency must be ISO 4217: $currency" }
            return Money(amount, currency)
        }
    }
}

class PaymentService(private val ledger: Ledger) {
    fun processRefund(original: Money, refundAmount: Long): Money {
        // BUG: bypasses Money.of() validation — refundAmount could be negative
        val refund = original.copy(amount = refundAmount)
        ledger.record(refund)
        return refund
    }
}

interface Ledger {
    fun record(money: Money)
}
