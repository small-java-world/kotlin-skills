package eval.kb020

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn

data class MarketPrice(val symbol: String, val value: Double)

class PriceApi {
    fun fetch(symbol: String): MarketPrice = MarketPrice(symbol, 100.0)
}

class PriceStreamService(
    private val api: PriceApi = PriceApi()
) {
    fun stream(symbol: String): Flow<MarketPrice> = flow {
        while (true) {
            emit(api.fetch(symbol))
            delay(1000)
        }
    }.flowOn(Dispatchers.IO)
}
