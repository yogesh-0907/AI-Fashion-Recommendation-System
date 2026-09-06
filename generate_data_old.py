import os
import pandas as pd
import numpy as np

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

np.random.seed(42)
num_rows = 10000

categories = ["Tops", "Bottoms", "Dresses", "Footwear", "Outerwear", "Accessories"]
brands = ["Zara", "H&M", "Nike", "Uniqlo", "Adidas", "Mango", "Puma", "Gucci", "Levi's"]

data = {
    "item_id": [f"ITEM_{10000 + i}" for i in range(num_rows)],
    "name": [f"Fashion Product {i+1}" for i in range(num_rows)],
    "category": np.random.choice(categories, num_rows),
    "brand": np.random.choice(brands, num_rows),
    "price": np.random.uniform(10.0, 250.0, num_rows).round(2),
    "rating": np.random.uniform(2.5, 5.0, num_rows).round(1),
    "user_id": np.random.choice([f"CUST_{i}" for i in range(1001, 1500)], num_rows)
}

df = pd.DataFrame(data)
df.to_csv("data/fashion_data.csv", index=False)
print("✅ Successfully generated 10,000 dataset rows in data/fashion_data.csv")