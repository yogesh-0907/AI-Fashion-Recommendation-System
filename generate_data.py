import pandas as pd
import numpy as np

np.random.seed(42)

REFERENCE_DATE = pd.Timestamp("2026-09-01")

NUM_CUSTOMERS = 10_000
NUM_PRODUCTS = 750
NUM_PURCHASES = 100_000

CATEGORIES = [
    "Shirt",
    "T-Shirt",
    "Jeans",
    "Trousers",
    "Jacket",
    "Hoodie",
    "Dress",
    "Skirt",
    "Kurta"
]

SUBCATEGORIES = [
    "Casual",
    "Formal",
    "Party",
    "Sports",
    "Ethnic"
]

FITS = [
    "Slim Fit",
    "Regular Fit",
    "Oversized",
    "Relaxed Fit"
]

COLORS = [
    "Black",
    "White",
    "Blue",
    "Navy",
    "Red",
    "Green",
    "Grey",
    "Brown",
    "Beige",
    "Pink",
    "Yellow"
]

PATTERNS = [
    "Plain",
    "Solid",
    "Checked",
    "Striped",
    "Printed",
    "Floral"
]

MATERIALS = [
    "Cotton",
    "Linen",
    "Denim",
    "Polyester",
    "Wool",
    "Rayon",
    "Silk",
    "Blended"
]

PRICE_RANGES = {
    "Shirt": (500, 2000),
    "T-Shirt": (300, 1500),
    "Jeans": (900, 3000),
    "Trousers": (700, 2500),
    "Jacket": (1200, 5000),
    "Hoodie": (800, 2500),
    "Dress": (900, 4000),
    "Skirt": (600, 2500),
    "Kurta": (700, 3000)
}

MATERIAL_PRICE_MULTIPLIER = {
    "Cotton": 1.00,
    "Linen": 1.15,
    "Denim": 1.20,
    "Polyester": 0.90,
    "Wool": 1.35,
    "Rayon": 1.05,
    "Silk": 1.60,
    "Blended": 0.95
}

def generate_products():
    products = []

    for i in range(NUM_PRODUCTS):
        category = np.random.choice(CATEGORIES)
        color = np.random.choice(COLORS)
        if category in ["Shirt", "T-Shirt", "Jeans", "Trousers"]:
            subcategory = np.random.choice(["Casual", "Formal", "Sports"])
        elif category in ["Jacket", "Hoodie"]:
            subcategory = np.random.choice(["Casual", "Sports"])
        elif category in ["Dress", "Skirt"]:
            subcategory = np.random.choice(["Casual", "Party"])
        else:  # Kurta
            subcategory = np.random.choice(["Casual", "Ethnic", "Party"])

        if category in ["Shirt", "Trousers", "Jeans"]:
            fit = np.random.choice(["Slim Fit", "Regular Fit", "Relaxed Fit"])
        elif category in ["T-Shirt", "Hoodie"]:
            fit = np.random.choice(["Regular Fit", "Oversized", "Relaxed Fit"])
        elif category in ["Dress", "Skirt"]:
            fit = np.random.choice(["Regular Fit", "Relaxed Fit"])
        else:
            fit = np.random.choice(FITS)

        pattern = np.random.choice(PATTERNS)
        if category in ["Jeans"]:
            material = np.random.choice(["Denim", "Blended"])
        elif category in ["Jacket", "Hoodie"]:
            material = np.random.choice(["Cotton", "Polyester", "Wool", "Blended"])
        elif category in ["Shirt", "T-Shirt"]:
            material = np.random.choice(["Cotton", "Linen", "Polyester", "Rayon", "Blended"])
        elif category in ["Dress", "Skirt"]:
            material = np.random.choice(["Cotton", "Linen", "Rayon", "Silk", "Polyester", "Blended"])
        elif category in ["Trousers"]:
            material = np.random.choice(["Cotton", "Linen", "Polyester", "Wool", "Blended"])
        else:  # Kurta
            material = np.random.choice(["Cotton", "Linen", "Rayon", "Silk", "Blended"])

        min_price, max_price = PRICE_RANGES[category]
        base_price = np.random.uniform(min_price, max_price)

        price = base_price * MATERIAL_PRICE_MULTIPLIER[material]
        price = round(price / 10) * 10

        products.append({
            "Product_ID": f"P{i + 1:05d}",
            "Category": category,
            "Subcategory": subcategory,
            "Fit": fit,
            "Color": color,
            "Pattern": pattern,
            "Material": material,
            "Price": price
        })

    return pd.DataFrame(products)

