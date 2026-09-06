def build_customer_context(profile, recommendations=None):
    """
    Build the complete AI context from:
    - Customer profile
    - Customer value/tag
    - Offer information
    - Learned preferences
    - Purchase history
    - Live customer activity
    - Actual recommendation engine results
    """

    customer = profile["customer"]
    preferences = profile["preferences"]
    strengths = profile["preference_strength"]

    # --------------------------------------------------------
    # SAFE CUSTOMER VALUES
    # --------------------------------------------------------

    age = customer.get("Age")
    gender = customer.get("Gender")
    income = customer.get("Annual_Income")

    age_text = (
        str(int(age))
        if age is not None
        else "Not available"
    )

    gender_text = (
        str(gender)
        if gender is not None
        else "Not available"
    )

    income_text = (
        f"₹{income:,.0f}"
        if income is not None
        else "Not available"
    )

    # --------------------------------------------------------
    # BASIC CUSTOMER CONTEXT
    # --------------------------------------------------------

    context = f"""
CUSTOMER PROFILE

Customer ID: {customer["Customer_ID"]}
Name: {customer.get("Name", "Not available")}
Email: {customer.get("Email", "Not available")}
Age: {age_text}
Gender: {gender_text}
Annual Income: {income_text}

CUSTOMER BEHAVIOR

Purchase Frequency: {customer["Purchase_Frequency"]}
Total Spending: ₹{customer["Total_Spending"]:,.2f}
Average Order Value: ₹{customer["Average_Order_Value"]:,.2f}
Days Since Last Purchase: {customer["Days_Since_Last_Purchase"]}
Website Visits: {customer["Website_Visits"]}

CUSTOMER VALUE

Customer Tag: {profile.get("customer_tag", "Unknown")}
Customer Value Score: {profile.get("customer_value_score", "Unknown")}

CUSTOMER OFFER

Offer: {profile.get("offer", "No offer available")}

CUSTOMER SEGMENT

Segment: {profile["segment"]}

LEARNED FASHION PREFERENCES

Category: {preferences.get("Category", "Unknown")}
Subcategory: {preferences.get("Subcategory", "Unknown")}
Fit: {preferences.get("Fit", "Unknown")}
Color: {preferences.get("Color", "Unknown")}
Pattern: {preferences.get("Pattern", "Unknown")}
Material: {preferences.get("Material", "Unknown")}

PREFERENCE STRENGTH

Category: {strengths.get("Category", 0)}
Subcategory: {strengths.get("Subcategory", 0)}
Fit: {strengths.get("Fit", 0)}
Color: {strengths.get("Color", 0)}
Pattern: {strengths.get("Pattern", 0)}
Material: {strengths.get("Material", 0)}

PURCHASE HISTORY

Total Transactions: {profile["purchase_count"]}
"""

    # --------------------------------------------------------
    # PURCHASE HISTORY
    # --------------------------------------------------------

    history = profile["purchase_history"]

    if not history.empty:

        context += "\nRecent Purchases:\n"

        for _, row in history.tail(10).iterrows():

            context += (
                f"- {row['Product_ID']} | "
                f"{row['Category']} | "
                f"{row['Subcategory']} | "
                f"{row['Fit']} | "
                f"{row['Color']} | "
                f"{row['Pattern']} | "
                f"{row['Material']} | "
                f"₹{row['Price']} | "
                f"Quantity: {row['Quantity']}\n"
            )

    else:

        context += (
            "\nNo historical purchases available. "
            "This is a new customer.\n"
        )

    # --------------------------------------------------------
    # LIVE CUSTOMER ACTIVITY
    # --------------------------------------------------------

    live_activity = profile.get(
        "live_activity",
        []
    )

    context += "\n\nLIVE CUSTOMER ACTIVITY\n"

    if live_activity:

        # Show the most recent 20 activities
        for activity in live_activity[-20:]:

            activity_type = activity.get(
                "Activity_Type",
                "Unknown"
            )

            product_id = activity.get(
                "Product_ID"
            )

            search_query = activity.get(
                "Search_Query"
            )

            activity_date = activity.get(
                "Activity_Date",
                ""
            )

            if product_id:

                context += (
                    f"- {activity_type} | "
                    f"Product ID: {product_id} | "
                    f"Date: {activity_date}\n"
                )

            elif search_query:

                context += (
                    f"- {activity_type} | "
                    f"Search: {search_query} | "
                    f"Date: {activity_date}\n"
                )

            else:

                context += (
                    f"- {activity_type} | "
                    f"Date: {activity_date}\n"
                )

    else:

        context += (
            "- No live activity recorded yet.\n"
        )

    # --------------------------------------------------------
    # ACTUAL RECOMMENDATIONS
    # --------------------------------------------------------

    if recommendations is not None and not recommendations.empty:

        context += (
            "\n\nACTUAL RECOMMENDATIONS "
            "FROM RECOMMENDATION ENGINE:\n"
        )

        for _, row in recommendations.iterrows():

            context += (
                f"- Product ID: {row['Product_ID']} | "
                f"Category: {row['Category']} | "
                f"Subcategory: {row['Subcategory']} | "
                f"Fit: {row['Fit']} | "
                f"Color: {row['Color']} | "
                f"Pattern: {row['Pattern']} | "
                f"Material: {row['Material']} | "
                f"Price: ₹{row['Price']} | "
                f"Match Type: "
                f"{row.get('Match_Type', 'Unknown')}\n"
            )

    else:

        context += (
            "\n\nACTUAL RECOMMENDATIONS "
            "FROM RECOMMENDATION ENGINE:\n"
            "No recommendations available.\n"
        )

    return context