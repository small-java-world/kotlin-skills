package eval.kb024

import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking

class InventoryGateway {
    suspend fun refreshRemote(): Int {
        delay(300)
        return 42
    }
}

class InventoryRefresher(
    private val gateway: InventoryGateway = InventoryGateway()
) {
    fun refreshBlocking(): Int = runBlocking {
        gateway.refreshRemote()
    }
}
