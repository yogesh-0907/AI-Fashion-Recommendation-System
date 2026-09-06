# ------------------------------------------------------------
# OFFER & DISCOUNT ENGINE
# ------------------------------------------------------------

OFFERS = {
    "VIP Customer": {
        "discount": 20,
        "minimum_purchase": 1500,
        "offer_type": "Exclusive VIP Offer",
        "message": "Enjoy an exclusive 20% discount on orders above ₹1,500!"
    },

    "Loyal Customer": {
        "discount": 15,
        "minimum_purchase": 1000,
        "offer_type": "Loyalty Reward",
        "message": "Thank you for being loyal! Enjoy 15% off on orders above ₹1,000."
    },

    "Regular Customer": {
        "discount": 10,
        "minimum_purchase": 800,
        "offer_type": "Regular Customer Offer",
        "message": "Enjoy 10% off on orders above ₹800."
    },

    "Occasional Shopper": {
        "discount": 5,
        "minimum_purchase": 500,
        "offer_type": "Daily Offer",
        "message": "Enjoy 5% off on orders above ₹500."
    },

    "At-Risk Customer": {
        "discount": 15,
        "minimum_purchase": 1000,
        "offer_type": "Win-Back Offer",
        "message": "We miss you! Come back and enjoy 15% off on orders above ₹1,000."
    },

    "New Customer": {
        "discount": 10,
        "minimum_purchase": 0,
        "offer_type": "Welcome Offer",
        "message": "Welcome! Enjoy 10% off your first purchase."
    }
}


def get_customer_offer(customer_tag):
    """
    Return the offer assigned to a customer.
    """

    return OFFERS.get(
        customer_tag,
        OFFERS["Regular Customer"]
    )


def calculate_discount(
    price,
    discount_percentage,
    minimum_purchase=0
):
    """
    Calculate discount only when the minimum
    purchase requirement is satisfied.
    """

    if price < minimum_purchase:

        return {
            "Original_Price": round(price, 2),
            "Discount_Percentage": 0,
            "Discount_Amount": 0.0,
            "Final_Price": round(price, 2),
            "Eligible": False
        }

    discount_amount = (
        price * discount_percentage / 100
    )

    final_price = price - discount_amount

    return {
        "Original_Price": round(price, 2),
        "Discount_Percentage": discount_percentage,
        "Discount_Amount": round(discount_amount, 2),
        "Final_Price": round(final_price, 2),
        "Eligible": True
    }