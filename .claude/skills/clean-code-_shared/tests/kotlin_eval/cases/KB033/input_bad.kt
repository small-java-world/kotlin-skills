package eval.kb033

import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.channelFlow
import kotlinx.coroutines.flow.conflate
import kotlinx.coroutines.flow.map

class SensorEventProcessor(
    private val sensorGateway: SensorGateway,
    private val eventStore: EventStore
) {
    // BUG: conflate() silently drops intermediate sensor readings
    // when the collector is slower than the producer.
    // No logging or explicit overflow strategy is present.
    fun processReadings(sensorId: String): Flow<ProcessedReading> =
        channelFlow {
            sensorGateway.streamReadings(sensorId).collect { raw ->
                send(raw)
            }
        }
        .conflate()  // intermediate values silently dropped
        .map { raw ->
            delay(100) // simulate slow processing
            val processed = ProcessedReading(raw.sensorId, raw.value * raw.calibration)
            eventStore.save(processed)
            processed
        }

    fun processAllSensors(sensorIds: List<String>): Flow<ProcessedReading> =
        channelFlow {
            sensorIds.forEach { id ->
                sensorGateway.streamReadings(id).collect { raw ->
                    send(raw)
                }
            }
        }
        .conflate()  // same silent drop issue at scale
        .map { raw ->
            ProcessedReading(raw.sensorId, raw.value * raw.calibration)
        }
}

data class RawReading(val sensorId: String, val value: Double, val calibration: Double)
data class ProcessedReading(val sensorId: String, val calibratedValue: Double)

interface SensorGateway {
    fun streamReadings(sensorId: String): Flow<RawReading>
}

interface EventStore {
    suspend fun save(reading: ProcessedReading)
}
