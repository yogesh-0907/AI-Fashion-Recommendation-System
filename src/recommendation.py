import pandas as pd
from database import get_user_activity

def _calculate_preference_score(products, preferences):
    return (
        (products["Category"] == preferences["Category"]).astype(int) * 30
        + (products["Subcategory"] == preferences["Subcategory"]).astype(int) * 15
        + (products["Fit"] == preferences["Fit"]).astype(int) * 25
        + (products["Color"] == preferences["Color"]).astype(int) * 15
        + (products["Pattern"] == preferences["Pattern"]).astype(int) * 7
        + (products["Material"] == preferences["Material"]).astype(int) * 8
    )


def _apply_requirements(products, requirements):
    result = products.copy()

    filters = {
        "Category": "Category",
        "Subcategory": "Subcategory",
        "Fit": "Fit",
        "Color": "Color",
        "Pattern": "Pattern",
        "Material": "Material"
    }

    for requirement, column in filters.items():

        value = requirements.get(requirement)

        if value:
            result = result[
                result[column] == value
            ]

    if requirements.get("Min_Price") is not None:
        result = result[
            result["Price"] >= requirements["Min_Price"]
        ]

    if requirements.get("Max_Price") is not None:
        result = result[
            result["Price"] <= requirements["Max_Price"]
        ]

    return result


def _calculate_popularity(purchases_df):
    popularity = (
        purchases_df
        .groupby("Product_ID")
        .agg(
            Purchase_Count=("Purchase_ID", "count"),
            Quantity_Sold=("Quantity", "sum")
        )
        .reset_index()
    )

    popularity["Popularity_Score"] = (
        popularity["Purchase_Count"] * 0.7
        + popularity["Quantity_Sold"] * 0.3
    )

    return popularity

def _calculate_live_preference_score(
    customer_id,
    products_df
):

    from query_parser import parse_user_query

    activities = get_user_activity(customer_id)

    if not activities:

        return pd.Series(
            0.0,
            index=products_df.index
        )

    # --------------------------------------------------------
    # ACTIVITY WEIGHTS
    # --------------------------------------------------------

    activity_weights = {
        "VIEW_PRODUCT": 1,
        "WISHLIST": 3,
        "CART": 4,
        "PURCHASE": 6,
        "SEARCH": 2
    }

    preference_counts = {}

    # --------------------------------------------------------
    # PROCESS ACTIVITIES
    # --------------------------------------------------------

    for activity in activities:

        activity_type = activity[1]
        product_id = activity[2]
        search_query = activity[3]

        weight = activity_weights.get(
            activity_type,
            0
        )

        if weight == 0:
            continue

        # ----------------------------------------------------
        # PRODUCT-BASED ACTIVITY
        # ----------------------------------------------------

        if (
            product_id is not None
            and activity_type != "SEARCH"
        ):

            product = products_df[
                products_df["Product_ID"] == product_id
            ]

            if product.empty:
                continue

            product = product.iloc[0]

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
                    preference_counts[column].get(value, 0)
                    + weight
                )

        # ----------------------------------------------------
        # SEARCH-BASED ACTIVITY
        # ----------------------------------------------------

        if (
            activity_type == "SEARCH"
            and search_query
        ):

            requirements = parse_user_query(
                search_query
            )

            for column in [
                "Category",
                "Subcategory",
                "Fit",
                "Color",
                "Pattern",
                "Material"
            ]:

                value = requirements.get(column)

                if value is None:
                    continue

                if column not in preference_counts:
                    preference_counts[column] = {}

                preference_counts[column][value] = (
                    preference_counts[column].get(value, 0)
                    + weight
                )

    # --------------------------------------------------------
    # CALCULATE LIVE SCORE
    # --------------------------------------------------------

    live_score = pd.Series(
        0.0,
        index=products_df.index
    )

    column_weights = {
        "Category": 30,
        "Subcategory": 15,
        "Fit": 25,
        "Color": 15,
        "Pattern": 7,
        "Material": 8
    }

    for column, column_weight in column_weights.items():

        if column not in preference_counts:
            continue

        total_weight = sum(
            preference_counts[column].values()
        )

        if total_weight == 0:
            continue

        for value, weight in preference_counts[column].items():

            match = (
                products_df[column] == value
            )

            live_score.loc[match] += (
                weight / total_weight
            ) * column_weight

    return live_score

