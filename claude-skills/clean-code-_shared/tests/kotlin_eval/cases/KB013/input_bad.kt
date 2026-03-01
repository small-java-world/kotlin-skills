// KB013: Cross-cutting SRP + blast-radius violation (advanced)
// OrderFulfillmentService handles domain logic, external calls, and audit in one class.

data class Order(val id: String, val items: List<String>, val userId: String)
data class PaymentResult(val success: Boolean, val transactionId: String)

object AuditStore {
    val entries = mutableListOf<String>()
    fun append(msg: String) { entries.add(msg) }
}

class PaymentGateway {
    fun charge(userId: String, amount: Int): PaymentResult {
        // Simulated external call
        return PaymentResult(true, "txn-${userId}-${amount}")
    }
}

class InventoryService {
    private val reserved = mutableMapOf<String, Int>()
    fun reserve(itemId: String): Boolean {
        reserved[itemId] = (reserved[itemId] ?: 0) + 1
        return true
    }
    fun release(itemId: String) {
        reserved[itemId] = maxOf(0, (reserved[itemId] ?: 0) - 1)
    }
}

class OrderFulfillmentService(
    private val payment: PaymentGateway,
    private val inventory: InventoryService,
) {
    // Returns a map mixing domain state, HTTP status codes, and audit trails
    fun fulfill(order: Order, pricePerItem: Int): Map<String, Any> {
        val total = order.items.size * pricePerItem

        // Step 1: reserve all items
        val reserved = order.items.map { item ->
            val ok = inventory.reserve(item)
            if (!ok) {
                AuditStore.append("RESERVE_FAIL order=${order.id} item=$item")
                return mapOf("status" to 409, "error" to "inventory_unavailable", "item" to item)
            }
            item
        }

        // Step 2: charge payment
        val result = payment.charge(order.userId, total)
        if (!result.success) {
            // rollback inventory
            reserved.forEach { inventory.release(it) }
            AuditStore.append("PAYMENT_FAIL order=${order.id} user=${order.userId}")
            return mapOf("status" to 402, "error" to "payment_failed")
        }

        // Step 3: write audit inline
        AuditStore.append("FULFILLED order=${order.id} txn=${result.transactionId} total=$total")

        // Step 4: format HTTP-like response inline
        return mapOf(
            "status" to 200,
            "orderId" to order.id,
            "transactionId" to result.transactionId,
            "totalCharged" to total,
            "reservedItems" to reserved,
        )
    }
}
