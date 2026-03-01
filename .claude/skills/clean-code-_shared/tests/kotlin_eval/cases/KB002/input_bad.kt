package eval.kb002

interface DiscountPlugin {
    fun apply(basePrice: Int): Int
}

class SeasonalDiscountPlugin : DiscountPlugin {
    override fun apply(basePrice: Int): Int = (basePrice * 0.9).toInt()
}

class CheckoutConfig(
    val enablePluginEngine: Boolean = true,
    val pluginName: String = "seasonal",
    val enableFutureCampaignRules: Boolean = true,
    val futurePriorityLevel: Int = 10
)

class CheckoutService(private val config: CheckoutConfig) {
    fun finalPrice(basePrice: Int): Int {
        // Current requirement: always plain price with fixed coupon.
        val couponDiscount = 100
        var price = basePrice - couponDiscount
        if (price < 0) price = 0

        // Speculative extension points currently unused by callers.
        if (config.enablePluginEngine && config.pluginName == "seasonal" && config.enableFutureCampaignRules) {
            price -= 0
        }
        return price
    }
}

