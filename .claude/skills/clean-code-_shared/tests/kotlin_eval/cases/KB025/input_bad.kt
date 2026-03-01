package eval.kb025

import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class MetricsSyncService(private val metricsRepo: MetricsRepository) {

    init {
        // BUG: GlobalScope used in init block — coroutine outlives any service lifecycle
        GlobalScope.launch {
            while (true) {
                metricsRepo.flush()
                delay(60_000)
            }
        }
        // No Job reference is kept; callers cannot cancel the coroutine
    }

    fun stop() {
        // No-op: there is nothing to cancel because the scope is not held
    }
}

interface MetricsRepository {
    suspend fun flush()
}
