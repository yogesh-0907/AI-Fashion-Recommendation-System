## 1. CUSTOMERS.csv

One row represents one customer.

Target records: 10,000 customers.

| Column                   | Data Type   | Description                                              | Allowed / Expected Values | Example   | Used By                          |
| ------------------------ | ----------- | -------------------------------------------------------- | ------------------------- | --------- | -------------------------------- |
| Customer_ID              | String      | Unique identifier for each customer                      | CUST00001, CUST00002, ... | CUST00001 | All modules                      |
| Age                      | Integer     | Customer's age                                           | 18–70                    | 24        | Segmentation                     |
| Gender                   | Categorical | Customer gender                                          | Male, Female, Other       | Female    | Segmentation                     |
| Annual_Income            | Float       | Estimated annual income of the customer                  | Positive value            | 450000.00 | Segmentation                     |
| Customer_Tenure          | Integer     | Number of months since the customer joined               | 1–120                    | 36        | Segmentation                     |
| Purchase_Frequency       | Integer     | Total number of purchase transactions made by customer   | 0 or greater              | 12        | Segmentation / RFM               |
| Total_Spending           | Float       | Total amount spent by the customer                       | 0 or greater              | 12500.00  | Segmentation / RFM               |
| Average_Order_Value      | Float       | Average amount spent per purchase transaction            | 0 or greater              | 1041.67   | Segmentation / RFM               |
| Days_Since_Last_Purchase | Integer     | Number of days since the customer's most recent purchase | 0 or greater              | 18        | Segmentation / RFM               |
| Website_Visits           | Integer     | Number of times the customer visited the website         | 0 or greater              | 45        | Segmentation / Behavior Analysis |

### Customer Data Generation Rules

1. `Customer_ID` must be unique for every customer.
2. `Age` must be between 18 and 70.
3. `Gender` should contain realistic categorical values such as Male, Female, and Other.
4. `Annual_Income` must always be a positive value.
5. `Customer_Tenure` must be between 1 and 120 months.
6. `Purchase_Frequency` must be 0 or greater.
7. `Total_Spending` must be 0 or greater.
8. `Average_Order_Value` must be calculated from actual spending and purchase frequency rather than being independently randomized.

   If:

   `Purchase_Frequency > 0`

   then:

   `Average_Order_Value = Total_Spending / Purchase_Frequency`
9. `Days_Since_Last_Purchase` must be 0 or greater.
10. `Website_Visits` must be 0 or greater.
11. Customer behavior must contain realistic relationships.

   For example:

* Customers with more purchases should generally have higher total spending.
* Customers with higher spending may generally have higher income.
* Highly active customers should generally have more website visits.
* Customers with longer tenure may generally have more accumulated purchases.
* Some customers should be frequent buyers.
* Some customers should be occasional buyers.
* Some customers should be low-engagement or inactive customers.

12. The dataset must contain different behavioral patterns so that K-Means can discover meaningful customer segments.
13. Do not add a `Segment` column. Customer segments must be discovered by the K-Means clustering algorithm.
14. Customer attributes must not be generated as completely independent random values.
15. Behavioral fields must remain consistent with the corresponding records in `PURCHASES.csv`.

   The following relationships must hold:

   `Purchase_Frequency = Number of purchase transactions`

   `Total_Spending = Sum of Product Price × Quantity`

   `Average_Order_Value = Total_Spending / Purchase_Frequency`

   `Days_Since_Last_Purchase = Reference Date - Latest Purchase_Date`

16. Customers with `Purchase_Frequency = 0` must have:

   `Total_Spending = 0`

   `Average_Order_Value = 0`

   `Days_Since_Last_Purchase` should represent that the customer has never made a purchase.

17. The customer dataset should contain enough behavioral variation to support meaningful segmentation using purchasing and engagement characteristics.

### Role in the Project

`CUSTOMERS.csv` stores customer-level demographic and behavioral information.

It will be used as the main customer-level dataset for customer segmentation and behavioral analysis.

Purchase-related information will be cross-validated with `PURCHASES.csv`.

The segmentation pipeline will use customer behavior to identify meaningful groups such as:

* High-value / loyal customers
* Frequent customers
* Occasional customers
* Low-engagement customers
* At-risk customers

