from datasets import load_dataset
import os


OUTPUT_FOLDER = "data/fashion_images"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)

print("Downloading fashion image dataset...")
print("This may take some time.\n")


dataset = load_dataset(
    "ashraq/fashion-product-images-small",
    split="train"
)


print(
    f"Dataset loaded: {len(dataset):,} images"
)
print()


allowed_categories = {
    "Shirts",
    "Tshirts",
    "Jeans",
    "Trousers",
    "Dresses",
    "Skirts",
    "Jackets",
    "Sweaters"
}


saved = 0


for item in dataset:

    category = str(
        item["articleType"]
    )

    if category not in allowed_categories:
        continue


    image = item["image"]

    image_id = str(
        item["id"]
    )


    filename = (
        f"{image_id}.jpg"
    )

    filepath = os.path.join(
        OUTPUT_FOLDER,
        filename
    )


    if os.path.exists(filepath):
        continue


    try:

        image.convert("RGB").save(
            filepath,
            "JPEG"
        )

        saved += 1

        print(
            f"Saved {saved}: {filename}"
        )

    except Exception as error:

        print(
            f"Skipped {image_id}: {error}"
        )


    if saved >= 1000:
        break


print()
print(
    f"Finished. Saved {saved} clothing images."
)