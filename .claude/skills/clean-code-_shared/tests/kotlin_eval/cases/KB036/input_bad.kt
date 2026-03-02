package eval.kb036

class HttpRequestBuilder {

    fun buildRequest(
        url: String,
        headers: Map<String, String>,
        body: String?,
        logger: RequestLogger
    ): HttpRequest {
        // BUG: 3-level scope function chain — receiver context shifts at each level
        return HttpRequest(url).apply {
            headers.forEach { (k, v) -> addHeader(k, v) }
            body?.let {
                setBody(it)
                setContentLength(it.length)
            }
        }.also {
            logger.log("Built request to ${it.url}")
            it.headers.forEach { (k, v) ->
                logger.log("  Header: $k=$v")
            }
        }.let {
            if (it.hasBody()) {
                it.apply { addHeader("Content-Type", "application/json") }
            } else {
                it
            }
        }
    }
}

class HttpRequest(val url: String) {
    val headers = mutableMapOf<String, String>()
    private var body: String? = null

    fun addHeader(key: String, value: String) { headers[key] = value }
    fun setBody(content: String) { body = content }
    fun setContentLength(length: Int) { headers["Content-Length"] = length.toString() }
    fun hasBody(): Boolean = body != null
}

interface RequestLogger {
    fun log(message: String)
}