products_df = generate_products()
products_df.to_csv("data/PRODUCTS.csv", index=False)
print(f"Generated {len(products_df)} products.")
print(products_df.head())

# ============================================================
# CUSTOMER GENERATION
# ============================================================

customer_ids = [f"CUST{i + 1:05d}" for i in range(NUM_CUSTOMERS)]

ages = np.random.randint(18, 71, NUM_CUSTOMERS)

genders = np.random.choice(
    ["Male", "Female", "Other"],
    size=NUM_CUSTOMERS,
    p=[0.48, 0.48, 0.04]
)

annual_incomes = np.random.lognormal(
    mean=np.log(500000),
    sigma=0.45,
    size=NUM_CUSTOMERS
)

annual_incomes = np.clip(
    annual_incomes,
    180000,
    2500000
).round(2)

customer_tenures = np.random.randint(
    1,
    121,
    NUM_CUSTOMERS
)

website_visits = np.random.poisson(
    lam=25,
    size=NUM_CUSTOMERS
)

website_visits = np.clip(
    website_visits,
    0,
    200
)

customers_df = pd.DataFrame({
    "Customer_ID": customer_ids,
    "Age": ages,
    "Gender": genders,
    "Annual_Income": annual_incomes,
    "Customer_Tenure": customer_tenures,
    "Website_Visits": website_visits
})

print(f"Generated {len(customers_df)} customers.")
print(customers_df.head())

# ============================================================
# CUSTOMER BEHAVIOR TENDENCIES
# ============================================================

behavior_profiles = np.random.choice(
    [
        "High_Value",
        "Frequent",
        "Occasional",
        "Low_Engagement",
        "At_Risk"
    ],
    size=NUM_CUSTOMERS,
    p=[0.15, 0.20, 0.30, 0.20, 0.15]
)

profile_settings = {
    "High_Value": {
        "purchase_mean": 18,
        "spending_multiplier": 1.8,
        "activity_multiplier": 1.4
    },
    "Frequent": {
        "purchase_mean": 14,
        "spending_multiplier": 1.2,
        "activity_multiplier": 1.3
    },
    "Occasional": {
        "purchase_mean": 6,
        "spending_multiplier": 1.0,
        "activity_multiplier": 0.9
    },
    "Low_Engagement": {
        "purchase_mean": 2,
        "spending_multiplier": 0.7,
        "activity_multiplier": 0.6
    },
    "At_Risk": {
        "purchase_mean": 8,
        "spending_multiplier": 1.1,
        "activity_multiplier": 0.8
    }
}

purchase_means = np.array([
    profile_settings[profile]["purchase_mean"]
    for profile in behavior_profiles
])

spending_multipliers = np.array([
    profile_settings[profile]["spending_multiplier"]
    for profile in behavior_profiles
])

activity_multipliers = np.array([
    profile_settings[profile]["activity_multiplier"]
    for profile in behavior_profiles
])

customers_df["Purchase_Tendency"] = purchase_means
customers_df["Spending_Tendency"] = spending_multipliers
customers_df["Activity_Tendency"] = activity_multipliers

print("\nCustomer behavior profiles:")
print(pd.Series(behavior_profiles).value_counts())

# ============================================================
# PURCHASE FREQUENCY
# ============================================================

purchase_counts = np.random.poisson(
    lam=customers_df["Purchase_Tendency"].values
)

purchase_counts = np.maximum(purchase_counts, 0)

# Keep the total number of transactions manageable
purchase_counts = np.minimum(purchase_counts, 40)

customers_df["Purchase_Count"] = purchase_counts

print("\nPurchase count statistics:")
print(customers_df["Purchase_Count"].describe())

# ============================================================
# CUSTOMER FASHION PREFERENCES
# ============================================================

customer_preferences = []

