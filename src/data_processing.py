import pandas as pd
import numpy as np

def load_data():
    """
    Loads product data from a CSV if available, or generates synthetic data.
    """
    try:
        return pd.read_csv("data/fashion_data.csv")
    except FileNotFoundError:
        np.random.seed(42)
        categories = ["Tops", "Bottoms", "Dresses", "Footwear", "Outerwear", "Accessories"]
        brands = ["Zara", "H&M", "Nike", "Uniqlo", "Adidas", "Mango"]
        
        data = {
            "item_id": [f"ITEM_{1000 + i}" for i in range(100)],
            "name": [f"Fashion Item {i+1}" for i in range(100)],
            "category": np.random.choice(categories, 100),
            "brand": np.random.choice(brands, 100),
            "price": np.random.uniform(15.0, 150.0, 100).round(2),
            "rating": np.random.uniform(3.0, 5.0, 100).round(1),
            "user_id": np.random.choice([f"CUST_{i}" for i in range(101, 120)], 100)
        }
        return pd.DataFrame(data)

def get_dashboard_metrics(df: pd.DataFrame) -> dict:
    """
    Calculates key metrics for the dashboard view.
    """
    return {
        "total_items": len(df),
        "total_categories": df["category"].nunique() if "category" in df.columns else 0,
        "total_brands": df["brand"].nunique() if "brand" in df.columns else 0,
        "avg_price": float(df["price"].mean()) if "price" in df.columns else 0.0
    }