The exact segments will not be manually assigned. K-Means will discover the customer groups from the available features.


## 2. PRODUCTS.csv

One row represents one clothing product.

Target records: 500–1,000 products.

| Column      | Data Type   | Description                         | Allowed / Expected Values                                              | Example  | Used By                     |
| ----------- | ----------- | ----------------------------------- | ---------------------------------------------------------------------- | -------- | --------------------------- |
| Product_ID  | String      | Unique identifier for each product  | P00001, P00002, ...                                                    | P00001   | All modules                 |
| Category    | Categorical | Main type of clothing               | Shirt, T-Shirt, Jeans, Trousers, Jacket, Hoodie, Dress, Skirt, Kurta   | Shirt    | Recommendation / Analysis   |
| Subcategory | Categorical | Specific product classification     | Casual, Formal, Party, Sports, Ethnic                                  | Casual   | Recommendation              |
| Fit         | Categorical | Clothing fit or style               | Slim Fit, Regular Fit, Oversized, Relaxed Fit                          | Slim Fit | Recommendation              |
| Color       | Categorical | Main color of the product           | Black, White, Blue, Navy, Red, Green, Grey, Brown, Beige, Pink, Yellow | Blue     | Preference / Recommendation |
| Pattern     | Categorical | Visual pattern of the product       | Plain, Solid, Checked, Striped, Printed, Floral                        | Plain    | Preference / Recommendation |
| Material    | Categorical | Main fabric or material             | Cotton, Linen, Denim, Polyester, Wool, Rayon, Silk, Blended            | Cotton   | Preference / Recommendation |
| Price       | Float       | Selling price of the product in INR | Positive value                                                         | 999.00   | Recommendation / Spending   |

### Product Data Generation Rules

1. `Product_ID` must be unique for every product.
2. Every product must have a valid `Category`.
3. Every product must have a valid `Subcategory`.
4. Every product must have a valid `Fit`.
5. Every product must have a valid `Color`.
6. Every product must have a valid `Pattern`.
7. Every product must have a valid `Material`.
8. `Price` must always be greater than zero.
9. Product attributes should be generated using realistic combinations rather than assigning every attribute completely independently.
10. Product prices should vary according to the type of product.

    For example:

    * T-Shirts should generally be cheaper than Jackets.
    * Jeans and Trousers should generally fall within a different price range from T-Shirts.
    * Dresses and premium ethnic wear may have higher prices.
11. Material should influence the expected price where appropriate.

    For example:

    * Silk and premium materials may generally have higher prices.
    * Cotton and blended materials may generally have moderate prices.
12. The catalog should contain enough products across different categories, fits, colors, patterns, and materials to support meaningful personalized recommendations.
13. Each category should contain multiple products with different combinations of attributes.
14. Product attributes should be compatible where appropriate.

    For example:

    * Denim should be commonly associated with Jeans or Jackets.
    * Floral patterns should be more common for Dresses and certain ethnic products.
    * Slim Fit should be more common for Shirts, Trousers, and Jeans.
    * Oversized and Relaxed Fit should be more common for T-Shirts and casual clothing.
15. The catalog should contain different price ranges so that the recommendation system can handle customers with different spending preferences.
16. Products must not be generated as completely independent random values.
17. The catalog should contain sufficient attribute diversity so that the recommendation engine can identify products similar to a customer's learned preferences.

### Role in the Project

`PRODUCTS.csv` represents the clothing catalog available in the system.

It provides the product attributes required by the personalized recommendation engine.

The recommendation system will compare customer preferences learned from `PURCHASES.csv` with product attributes such as:

* Category
* Subcategory
* Fit
* Color
* Pattern
* Material
* Price

For example, if a customer frequently purchases:

* Shirts
* Slim Fit
* Blue
* Plain
* Cotton
* Around ₹800–₹1,200

the recommendation engine should use these learned preferences to rank similar products from `PRODUCTS.csv`.

The product catalog will also be used to satisfy explicit customer requests such as:

> "Show me slim-fit blue shirts under ₹1,200."

The recommendation engine should filter and rank products according to the customer's requested requirements and learned preferences.



## 3. PURCHASES.csv

