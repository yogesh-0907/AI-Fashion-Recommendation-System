import os
import sqlite3
from datetime import datetime
import hashlib

DATABASE_NAME = "fashion_app.db"


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            customer_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            created_at TEXT
        )
    """)
    
    # Add role column to existing users table if it does not exist
    try:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT DEFAULT 'customer'
        """)
    except sqlite3.OperationalError as error:
        if "duplicate column name" not in str(error):
            raise
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            activity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            activity_type TEXT,
            product_id TEXT,
            search_query TEXT,
            activity_date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            product_id TEXT,
            added_date TEXT,
            UNIQUE(customer_id, product_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            order_date TEXT,
            order_status TEXT,
            total_amount REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id TEXT,
            quantity INTEGER,
            price REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            product_id TEXT,
            quantity INTEGER DEFAULT 1,
            added_date TEXT,
            UNIQUE(customer_id, product_id)
        )
    """)

    connection.commit()
    connection.close()


def add_to_wishlist(customer_id, product_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO wishlist
        (
            customer_id,
            product_id,
            added_date
        )
        VALUES (?, ?, ?)
    """, (
        customer_id,
        product_id,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def remove_from_wishlist(customer_id, product_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM wishlist
        WHERE customer_id = ?
        AND product_id = ?
    """, (
        customer_id,
        product_id
    ))

    connection.commit()
    connection.close()


def get_wishlist(customer_id):

    connection = get_connection()

    wishlist = connection.execute("""
        SELECT product_id
        FROM wishlist
        WHERE customer_id = ?
        ORDER BY added_date DESC
    """, (
        customer_id,
    )).fetchall()

    connection.close()

    return [
        row[0]
        for row in wishlist
    ]

# --------------------------------------------------
# CART
# --------------------------------------------------

def add_to_cart(customer_id, product_id, quantity=1):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO cart
        (
            customer_id,
            product_id,
            quantity,
            added_date
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(customer_id, product_id)
        DO UPDATE SET
            quantity = quantity + excluded.quantity
    """, (
        customer_id,
        product_id,
        quantity,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def remove_from_cart(customer_id, product_id):

    connection = get_connection()

    connection.execute("""
        DELETE FROM cart
        WHERE customer_id = ?
        AND product_id = ?
    """, (
        customer_id,
        product_id
    ))

    connection.commit()
    connection.close()


def update_cart_quantity(
    customer_id,
    product_id,
    quantity
):

    connection = get_connection()

    if quantity <= 0:

        connection.execute("""
            DELETE FROM cart
            WHERE customer_id = ?
            AND product_id = ?
        """, (
            customer_id,
            product_id
        ))

    else:

        connection.execute("""
            UPDATE cart
            SET quantity = ?
            WHERE customer_id = ?
            AND product_id = ?
        """, (
            quantity,
            customer_id,
            product_id
        ))

    connection.commit()
    connection.close()


def get_cart(customer_id):

    connection = get_connection()

    cart = connection.execute("""
        SELECT
            product_id,
            quantity
        FROM cart
        WHERE customer_id = ?
        ORDER BY added_date DESC
    """, (
        customer_id,
    )).fetchall()

    connection.close()

    return cart

# --------------------------------------------------
# ORDERS
# --------------------------------------------------

def create_order(
    customer_id,
    cart_items,
    products_df
):
    connection = get_connection()
    cursor = connection.cursor()

    total_amount = 0

    # ----------------------------------------------
    # Calculate total
    # ----------------------------------------------

    for product_id, quantity in cart_items:

        product = products_df[
            products_df["Product_ID"] == product_id
        ]

        if product.empty:
            continue

        price = float(
            product.iloc[0]["Price"]
        )

        total_amount += price * quantity

    # ----------------------------------------------
    # Create order
    # ----------------------------------------------

    order_date = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO orders
        (
            customer_id,
            order_date,
            order_status,
            total_amount
        )
        VALUES (?, ?, ?, ?)
    """, (
        customer_id,
        order_date,
        "Confirmed",
        total_amount
    ))

    order_id = cursor.lastrowid

    # ----------------------------------------------
    # Create order items
    # ----------------------------------------------

    for product_id, quantity in cart_items:

        product = products_df[
            products_df["Product_ID"] == product_id
        ]

        if product.empty:
            continue

        price = float(
            product.iloc[0]["Price"]
        )

        cursor.execute("""
            INSERT INTO order_items
            (
                order_id,
                product_id,
                quantity,
                price
            )
            VALUES (?, ?, ?, ?)
        """, (
            order_id,
            product_id,
            quantity,
            price
        ))

    # ----------------------------------------------
    # Clear customer's cart
    # ----------------------------------------------

    cursor.execute("""
        DELETE FROM cart
        WHERE customer_id = ?
    """, (
        customer_id,
    ))

    connection.commit()
    connection.close()

    return order_id, total_amount


def get_orders(customer_id):

    connection = get_connection()

    orders = connection.execute("""
        SELECT
            order_id,
            order_date,
            order_status,
            total_amount
        FROM orders
        WHERE customer_id = ?
        ORDER BY order_date DESC
    """, (
        customer_id,
    )).fetchall()

    connection.close()

    return orders


def get_order_items(order_id):

    connection = get_connection()

    items = connection.execute("""
        SELECT
            product_id,
            quantity,
            price
        FROM order_items
        WHERE order_id = ?
    """, (
        order_id,
    )).fetchall()

    connection.close()

    return items

# --------------------------------------------------
# USER ACTIVITY
# --------------------------------------------------

def record_activity(
    customer_id,
    activity_type,
    product_id=None,
    search_query=None
):

    connection = get_connection()

    connection.execute("""
        INSERT INTO user_activity
        (
            customer_id,
            activity_type,
            product_id,
            search_query,
            activity_date
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        customer_id,
        activity_type,
        product_id,
        search_query,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_user_activity(customer_id):

    connection = get_connection()

    activities = connection.execute("""
        SELECT
            activity_id,
            activity_type,
            product_id,
            search_query,
            activity_date
        FROM user_activity
        WHERE customer_id = ?
        ORDER BY activity_date DESC
    """, (
        customer_id,
    )).fetchall()

    connection.close()

    return activities

# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

if __name__ == "__main__":

    initialize_database()

    print(
        "Fashion application database "
        "initialized successfully."
    )

def register_user(name, email, password):

    connection = get_connection()

    try:

        password_hash = hashlib.sha256(
            password.encode()
        ).hexdigest()

        connection.execute("""
            INSERT INTO users
            (
                customer_id,
                name,
                email,
                password,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            f"USER{int(datetime.now().timestamp())}",
            name,
            email,
            password_hash,
            "customer",
            datetime.now().isoformat()
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def login_user(email, password):

    connection = get_connection()

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    user = connection.execute("""
        SELECT
            customer_id,
            name,
            email,
            role
        FROM users
        WHERE email = ?
        AND password = ?
    """, (
        email,
        password_hash
    )).fetchone()

    connection.close()

    if user is None:
        return None

    admin_email = os.getenv(
        "ADMIN_EMAIL",
        ""
    ).strip().lower()

    if (
        admin_email
        and user[2].strip().lower() == admin_email
    ):
        user = (
            user[0],
            user[1],
            user[2],
            "admin"
        )

    return user

def make_user_admin(email):

    connection = get_connection()

    connection.execute("""
        UPDATE users
        SET role = 'admin'
        WHERE email = ?
    """, (
        email,
    ))

    connection.commit()
    connection.close()

initialize_database()

def reset_user_password(email, new_password):

    import hashlib

    password_hash = hashlib.sha256(
        new_password.encode()
    ).hexdigest()

    connection = get_connection()

    connection.execute("""
        UPDATE users
        SET password = ?
        WHERE email = ?
    """, (
        password_hash,
        email
    ))

    connection.commit()

    connection.close()