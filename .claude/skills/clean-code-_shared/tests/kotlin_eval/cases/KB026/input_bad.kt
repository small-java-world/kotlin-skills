package eval.kb026

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.shareIn
import kotlinx.coroutines.flow.SharingStarted

class OrderEventRepository(private val scope: CoroutineScope) {

    private fun fetchOrderEvents(): Flow<OrderEvent> = flow {
        // Simulates a cold source: re-executed on each collection
        emit(OrderEvent("order-1", "CREATED"))
        emit(OrderEvent("order-2", "SHIPPED"))
    }

    // BUG: replay=0 means late subscribers miss all previously emitted events
    val orderEvents: Flow<OrderEvent> = fetchOrderEvents()
        .shareIn(scope, SharingStarted.Eagerly, replay = 0)
}

data class OrderEvent(val orderId: String, val status: String)
