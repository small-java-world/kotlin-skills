// KB039: False-positive resistance case — correct structured concurrency.
// WorkerManager injects scope, uses supervisorScope, and manages Job lifecycle.

package eval.kb039

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import kotlinx.coroutines.supervisorScope

class WorkerManager(
    private val scope: CoroutineScope,
    private val processor: TaskProcessor
) : AutoCloseable {

    private val activeJobs = mutableListOf<Job>()

    suspend fun runAll(tasks: List<String>) = supervisorScope {
        tasks.forEach { task ->
            val job = launch {
                processor.process(task)
            }
            activeJobs.add(job)
        }
    }

    override fun close() {
        scope.cancel()
        activeJobs.clear()
    }
}

interface TaskProcessor {
    suspend fun process(task: String)
}
