package eval.kb032

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class DashboardViewModel(
    private val statsRepo: StatsRepository,
    private val auditLog: AuditLog,
    scope: CoroutineScope
) {
    private val _state = MutableStateFlow(DashboardState.EMPTY)
    val state: StateFlow<DashboardState> = _state

    init {
        scope.launch {
            statsRepo.observe().collect { stats ->
                _state.value = DashboardState(stats.total, stats.active)
                // BUG: side effect inside collect — re-collect replays
                // the latest value, causing duplicate audit writes
                auditLog.recordView(stats.total)
            }
        }
    }

    fun refresh() {
        // Triggers re-emission, causing another auditLog.recordView
        _state.value = _state.value.copy(refreshCount = _state.value.refreshCount + 1)
    }
}

data class DashboardState(
    val total: Int = 0,
    val active: Int = 0,
    val refreshCount: Int = 0
) {
    companion object {
        val EMPTY = DashboardState()
    }
}

data class Stats(val total: Int, val active: Int)

interface StatsRepository {
    fun observe(): kotlinx.coroutines.flow.Flow<Stats>
}

interface AuditLog {
    suspend fun recordView(total: Int)
}
