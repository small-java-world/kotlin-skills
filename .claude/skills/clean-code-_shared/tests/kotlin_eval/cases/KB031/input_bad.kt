package eval.kb031

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class CacheWarmingService(private val cacheLoader: CacheLoader) {

    // BUG: internally created scope with hardcoded Dispatchers.IO and no SupervisorJob
    // Cannot be cancelled from outside, leaks coroutines on service shutdown,
    // and one child failure cancels the entire scope
    private val scope = CoroutineScope(Dispatchers.IO)

    fun startWarming(keys: List<String>) {
        keys.forEach { key ->
            scope.launch {
                cacheLoader.load(key)
            }
        }
    }

    fun startPeriodicRefresh(key: String, intervalMs: Long) {
        scope.launch {
            while (true) {
                cacheLoader.load(key)
                delay(intervalMs)
            }
        }
    }

    // No cancel/close method — the scope lives forever
}

interface CacheLoader {
    suspend fun load(key: String)
}
