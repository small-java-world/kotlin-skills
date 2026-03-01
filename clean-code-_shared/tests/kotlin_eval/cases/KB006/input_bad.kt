package eval.kb006

class RetryPolicyV1 {
    fun shouldRetry(statusCode: Int): Boolean = statusCode >= 500
}

class RetryPolicyV2 {
    fun shouldRetryWithBackoff(statusCode: Int, attempt: Int): Boolean {
        return statusCode >= 500 || (statusCode == 429 && attempt <= 5)
    }
}

class HttpExecutor(
    private val v1: RetryPolicyV1,
    private val v2: RetryPolicyV2
) {
    // Refactor + behavior change mixed in one patch.
    fun execute(statusCode: Int, attempt: Int): Boolean {
        return if (attempt <= 1) {
            v1.shouldRetry(statusCode)
        } else {
            v2.shouldRetryWithBackoff(statusCode, attempt)
        }
    }
}

