import pandas as pd


PREFERENCE_COLUMNS = [
    "Category",
    "Subcategory",
    "Fit",
    "Color",
    "Pattern",
    "Material"
]


def get_customer_preferences(
    customer_id,
    purchases_df,
    products_df
):
    """
    Learn a customer's fashion preferences
    from their purchase history.
    """

    customer_purchases = purchases_df[
        purchases_df["Customer_ID"] == customer_id
    ]

    if customer_purchases.empty:
        return None

    history = customer_purchases.merge(
        products_df,
        on="Product_ID",
        how="left"
    )

    preferences = {}

    for column in PREFERENCE_COLUMNS:

        counts = (
            history[column]
            .value_counts()
        )

        preferences[column] = counts.index[0]

    # Preference strength
    preference_strength = {}

    total_purchases = len(history)

    for column in PREFERENCE_COLUMNS:

        top_count = (
            history[column]
            .value_counts()
            .iloc[0]
        )

        preference_strength[column] = round(
            top_count / total_purchases,
            2
        )

    return {
        "preferences": preferences,
        "strength": preference_strength,
        "purchase_count": total_purchases
    }


def get_customer_history(
    customer_id,
    purchases_df,
    products_df
):
    """
    Return complete purchase history
    for a customer.
    """

    customer_purchases = purchases_df[
        purchases_df["Customer_ID"] == customer_id
    ]

    return customer_purchases.merge(
        products_df,
        on="Product_ID",
        how="left"
    )