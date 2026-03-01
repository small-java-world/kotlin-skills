package eval.kb011

import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class EventProcessor {
    private val results = mutableListOf<String>()

    fun processAsync(event: String) {
        GlobalScope.launch {
            delay(100)
            results.add(event.uppercase())
        }
    }

    fun getResults(): List<String> = results.toList()
}

