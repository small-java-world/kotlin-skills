package eval.kb003

class InvoiceService {
    fun createInvoiceTotal(subtotal: Int, userTier: String, coupon: String): Int {
        var discount = 0
        if (userTier == "gold") discount += subtotal / 10
        if (coupon == "WELCOME10") discount += subtotal / 10
        if (discount > subtotal / 2) discount = subtotal / 2
        return subtotal - discount
    }

    fun previewInvoiceTotal(subtotal: Int, userTier: String, coupon: String): Int {
        var discount = 0
        if (userTier == "gold") discount += subtotal / 10
        if (coupon == "WELCOME10") discount += subtotal / 10
        if (discount > subtotal / 2) discount = subtotal / 2
        return subtotal - discount
    }
}