def recommend_products(
    customer_id,
    purchases_df,
    products_df,
    top_n=10,
    user_requirements=None
):

    from preferences import get_customer_preferences

    # --------------------------------------------------------
    # CUSTOMER HISTORY
    # --------------------------------------------------------

    customer_purchases = purchases_df[
        purchases_df["Customer_ID"] == customer_id
    ]

    live_activities = get_user_activity(
        customer_id
    )

    has_purchase_history = not customer_purchases.empty
    has_live_activity = bool(live_activities)

    has_history = (
        has_purchase_history
        or has_live_activity
    )
    # --------------------------------------------------------
    # POPULARITY
    # --------------------------------------------------------

    popularity = _calculate_popularity(purchases_df)

    products = products_df.merge(
        popularity,
        on="Product_ID",
        how="left"
    )

    products["Purchase_Count"] = (
        products["Purchase_Count"].fillna(0)
    )

    products["Quantity_Sold"] = (
        products["Quantity_Sold"].fillna(0)
    )

    products["Popularity_Score"] = (
        products["Popularity_Score"].fillna(0)
    )

    # Normalize popularity to 0-100
    max_popularity = products["Popularity_Score"].max()

    if max_popularity > 0:

        products["Popularity_Normalized"] = (
            products["Popularity_Score"]
            / max_popularity
        ) * 100

    else:

        products["Popularity_Normalized"] = 0

    # --------------------------------------------------------
    # REMOVE PURCHASED PRODUCTS
    # --------------------------------------------------------

    purchased_products = customer_purchases[
        "Product_ID"
    ].unique()

    products = products[
        ~products["Product_ID"].isin(purchased_products)
    ].copy()

    # --------------------------------------------------------
    # CUSTOMER PREFERENCES
    # --------------------------------------------------------

    preference_result = None

    if has_purchase_history:

        preference_result = get_customer_preferences(
            customer_id,
            purchases_df,
            products_df
        )

        preferences = preference_result["preferences"]

        historical_score = _calculate_preference_score(
            products,
            preferences
        )

    else:

        historical_score = pd.Series(
            0.0,
            index=products.index
        )

    live_score = _calculate_live_preference_score(
        customer_id,
        products_df
    )

    live_score = live_score.reindex(
        products.index,
        fill_value=0
    )

    if has_purchase_history:

        products["Preference_Score"] = (
            historical_score * 0.7
            + live_score * 0.3
        )

    else:

        products["Preference_Score"] = live_score

    # --------------------------------------------------------
    # DETECT LIVE BEHAVIOR
    # --------------------------------------------------------

    has_live_behavior = (
        products["Preference_Score"].max() > 0
    )

    # --------------------------------------------------------
    # DETECT POPULAR / TRENDING REQUEST
    # --------------------------------------------------------

    popular_request = False

    if user_requirements is not None:

        if all(
            value is None
            for value in user_requirements.values()
        ):
            popular_request = True

    # --------------------------------------------------------
    # POPULAR / TRENDING MODE
    # --------------------------------------------------------

    if popular_request:

        products["Final_Score"] = (
            products["Popularity_Score"] * 0.8
            + products["Preference_Score"] * 0.2
        )

        products = products.sort_values(
            "Final_Score",
            ascending=False
        )

        if has_history:

            products["Match_Type"] = (
                "Popular + Personalized"
            )

        elif has_live_behavior:

            products["Match_Type"] = (
                "Popular + Live Personalized"
            )

        else:

            products["Match_Type"] = (
                "Popular Recommendation (Cold Start)"
            )

        return products.head(top_n)

    # --------------------------------------------------------
    # NO USER REQUIREMENTS
    # --------------------------------------------------------

    if not user_requirements:

        products["Final_Score"] = (
            products["Preference_Score"] * 0.8
            + products["Popularity_Normalized"] * 0.2
        )

        products = products.sort_values(
            "Final_Score",
            ascending=False
        )

        if has_history:

            products["Match_Type"] = (
                "Preference Match"
            )

        elif has_live_behavior:

            products["Match_Type"] = (
                "Live Behavioral Match"
            )

        else:

            products["Match_Type"] = (
                "Popular Recommendation (Cold Start)"
            )

        return products.head(top_n)

    # --------------------------------------------------------
    # PURE COLD START + REQUIREMENTS
    # --------------------------------------------------------

    # Only customers with NO history AND NO live behaviour
    # should enter this section.

    if not has_history and not has_live_behavior:

        filtered = _apply_requirements(
            products,
            user_requirements
        )

        if not filtered.empty:

            filtered = filtered.sort_values(
                "Popularity_Score",
                ascending=False
            )

            filtered["Match_Type"] = (
                "Popular Match (Cold Start)"
            )

            return filtered.head(top_n)

        # ----------------------------------------------------
        # RELAX REQUIREMENTS
        # ----------------------------------------------------

        relaxation_order = [
            "Material",
            "Pattern",
            "Color",
            "Subcategory"
        ]

        for requirement_to_relax in relaxation_order:

            relaxed_requirements = (
                user_requirements.copy()
            )

            relaxed_requirements[
                requirement_to_relax
            ] = None

            relaxed = _apply_requirements(
                products,
                relaxed_requirements
            )

            if not relaxed.empty:

                relaxed = relaxed.sort_values(
                    "Popularity_Score",
                    ascending=False
                )

                relaxed["Match_Type"] = (
                    f"Popular Relaxed Match "
                    f"(ignored {requirement_to_relax})"
                )

                return relaxed.head(top_n)

    # --------------------------------------------------------
    # EXACT MATCH
    # --------------------------------------------------------

    exact_matches = _apply_requirements(
        products,
        user_requirements
    )

    if not exact_matches.empty:

        exact_matches["Final_Score"] = (
            exact_matches["Preference_Score"] * 0.8
            + exact_matches["Popularity_Normalized"] * 0.2
        )

        exact_matches = exact_matches.sort_values(
            "Final_Score",
            ascending=False
        )

        if has_history:

            exact_matches["Match_Type"] = (
                "Exact Match"
            )

        elif has_live_behavior:

            exact_matches["Match_Type"] = (
                "Exact Live Behavioral Match"
            )

        else:

            exact_matches["Match_Type"] = (
                "Exact Match"
            )

        return exact_matches.head(top_n)

    # --------------------------------------------------------
    # RELAX REQUIREMENTS
    # --------------------------------------------------------

    relaxation_order = [
        "Material",
        "Pattern",
        "Color",
        "Subcategory"
    ]

    for requirement_to_relax in relaxation_order:

        relaxed_requirements = (
            user_requirements.copy()
        )

        relaxed_requirements[
            requirement_to_relax
        ] = None

        relaxed_matches = _apply_requirements(
            products,
            relaxed_requirements
        )

        if not relaxed_matches.empty:

            relaxed_matches["Final_Score"] = (
                relaxed_matches["Preference_Score"] * 0.8
                + relaxed_matches["Popularity_Normalized"] * 0.2
            )

            relaxed_matches = relaxed_matches.sort_values(
                "Final_Score",
                ascending=False
            )

            if has_live_behavior and not has_history:

                relaxed_matches["Match_Type"] = (
                    f"Live Relaxed Match "
                    f"(ignored {requirement_to_relax})"
                )

            else:

                relaxed_matches["Match_Type"] = (
                    f"Relaxed Match "
                    f"(ignored {requirement_to_relax})"
                )

            return relaxed_matches.head(top_n)

    # --------------------------------------------------------
    # FINAL FALLBACK
    # --------------------------------------------------------

    fallback_requirements = {
        "Category": user_requirements.get("Category"),
        "Subcategory": None,
        "Fit": user_requirements.get("Fit"),
        "Color": None,
        "Pattern": None,
        "Material": None,
        "Min_Price": user_requirements.get("Min_Price"),
        "Max_Price": user_requirements.get("Max_Price")
    }

    fallback = _apply_requirements(
        products,
        fallback_requirements
    )

    if fallback.empty:

        fallback = products.copy()

    fallback["Final_Score"] = (
        fallback["Preference_Score"] * 0.8
        + fallback["Popularity_Normalized"] * 0.2
    )

    fallback = fallback.sort_values(
        "Final_Score",
        ascending=False
    )

    if has_live_behavior and not has_history:

        fallback["Match_Type"] = (
            "Best Live Behavioral Match"
        )

    else:

        fallback["Match_Type"] = (
            "Best Available Match"
        )

    return fallback.head(top_n)