One row represents one customer-product purchase transaction.

Target records: approximately 50,000–150,000 records.

| Column        | Data Type | Description                         | Allowed / Expected Values   | Example    | Used By                              |
| ------------- | --------- | ----------------------------------- | --------------------------- | ---------- | ------------------------------------ |
| Purchase_ID   | String    | Unique identifier for each purchase | PUR00001, PUR00002, ...     | PUR00001   | Purchase Tracking                    |
| Customer_ID   | String    | Customer who made the purchase      | Must exist in CUSTOMERS.csv | CUST00001  | Segmentation / Preference Analysis   |
| Product_ID    | String    | Product purchased                   | Must exist in PRODUCTS.csv  | P00001     | Recommendation / Preference Analysis |
| Purchase_Date | Date      | Date on which the purchase occurred | Valid historical date       | 2026-06-12 | RFM / Preference Analysis            |
| Quantity      | Integer   | Number of units purchased           | 1 or greater                | 1          | Spending / Preference Analysis       |

### Purchase Data Generation Rules

1. `Purchase_ID` must be unique for every purchase transaction.
2. Every `Customer_ID` must exist in `CUSTOMERS.csv`.
3. Every `Product_ID` must exist in `PRODUCTS.csv`.
4. `Quantity` must be at least 1.
5. `Purchase_Date` must be a valid date.
6. Purchase dates should cover a realistic historical period rather than being concentrated on a single date.
7. Customers should have different numbers of purchase transactions.
8. Some customers should make frequent purchases, while others should make occasional or very few purchases.
9. Customers should repeatedly purchase products with similar attributes according to their learned preferences.

   For example, a customer who frequently purchases:

   * Shirts
   * Slim Fit
   * Blue
   * Plain
   * Cotton

   should have a higher probability of purchasing products with similar attributes in future transactions.
10. Purchase behavior should vary between different customer behavior patterns.

    For example:

    * Frequent customers should generally have more transactions.
    * High-value customers should generally spend more.
    * Occasional customers should have fewer transactions.
    * Inactive customers should have older last-purchase dates or no purchase history.
11. Product selection should depend on the customer's preference profile rather than being completely random.
12. Purchase quantities should be realistic. Most transactions should contain a small number of units, while larger quantities should occur less frequently.
13. The purchase history must contain enough repeated behavior to allow the system to learn customer preferences for:

    * Category
    * Subcategory
    * Fit
    * Color
    * Pattern
    * Material
    * Price range
14. Purchase records must be consistent with `PRODUCTS.csv`.

    The spending for each purchase transaction must be calculated using:

    `Purchase Amount = Product Price × Quantity`
15. Customer-level purchase statistics in `CUSTOMERS.csv` must be derived from the purchase history.

    `Purchase_Frequency = Number of purchase transactions`

    `Total_Spending = Sum of Product Price × Quantity`

    `Average_Order_Value = Total_Spending / Purchase_Frequency`

    `Days_Since_Last_Purchase = Reference Date - Latest Purchase_Date`
16. The purchase history must contain enough variation to support customer segmentation using Recency, Frequency, Monetary (RFM) and other behavioral features.
17. The purchase history should include customers with different purchasing patterns so that meaningful customer segments can be discovered by K-Means.
18. Purchase records must not be generated as completely independent random customer-product combinations.

### Role in the Project

`PURCHASES.csv` represents the historical purchase behavior of customers.

It connects `CUSTOMERS.csv` with `PRODUCTS.csv` and acts as the main source for learning customer preferences.

The relationship between the three datasets is:

`CUSTOMERS.csv`

→ identifies the customer

`PURCHASES.csv`

→ records what the customer purchased and when

`PRODUCTS.csv`

→ describes the characteristics of the purchased product

The preference analysis system will aggregate purchase history to determine each customer's preferred:

* Categories
* Subcategories
* Fits
* Colors
* Patterns
* Materials
* Price ranges

These learned preferences will then be used by the recommendation engine to rank suitable products from `PRODUCTS.csv`.

The purchase history will also provide the data required to calculate RFM features:

* **Recency** — How recently the customer purchased
* **Frequency** — How often the customer purchases
* **Monetary** — How much the customer spends
