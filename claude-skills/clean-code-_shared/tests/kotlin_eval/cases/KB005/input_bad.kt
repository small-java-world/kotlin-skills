package eval.kb005

class OrderRepo { fun cancel(orderId: String) {} }
class InventoryRepo { fun restock(orderId: String) {} }
class BillingClient { fun refund(orderId: String) {} }
class NotificationClient { fun send(message: String) {} }

class CancelOrderService(
    private val orderRepo: OrderRepo,
    private val inventoryRepo: InventoryRepo,
    private val billingClient: BillingClient,
    private val notificationClient: NotificationClient
) {
    fun cancelOrder(orderId: String) {
        orderRepo.cancel(orderId)
        inventoryRepo.restock(orderId)
        billingClient.refund(orderId)
        notificationClient.send("order canceled: $orderId")
    }
}

