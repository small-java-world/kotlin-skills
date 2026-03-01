// KB015: False-positive resistance case — clean code, no violations expected.
// PricingCalculator is simple, well-separated, and fully testable.

data class PricingRequest(val basePrice: Int, val discountPercent: Int)
data class PricingResult(val originalPrice: Int, val discountAmount: Int, val finalPrice: Int)

/**
 * Pure domain function: calculates final price from a request.
 * No I/O, no side effects, no global state.
 */
fun calculatePrice(request: PricingRequest): PricingResult {
    require(request.basePrice >= 0) { "basePrice must be non-negative" }
    require(request.discountPercent in 0..100) { "discountPercent must be 0–100" }

    val discountAmount = request.basePrice * request.discountPercent / 100
    val finalPrice = request.basePrice - discountAmount
    return PricingResult(request.basePrice, discountAmount, finalPrice)
}
