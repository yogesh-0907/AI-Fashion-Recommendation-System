import pandas as pd

customers = pd.read_csv("data/CUSTOMERS.csv")
products = pd.read_csv("data/PRODUCTS.csv")
purchases = pd.read_csv("data/PURCHASES.csv")

purchase_data = purchases.merge(
    products,
    on="Product_ID",
    how="left"
)

# ------------------------------------------------------------
# CHECK MOST PURCHASED CATEGORIES
# ------------------------------------------------------------

print("\n=== MOST PURCHASED CATEGORIES ===")
print(
    purchase_data["Category"]
    .value_counts()
    .head(10)
)

# ------------------------------------------------------------
# CHECK MOST PURCHASED FITS
# ------------------------------------------------------------

print("\n=== MOST PURCHASED FITS ===")
print(
    purchase_data["Fit"]
    .value_counts()
)

# ------------------------------------------------------------
# CHECK MOST PURCHASED COLORS
# ------------------------------------------------------------

print("\n=== MOST PURCHASED COLORS ===")
print(
    purchase_data["Color"]
    .value_counts()
)

# ------------------------------------------------------------
# CHECK MOST PURCHASED PATTERNS
# ------------------------------------------------------------

print("\n=== MOST PURCHASED PATTERNS ===")
print(
    purchase_data["Pattern"]
    .value_counts()
)

# ------------------------------------------------------------
# CHECK ONE CUSTOMER'S PURCHASE HISTORY
# ------------------------------------------------------------

customer_id = "CUST00001"

customer_history = purchase_data[
    purchase_data["Customer_ID"] == customer_id
]

print(f"\n=== PURCHASE HISTORY FOR {customer_id} ===")
print(
    customer_history[
        [
            "Product_ID",
            "Category",
            "Fit",
            "Color",
            "Pattern",
            "Material",
            "Price"
        ]
    ].to_string(index=False)
)