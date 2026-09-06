import os
import shutil
import csv
import pandas as pd


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

PRODUCTS_FILE = "data/PRODUCTS.csv"
DATASET_FILE = "data/fashion_dataset/styles.csv"
DATASET_IMAGES = "data/fashion_dataset/images"
OUTPUT_FOLDER = "data/product_images"


# --------------------------------------------------
# CREATE OUTPUT FOLDER
# --------------------------------------------------

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --------------------------------------------------
# LOAD OUR PRODUCTS
# --------------------------------------------------

products = pd.read_csv(PRODUCTS_FILE)

print(f"Our products: {len(products)}")


# --------------------------------------------------
# LOAD DATASET SAFELY
# --------------------------------------------------

print("Reading fashion dataset...")

dataset_rows = []

with open(
    DATASET_FILE,
    "r",
    encoding="utf-8",
    errors="replace",
    newline=""
) as file:

    reader = csv.reader(file)

    header = next(reader)

    print(f"Dataset columns: {header}")

    for row in reader:

        # We only need:
        # id          -> position 0
        # articleType -> position 4
        # baseColour  -> position 5

        if len(row) < 6:
            continue

        dataset_rows.append({
            "id": row[0],
            "articleType": row[4],
            "baseColour": row[5]
        })


dataset = pd.DataFrame(dataset_rows)

print(f"Dataset products loaded: {len(dataset)}")
print()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize(text):

    return (
        str(text)
        .lower()
        .strip()
        .replace("-", "")
        .replace("_", "")
        .replace(" ", "")
    )


def category_match(
    our_category,
    dataset_type
):

    our_category = normalize(our_category)
    dataset_type = normalize(dataset_type)

    mappings = {

        "shirt": [
            "shirt",
            "shirts",
            "formalshirt",
            "casualshirt"
        ],

        "tshirt": [
            "tshirt",
            "tshirts"
        ],

        "jeans": [
            "jeans"
        ],

        "trousers": [
            "trousers",
            "trouser"
        ],

        "jacket": [
            "jacket",
            "jackets"
        ],

        "hoodie": [
            "sweater",
            "sweaters",
            "hoodie",
            "sweatshirt"
        ],

        "dress": [
            "dress",
            "dresses"
        ],

        "skirt": [
            "skirt",
            "skirts"
        ],

        "kurta": [
            "kurta",
            "kurtas"
        ]
    }

    allowed_types = mappings.get(
        our_category,
        []
    )

    return dataset_type in allowed_types


def color_match(
    our_color,
    dataset_color
):

    our_color = normalize(our_color)
    dataset_color = normalize(dataset_color)

    if our_color == dataset_color:
        return True

    color_aliases = {

        "navy": [
            "navy",
            "blue"
        ],

        "blue": [
            "blue",
            "navy"
        ],

        "grey": [
            "grey",
            "gray"
        ],

        "gray": [
            "grey",
            "gray"
        ],

        "beige": [
            "beige",
            "cream"
        ],

        "brown": [
            "brown"
        ],

        "pink": [
            "pink"
        ],

        "red": [
            "red"
        ],

        "green": [
            "green"
        ],

        "yellow": [
            "yellow"
        ],

        "black": [
            "black"
        ],

        "white": [
            "white"
        ]
    }

    allowed = color_aliases.get(
        our_color,
        [our_color]
    )

    return dataset_color in allowed


# --------------------------------------------------
# CHECK REQUIRED DATASET COLUMNS
# --------------------------------------------------

required_columns = [
    "id",
    "articleType",
    "baseColour"
]

for column in required_columns:

    if column not in dataset.columns:

        raise ValueError(
            f"Required column '{column}' "
            f"was not found in styles.csv"
        )


# --------------------------------------------------
# FIND AVAILABLE IMAGES
# --------------------------------------------------

available_images = set(
    os.path.splitext(filename)[0]
    for filename in os.listdir(DATASET_IMAGES)
    if filename.lower().endswith(".jpg")
)

