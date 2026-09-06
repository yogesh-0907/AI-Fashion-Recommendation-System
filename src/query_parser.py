import re


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

SUBCATEGORIES = [
    "Casual",
    "Formal",
    "Party",
    "Sports",
    "Ethnic"
]


def parse_user_query(query):
    """
    Extract fashion requirements from natural language.
    """

    text = query.lower()

    result = {
        "Category": None,
        "Subcategory": None,
        "Fit": None,
        "Color": None,
        "Pattern": None,
        "Material": None,
        "Max_Price": None,
        "Min_Price": None
    }

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    category_aliases = {
        "shirt": "Shirt",
        "shirts": "Shirt",
        "tshirt": "T-Shirt",
        "t-shirt": "T-Shirt",
        "t shirts": "T-Shirt",
        "jeans": "Jeans",
        "trouser": "Trousers",
        "trousers": "Trousers",
        "jacket": "Jacket",
        "hoodie": "Hoodie",
        "dress": "Dress",
        "skirt": "Skirt",
        "kurta": "Kurta"
    }

    for word, category in category_aliases.items():

        if word in text:
            result["Category"] = category
            break

    # --------------------------------------------------------
    # FIT
    # --------------------------------------------------------

    fit_aliases = {
        "slim fit": "Slim Fit",
        "slim-fit": "Slim Fit",
        "regular fit": "Regular Fit",
        "regular-fit": "Regular Fit",
        "oversized": "Oversized",
        "relaxed fit": "Relaxed Fit",
        "relaxed-fit": "Relaxed Fit"
    }

    for phrase, fit in fit_aliases.items():

        if phrase in text:
            result["Fit"] = fit
            break

    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    for color in COLORS:

        if color.lower() in text:
            result["Color"] = color
            break

    # --------------------------------------------------------
    # PATTERN
    # --------------------------------------------------------

    for pattern in PATTERNS:

        if pattern.lower() in text:
            result["Pattern"] = pattern
            break

    # --------------------------------------------------------
    # MATERIAL
    # --------------------------------------------------------

    for material in MATERIALS:

        if material.lower() in text:
            result["Material"] = material
            break

    # --------------------------------------------------------
    # SUBCATEGORY
    # --------------------------------------------------------

    for subcategory in SUBCATEGORIES:

        if subcategory.lower() in text:
            result["Subcategory"] = subcategory
            break

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price_match = re.search(
        r"(?:under|below|less than|within|upto|up to)\s*[₹rs.]*\s*(\d+(?:,\d+)*)",
        text
    )

    if price_match:

        result["Max_Price"] = float(
            price_match.group(1).replace(",", "")
        )

    price_range_match = re.search(
        r"(?:between|from)\s*[₹rs.]*\s*(\d+(?:,\d+)*)"
        r"\s*(?:and|to|-)\s*[₹rs.]*\s*(\d+(?:,\d+)*)",
        text
    )

    if price_range_match:

        result["Min_Price"] = float(
            price_range_match.group(1).replace(",", "")
        )

        result["Max_Price"] = float(
            price_range_match.group(2).replace(",", "")
        )

    return result