for _, customer in customers_df.iterrows():

    # Preferred category
    preferred_category = np.random.choice(
        CATEGORIES,
        p=[0.18, 0.18, 0.12, 0.10, 0.08, 0.08, 0.10, 0.06, 0.10]
    )

    # Preferred fit based on category
    if preferred_category in ["Shirt", "Jeans", "Trousers"]:
        preferred_fit = np.random.choice(
            ["Slim Fit", "Regular Fit", "Relaxed Fit"],
            p=[0.50, 0.30, 0.20]
        )
    elif preferred_category in ["T-Shirt", "Hoodie"]:
        preferred_fit = np.random.choice(
            ["Regular Fit", "Oversized", "Relaxed Fit"],
            p=[0.30, 0.45, 0.25]
        )
    else:
        preferred_fit = np.random.choice(
            ["Regular Fit", "Relaxed Fit"],
            p=[0.60, 0.40]
        )

    preferred_color = np.random.choice(
        COLORS,
        p=[
            0.14, 0.12, 0.13, 0.10, 0.07, 0.06,
            0.10, 0.07, 0.07, 0.08, 0.06
        ]
    )

    preferred_pattern = np.random.choice(
        PATTERNS,
        p=[0.30, 0.20, 0.15, 0.12, 0.15, 0.08]
    )

    preferred_material = np.random.choice(
        MATERIALS,
        p=[0.25, 0.10, 0.12, 0.15, 0.07, 0.10, 0.06, 0.15]
    )

    # Preferred spending level influenced by income
    income = customer["Annual_Income"]

    if income < 350000:
        preferred_price = np.random.uniform(500, 1200)
    elif income < 700000:
        preferred_price = np.random.uniform(700, 1800)
    else:
        preferred_price = np.random.uniform(1000, 3000)

    customer_preferences.append({
        "Customer_ID": customer["Customer_ID"],
        "Preferred_Category": preferred_category,
        "Preferred_Fit": preferred_fit,
        "Preferred_Color": preferred_color,
        "Preferred_Pattern": preferred_pattern,
        "Preferred_Material": preferred_material,
        "Preferred_Price": preferred_price
    })

preferences_df = pd.DataFrame(customer_preferences)


# ============================================================
# PURCHASE TRANSACTION GENERATION - OPTIMIZED
# ============================================================

purchase_rows = []

# Convert product attributes to arrays for fast processing
product_categories = products_df["Category"].values
product_fits = products_df["Fit"].values
product_colors = products_df["Color"].values
product_patterns = products_df["Pattern"].values
product_materials = products_df["Material"].values
product_ids = products_df["Product_ID"].values

product_indices = np.arange(len(products_df))

# Pre-build category + fit lookup
category_fit_lookup = {}

for category in CATEGORIES:
    for fit in FITS:

        indices = product_indices[
            (product_categories == category) &
            (product_fits == fit)
        ]

        if len(indices) > 0:
            category_fit_lookup[(category, fit)] = indices


# Fast customer preference lookup
preference_lookup = (
    preferences_df
    .set_index("Customer_ID")
    .to_dict("index")
)


# ------------------------------------------------------------
# GENERATE PURCHASES
# ------------------------------------------------------------

for _, customer in customers_df.iterrows():

    customer_id = customer["Customer_ID"]
    purchase_count = int(customer["Purchase_Count"])

    if purchase_count == 0:
        continue

    preference = preference_lookup[customer_id]

    preferred_category = preference["Preferred_Category"]
    preferred_fit = preference["Preferred_Fit"]
    preferred_color = preference["Preferred_Color"]
    preferred_pattern = preference["Preferred_Pattern"]
    preferred_material = preference["Preferred_Material"]

    # Find products matching preferred category + fit
    candidates = category_fit_lookup.get(
        (preferred_category, preferred_fit)
    )

    # Fallback to category only
    if candidates is None or len(candidates) == 0:

        candidates = product_indices[
            product_categories == preferred_category
        ]

    # Calculate preference scores ONCE per customer
    candidate_scores = (
        (product_colors[candidates] == preferred_color).astype(int) * 3
        + (product_patterns[candidates] == preferred_pattern).astype(int) * 2
        + (product_materials[candidates] == preferred_material).astype(int) * 2
    )

    weights = np.exp(candidate_scores)
    probabilities = weights / weights.sum()

    # Generate all purchase choices for this customer
    for _ in range(purchase_count):

        # 80% preference-based purchase
        if np.random.random() < 0.80:

            selected_index = np.random.choice(
                candidates,
                p=probabilities
            )

        # 20% exploration
        else:

            selected_index = np.random.choice(
                product_indices
            )

        # Purchase date
        max_days = min(
            int(customer["Customer_Tenure"]) * 30,
            730
        )

        max_days = max(max_days, 30)

        purchase_date = (
            REFERENCE_DATE
            - pd.Timedelta(
                days=np.random.randint(0, max_days + 1)
            )
        )

        # Quantity
        quantity = np.random.choice(
            [1, 2, 3],
            p=[0.80, 0.17, 0.03]
        )

        purchase_rows.append({
            "Purchase_ID": f"PUR{len(purchase_rows) + 1:05d}",
            "Customer_ID": customer_id,
            "Product_ID": product_ids[selected_index],
            "Purchase_Date": purchase_date,
            "Quantity": int(quantity)
        })