print(
    f"Available images: "
    f"{len(available_images)}"
)

print()


# --------------------------------------------------
# MATCH PRODUCTS WITH REAL IMAGES
# --------------------------------------------------

used_images = set()

matched = 0
category_only_matches = 0
fallback_matches = 0


for index, product in products.iterrows():

    product_id = product["Product_ID"]

    our_category = product["Category"]
    our_color = product["Color"]


    # --------------------------------------------------
    # 1. CATEGORY + COLOR MATCH
    # --------------------------------------------------

    candidates = dataset[
        dataset["articleType"].apply(
            lambda value:
            category_match(
                our_category,
                value
            )
        )
        &
        dataset["baseColour"].apply(
            lambda value:
            color_match(
                our_color,
                value
            )
        )
    ]


    candidates = candidates[
        candidates["id"]
        .astype(str)
        .isin(available_images)
    ]


    candidates = candidates[
        ~candidates["id"]
        .astype(str)
        .isin(used_images)
    ]


    # --------------------------------------------------
    # 2. CATEGORY ONLY
    # --------------------------------------------------

    if candidates.empty:

        candidates = dataset[
            dataset["articleType"].apply(
                lambda value:
                category_match(
                    our_category,
                    value
                )
            )
        ]


        candidates = candidates[
            candidates["id"]
            .astype(str)
            .isin(available_images)
        ]


        candidates = candidates[
            ~candidates["id"]
            .astype(str)
            .isin(used_images)
        ]


        if not candidates.empty:

            category_only_matches += 1


    # --------------------------------------------------
    # 3. FALLBACK IMAGE
    # --------------------------------------------------

    if candidates.empty:

        candidates = dataset[
            dataset["id"]
            .astype(str)
            .isin(available_images)
        ]


        candidates = candidates[
            ~candidates["id"]
            .astype(str)
            .isin(used_images)
        ]


        if not candidates.empty:

            fallback_matches += 1


    # --------------------------------------------------
    # NO IMAGE
    # --------------------------------------------------

    if candidates.empty:

        print(
            f"WARNING: "
            f"No image found for {product_id}"
        )

        products.at[
            index,
            "Image_URL"
        ] = ""

        continue


    # --------------------------------------------------
    # SELECT IMAGE
    # --------------------------------------------------

    selected = candidates.sample(
        n=1,
        random_state=42 + index
    ).iloc[0]


    image_id = str(
        selected["id"]
    )


    source_file = os.path.join(
        DATASET_IMAGES,
        f"{image_id}.jpg"
    )


    destination_file = os.path.join(
        OUTPUT_FOLDER,
        f"{product_id}.jpg"
    )


    # --------------------------------------------------
    # COPY REAL IMAGE
    # --------------------------------------------------

    shutil.copy2(
        source_file,
        destination_file
    )


    used_images.add(
        image_id
    )


    products.at[
        index,
        "Image_URL"
    ] = (
        f"data/product_images/"
        f"{product_id}.jpg"
    )


    matched += 1


    print(
        f"[{matched}/750] "
        f"{product_id} -> "
        f"{image_id}.jpg"
    )


# --------------------------------------------------
# SAVE PRODUCTS.CSV
# --------------------------------------------------

products.to_csv(
    PRODUCTS_FILE,
    index=False
)


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print()
print("=" * 60)
print("IMAGE INTEGRATION COMPLETE")
print("=" * 60)

print(
    f"Our products:              "
    f"{len(products)}"
)

print(
    f"Images matched:            "
    f"{matched}"
)

print(
    f"Category-only matches:     "
    f"{category_only_matches}"
)

print(
    f"Fallback matches:          "
    f"{fallback_matches}"
)

print(
    f"Images saved in:           "
    f"{OUTPUT_FOLDER}"
)

print()
print(
    "PRODUCTS.csv updated successfully."
)