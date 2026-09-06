import pandas as pd

from preferences import (
    get_customer_preferences,
    get_customer_history
)

from database import (
    get_connection,
    get_user_activity
)

from customer_value import assign_customer_tags
from offers import get_customer_offer

# --------------------------------------------------
# GET REGISTERED USER
# --------------------------------------------------

def get_registered_user(customer_id):

    connection = get_connection()

    user = connection.execute(
        """
        SELECT
            customer_id,
            name,
            email,
            created_at
        FROM users
        WHERE customer_id = ?
        """,
        (customer_id,)
    ).fetchone()

    connection.close()

    return user


# --------------------------------------------------
# GET LIVE PREFERENCES
# --------------------------------------------------

def get_live_preferences(
    customer_id,
    products_df
):

    activities = get_user_activity(
        customer_id
    )

    if not activities:
        return {}, {}

    activity_weights = {
        "VIEW_PRODUCT": 1,
        "WISHLIST": 3,
        "CART": 4,
        "PURCHASE": 6
    }

    preference_counts = {}

    total_weight = 0

    for activity in activities:

        activity_type = activity[1]
        product_id = activity[2]

        if (
            product_id is None
            or activity_type not in activity_weights
        ):
            continue

        product = products_df[
            products_df["Product_ID"] == product_id
        ]

        if product.empty:
            continue

        product = product.iloc[0]

        weight = activity_weights[
            activity_type
        ]

        total_weight += weight

        for column in [
            "Category",
            "Subcategory",
            "Fit",
            "Color",
            "Pattern",
            "Material"
        ]:

            value = product[column]

            if column not in preference_counts:
                preference_counts[column] = {}

            preference_counts[column][value] = (
                preference_counts[column].get(
                    value,
                    0
                ) + weight
            )

    if not preference_counts:
        return {}, {}

    preferences = {}
    strengths = {}

    for column, values in preference_counts.items():

        best_value = max(
            values,
            key=values.get
        )

        preferences[column] = best_value

        column_total = sum(
            values.values()
        )

        if column_total > 0:

            strengths[column] = round(
                values[best_value] / column_total,
                2
            )

        else:

            strengths[column] = 0

    return preferences, strengths


# --------------------------------------------------
# CUSTOMER PROFILE
# --------------------------------------------------

def get_customer_profile(
    customer_id,
    customers_df,
    purchases_df,
    products_df,
    segmented_df=None
):

    # ==================================================
    # HISTORICAL CUSTOMER
    # ==================================================

    customer = customers_df[
        customers_df["Customer_ID"] == customer_id
    ]

    if not customer.empty:

        customer = customer.iloc[0].to_dict()

        segment = "New Customer"

        if segmented_df is not None:

            segmented_customer = segmented_df[
                segmented_df["Customer_ID"] == customer_id
            ]

            if not segmented_customer.empty:

                segment = segmented_customer.iloc[0].get(
                    "Segment",
                    "Unknown"
                )

    # ==================================================
    # NEW REGISTERED CUSTOMER
    # ==================================================

    else:

        registered_user = get_registered_user(
            customer_id
        )

        if registered_user is None:
            return None

        customer = {

            "Customer_ID": registered_user[0],

            "Name": registered_user[1],

            "Email": registered_user[2],

            "Created_At": registered_user[3],

            "Age": 0,

            "Gender": "Unknown",

            "Annual_Income": 0,

            "Customer_Tenure": 0,

            "Purchase_Frequency": 0,

            "Total_Spending": 0,

            "Average_Order_Value": 0,

            "Days_Since_Last_Purchase": 9999,

            "Website_Visits": 0
        }

        segment = "New Customer"


    # ==================================================
    # HISTORICAL PURCHASE PREFERENCES
    # ==================================================

    preference_result = get_customer_preferences(
        customer_id,
        purchases_df,
        products_df
    )

    if preference_result:

        historical_preferences = (
            preference_result["preferences"]
        )

        historical_strengths = (
            preference_result["strength"]
        )

        purchase_count = (
            preference_result["purchase_count"]
        )

    else:

        historical_preferences = {}

        historical_strengths = {}

        purchase_count = 0


    # ==================================================
    # LIVE PREFERENCES
    # ==================================================

    live_preferences, live_strengths = (
        get_live_preferences(
            customer_id,
            products_df
        )
    )


    # ==================================================
    # COMBINE PREFERENCES
    # ==================================================

    if purchase_count > 0:

        # Historical purchases are the stronger signal.

        preferences = historical_preferences.copy()

        preference_strength = (
            historical_strengths.copy()
        )

        # If a live preference exists, use it for
        # attributes where the customer has strong
        # recent activity.

        for column in live_preferences:

            if (
                column not in preferences
                or live_strengths.get(column, 0) >= 0.6
            ):

                preferences[column] = (
                    live_preferences[column]
                )

                preference_strength[column] = (
                    live_strengths.get(column, 0)
                )

    else:

        # Brand-new customer:
        # learn preferences entirely from live activity.

        preferences = live_preferences

        preference_strength = live_strengths


    # ==================================================
    # PURCHASE HISTORY
    # ==================================================

    history = get_customer_history(
        customer_id,
        purchases_df,
        products_df
    )


    # ==================================================
    # LIVE ACTIVITY
    # ==================================================

    activities = get_user_activity(
        customer_id
    )

    live_activity = []

    for activity in activities:

        activity_type = activity[1]

        product_id = activity[2]

        search_query = activity[3]

        activity_date = activity[4]

        live_activity.append({

            "Activity_Type": activity_type,

            "Product_ID": product_id,

            "Search_Query": search_query,

            "Activity_Date": activity_date
        })


    # ==================================================
    # ACTIVITY COUNT
    # ==================================================

    customer["Website_Visits"] = len(
        live_activity
    )

    # ==================================================
    # CUSTOMER VALUE + OFFER
    # ==================================================

    if customer_id in customers_df["Customer_ID"].values:

        tagged_customers = assign_customer_tags(
            customers_df
        )

        tagged_customer = tagged_customers[
            tagged_customers["Customer_ID"] == customer_id
        ]

        if not tagged_customer.empty:

            customer_tag = tagged_customer.iloc[0][
                "Customer_Tag"
            ]

            customer_value_score = tagged_customer.iloc[0][
                "Customer_Value_Score"
            ]

        else:

            customer_tag = "New Customer"
            customer_value_score = 0.0

    else:

        customer_tag = "New Customer"
        customer_value_score = 0.0


    customer_offer = get_customer_offer(
        customer_tag
    )
    
    # ==================================================
    # FINAL PROFILE
    # ==================================================

    return {
        "customer": customer,
        "segment": segment,

        "customer_tag": customer_tag,

        "customer_value_score": customer_value_score,

        "offer": customer_offer,

        "preferences": preferences,

        "preference_strength": preference_strength,

        "purchase_count": purchase_count,

        "purchase_history": history,

        "live_activity": live_activity
    }