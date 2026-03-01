// KB018: Poor test naming and assertions (CC-T004)
// Tests exist but names are vague and assertions don't express the expected behavior.

data class Email(val to: String, val subject: String, val body: String)

class EmailValidator {
    fun validate(email: Email): List<String> {
        val errors = mutableListOf<String>()
        if (!email.to.contains("@")) errors.add("invalid_recipient")
        if (email.subject.isBlank()) errors.add("empty_subject")
        if (email.body.length > 10_000) errors.add("body_too_long")
        return errors
    }
}

// --- Test file (same compilation unit for evaluation purposes) ---

class EmailValidatorTest {
    private val validator = EmailValidator()

    // Vague name: "test1" says nothing about the expected behavior
    fun test1() {
        val result = validator.validate(Email("user@example.com", "Hello", "World"))
        assert(result.isEmpty())  // What behavior is being verified?
    }

    // Vague name: "testValidation" is too generic
    fun testValidation() {
        val result = validator.validate(Email("bad-email", "", "x".repeat(20_000)))
        assert(result.size == 3)  // Magic number assertion — which 3 errors?
    }

    // Name suggests one thing, assertion checks another
    fun testEmailFormat() {
        val result = validator.validate(Email("no-at-sign", "Subject", "Body"))
        assert(result.isNotEmpty())  // Asserts "not empty" but doesn't verify WHICH error
    }

    // Assertion uses toString comparison — brittle and unexpressive
    fun testErrors() {
        val result = validator.validate(Email("bad", "", "ok"))
        assert(result.toString() == "[invalid_recipient, empty_subject]")
    }
}
