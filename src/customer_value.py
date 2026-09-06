import pandas as pd


def assign_customer_tags(customers_df):
    """
    Assign customer-value tags using:
    - Purchase Frequency
    - Total Spending
    - Recency
    """

    customers = customers_df.copy()

    customers["Customer_Tag"] = "New Customer"
    customers["Customer_Value_Score"] = 0.0

    purchased = customers["Purchase_Frequency"] > 0

    if not purchased.any():
        return customers

    active = customers.loc[purchased].copy()

    # ------------------------------------------------------------
    # Percentile scores
    # ------------------------------------------------------------

    frequency_score = (
        active["Purchase_Frequency"].rank(pct=True) * 100
    )

    spending_score = (
        active["Total_Spending"].rank(pct=True) * 100
    )

    # Lower recency = better
    recency_score = (
        (1 - active["Days_Since_Last_Purchase"].rank(pct=True))
        * 100
    )

    loyalty_score = (
        active["Purchase_Frequency"].rank(pct=True) * 100
    )

    # ------------------------------------------------------------
    # Overall Customer Value Score
    # ------------------------------------------------------------

    value_score = (
        frequency_score * 0.30
        + spending_score * 0.35
        + recency_score * 0.20
        + loyalty_score * 0.15
    )

    customers.loc[
        active.index,
        "Customer_Value_Score"
    ] = value_score.round(2)

    # ------------------------------------------------------------
    # Thresholds
    # ------------------------------------------------------------

    high_frequency = active[
        "Purchase_Frequency"
    ].quantile(0.75)

    high_spending = active[
        "Total_Spending"
    ].quantile(0.75)

    low_frequency = active[
        "Purchase_Frequency"
    ].quantile(0.25)

    at_risk_recency = active[
        "Days_Since_Last_Purchase"
    ].quantile(0.75)

    # ------------------------------------------------------------
    # Assign Tags
    # ------------------------------------------------------------

    for index in active.index:

        frequency = customers.loc[
            index,
            "Purchase_Frequency"
        ]

        spending = customers.loc[
            index,
            "Total_Spending"
        ]

        recency = customers.loc[
            index,
            "Days_Since_Last_Purchase"
        ]

        score = customers.loc[
            index,
            "Customer_Value_Score"
        ]

        # --------------------------------------------------------
        # At-Risk Customer
        # --------------------------------------------------------

        if recency >= at_risk_recency:

            tag = "At-Risk Customer"

        # --------------------------------------------------------
        # VIP Customer
        # --------------------------------------------------------

        elif (
            score >= 80
            and frequency >= high_frequency
            and spending >= high_spending
        ):

            tag = "VIP Customer"

        # --------------------------------------------------------
        # Loyal Customer
        # --------------------------------------------------------

        elif (
            score >= 65
            and frequency >= 5
        ):

            tag = "Loyal Customer"

        # --------------------------------------------------------
        # Occasional Shopper
        # --------------------------------------------------------

        elif frequency <= low_frequency:

            tag = "Occasional Shopper"

        # --------------------------------------------------------
        # Regular Customer
        # --------------------------------------------------------

        else:

            tag = "Regular Customer"

        customers.loc[
            index,
            "Customer_Tag"
        ] = tag

    return customers


def get_customer_tag(customer_id, tagged_customers_df):
    """
    Get the tag assigned to one customer.
    """

    customer = tagged_customers_df[
        tagged_customers_df["Customer_ID"] == customer_id
    ]

    if customer.empty:
        return None

    return customer.iloc[0]["Customer_Tag"]