purchases_df = pd.DataFrame(purchase_rows)


# ------------------------------------------------------------
# SAVE PURCHASES
# ------------------------------------------------------------

purchases_df.to_csv(
    "data/PURCHASES.csv",
    index=False
)

print(f"\nGenerated {len(purchases_df)} purchase transactions.")
print("PURCHASES.csv saved successfully.")
print(purchases_df.head())

# ============================================================
# CALCULATE CUSTOMER PURCHASE STATISTICS
# ============================================================

purchase_summary = (
    purchases_df
    .groupby("Customer_ID")
    .agg(
        Purchase_Frequency=("Purchase_ID", "count"),
        Total_Spending=("Product_ID", lambda x: 0)
    )
    .reset_index()
)

# Calculate actual spending using product prices
purchases_with_price = purchases_df.merge(
    products_df[["Product_ID", "Price"]],
    on="Product_ID",
    how="left"
)

purchases_with_price["Purchase_Amount"] = (
    purchases_with_price["Price"] *
    purchases_with_price["Quantity"]
)

spending_summary = (
    purchases_with_price
    .groupby("Customer_ID")["Purchase_Amount"]
    .sum()
    .reset_index(name="Total_Spending")
)

last_purchase_summary = (
    purchases_df
    .groupby("Customer_ID")["Purchase_Date"]
    .max()
    .reset_index(name="Last_Purchase_Date")
)

purchase_summary = (
    purchases_df
    .groupby("Customer_ID")
    .size()
    .reset_index(name="Purchase_Frequency")
)

purchase_summary = purchase_summary.merge(
    spending_summary,
    on="Customer_ID",
    how="left"
)

purchase_summary = purchase_summary.merge(
    last_purchase_summary,
    on="Customer_ID",
    how="left"
)

purchase_summary["Average_Order_Value"] = (
    purchase_summary["Total_Spending"] /
    purchase_summary["Purchase_Frequency"]
)

purchase_summary["Days_Since_Last_Purchase"] = (
    REFERENCE_DATE -
    pd.to_datetime(purchase_summary["Last_Purchase_Date"])
).dt.days

print("\nPurchase statistics calculated successfully.")
print(purchase_summary.head())

# ============================================================
# BUILD FINAL CUSTOMERS DATASET
# ============================================================

customers_df = customers_df.merge(
    purchase_summary[
        [
            "Customer_ID",
            "Purchase_Frequency",
            "Total_Spending",
            "Average_Order_Value",
            "Days_Since_Last_Purchase"
        ]
    ],
    on="Customer_ID",
    how="left"
)

# Customers with no purchases
customers_df["Purchase_Frequency"] = (
    customers_df["Purchase_Frequency"]
    .fillna(0)
    .astype(int)
)

customers_df["Total_Spending"] = (
    customers_df["Total_Spending"]
    .fillna(0)
    .round(2)
)

customers_df["Average_Order_Value"] = (
    customers_df["Average_Order_Value"]
    .fillna(0)
    .round(2)
)

# Use a large value to indicate that the customer has never purchased
customers_df["Days_Since_Last_Purchase"] = (
    customers_df["Days_Since_Last_Purchase"]
    .fillna(9999)
    .astype(int)
)

# Remove temporary generation columns
customers_df = customers_df.drop(
    columns=[
        "Purchase_Tendency",
        "Spending_Tendency",
        "Activity_Tendency",
        "Purchase_Count"
    ]
)

# Arrange columns according to data_dictionary.md
customers_df = customers_df[
    [
        "Customer_ID",
        "Age",
        "Gender",
        "Annual_Income",
        "Customer_Tenure",
        "Purchase_Frequency",
        "Total_Spending",
        "Average_Order_Value",
        "Days_Since_Last_Purchase",
        "Website_Visits"
    ]
]

customers_df.to_csv(
    "data/CUSTOMERS.csv",
    index=False
)

print(f"\nGenerated {len(customers_df)} customers.")
print("CUSTOMERS.csv saved successfully.")
print(customers_df.head())