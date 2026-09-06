import pandas as pd


def get_all_products(products_df):
    """
    Return all clothing products.
    """

    return products_df.copy()


def search_products(products_df, search_text):
    """
    Search clothing products using multiple words.

    Example:
        "white shirt"
        "blue slim fit"
        "black jeans"
        "casual dress"

    Each word is searched across all relevant
    clothing attributes.
    """

    if not search_text:
        return products_df.copy()

    search_text = search_text.lower().strip()

    words = search_text.split()

    searchable_columns = [
        "Product_ID",
        "Product_Name",
        "Category",
        "Subcategory",
        "Fit",
        "Color",
        "Pattern",
        "Material"
    ]

    # Start with every product selected
    mask = pd.Series(
        True,
        index=products_df.index
    )

    # Every word must match somewhere
    for word in words:

        word_mask = pd.Series(
            False,
            index=products_df.index
        )

        for column in searchable_columns:

            word_mask = word_mask | (
                products_df[column]
                .astype(str)
                .str.lower()
                .str.contains(
                    word,
                    na=False,
                    regex=False
                )
            )

        mask = mask & word_mask

    return products_df[mask].copy()


def filter_by_category(products_df, category):
    """
    Filter products by clothing category.
    """

    if not category:
        return products_df.copy()

    return products_df[
        products_df["Category"].str.lower()
        == category.lower()
    ].copy()


def get_product_by_id(products_df, product_id):
    """
    Get one product using Product_ID.
    """

    product = products_df[
        products_df["Product_ID"] == product_id
    ]

    if product.empty:
        return None

    return product.iloc[0]


def get_products_by_ids(products_df, product_ids):
    """
    Get multiple products using Product_ID values.
    """

    if not product_ids:
        return products_df.iloc[0:0].copy()

    return products_df[
        products_df["Product_ID"].isin(product_ids)
    ].copy()