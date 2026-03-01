package eval.kb028

data class Request(val payload: String, val userId: String)
data class ValidatedRequest(val payload: String, val userId: String)
data class TransformedPayload(val value: String)

class RequestProcessor(
    private val repo: RequestRepository,
    private val logger: Logger
) {
    fun process(request: Request): String {
        // BUG: 4-level scope function chain — receiver identity is lost at each level
        return request
            .let { it.validate() }
            .run { transform(this) }
            .also { logger.log(it) }
            .let { repo.save(it) }
    }
}

fun Request.validate(): ValidatedRequest = ValidatedRequest(payload.trim(), userId)
fun transform(req: ValidatedRequest): TransformedPayload = TransformedPayload(req.payload.uppercase())

interface RequestRepository {
    fun save(payload: TransformedPayload): String
}

interface Logger {
    fun log(payload: TransformedPayload)
}
