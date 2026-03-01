package eval.kb007

object RuntimeFlags {
    var strictMode: Boolean = false
}

class InputNormalizer {
    fun normalize(input: String): String {
        return if (RuntimeFlags.strictMode) input.trim().lowercase() else input.trim()
    }
}

class AdminApi {
    fun setStrictMode(enabled: Boolean) {
        RuntimeFlags.strictMode = enabled
    }
}

