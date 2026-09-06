import pandas as pd


# ============================================================
# LOAD EXISTING PRODUCTS
# ============================================================

products = pd.read_csv(
    "data/PRODUCTS.csv"
)


# ============================================================
# PRODUCT NAMES
# ============================================================

def create_product_name(row):

    return (
        f"{row['Color']} "
        f"{row['Fit']} "
        f"{row['Category']}"
    )


products["Product_Name"] = products.apply(
    create_product_name,
    axis=1
)


# ============================================================
# RATINGS
# ============================================================

products["Rating"] = (
    3.8
    + (
        products["Product_ID"]
        .str.extract(r"(\d+)")[0]
        .astype(int)
        % 13
    ) / 20
)

products["Rating"] = products["Rating"].clip(
    upper=4.9
).round(1)


# ============================================================
# DESCRIPTIONS
# ============================================================

def create_description(row):

    return (
        f"{row['Subcategory']} {row['Category']} "
        f"with {row['Fit']} design in {row['Color']}. "
        f"{row['Pattern']} pattern made from "
        f"{row['Material']}. Suitable for everyday "
        f"fashion and comfortable styling."
    )


products["Description"] = products.apply(
    create_description,
    axis=1
)


# ============================================================
# IMAGE URL
# ============================================================

def create_image_url(row):

    category = row["Category"].lower()

    image_query = {
        "shirt": "shirt,fashion",
        "t-shirt": "tshirt,fashion",
        "jeans": "jeans,fashion",
        "trousers": "trousers,fashion",
        "jacket": "jacket,fashion",
        "hoodie": "hoodie,fashion",
        "dress": "dress,fashion",
        "skirt": "skirt,fashion",
        "kurta": "kurta,fashion"
    }

    query = image_query.get(
        category,
        "clothing,fashion"
    )

    product_number = int(
        row["Product_ID"].replace("P", "")
    )

    return (
        f"https://loremflickr.com/600/800/"
        f"{query}?lock={product_number}"
    )


products["Image_URL"] = products.apply(
    create_image_url,
    axis=1
)


# ============================================================
# SAVE
# ============================================================

products.to_csv(
    "data/PRODUCTS.csv",
    index=False
)


# ============================================================
# RESULT
# ============================================================

print("Product details added successfully.")
print()
print("Products:", len(products))
print()
print(
    products[
        [
            "Product_ID",
            "Product_Name",
            "Price",
            "Rating",
            "Image_URL"
        ]
    ].head(10).to_string(index=False)
)