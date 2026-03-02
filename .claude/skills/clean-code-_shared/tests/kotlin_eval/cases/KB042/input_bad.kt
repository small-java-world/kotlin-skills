// KB042: False-positive resistance case — correct Flow/Channel usage.
// EventBus uses SharedFlow with replay=1 and explicit overflow strategy.

package eval.kb042

import kotlinx.coroutines.channels.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow

class EventBus<T> {
    private val _events = MutableSharedFlow<T>(
        replay = 1,
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<T> = _events.asSharedFlow()

    suspend fun emit(event: T) {
        _events.emit(event)
    }
}
