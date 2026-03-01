// KB016: DRY violation — duplicated discount calculation logic (CC-P003)
// Two services independently implement the same discount rule.

data class Product(val id: String, val price: Double, val category: String)

class CartService {
    fun calculateTotal(products: List<Product>, memberTier: String): Double {
        var total = 0.0
        for (p in products) {
            var discount = 0.0
            // Discount rule duplicated here and in InvoiceService
            if (memberTier == "gold") {
                discount = if (p.category == "electronics") 0.15 else 0.10
            } else if (memberTier == "silver") {
                discount = if (p.category == "electronics") 0.10 else 0.05
            }
            total += p.price * (1 - discount)
        }
        return total
    }
}

class InvoiceService {
    fun generateLineItems(products: List<Product>, memberTier: String): List<Pair<String, Double>> {
        return products.map { p ->
            var discount = 0.0
            // Same discount rule as CartService — if one changes, the other drifts
            if (memberTier == "gold") {
                discount = if (p.category == "electronics") 0.15 else 0.10
            } else if (memberTier == "silver") {
                discount = if (p.category == "electronics") 0.10 else 0.05
            }
            p.id to p.price * (1 - discount)
        }
    }
}
