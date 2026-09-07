import sys
import os
import random
import smtplib
import time
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "src"
    )
)

import streamlit as st
import pandas as pd

from shopping import (
    get_all_products,
    search_products,
    filter_by_category,
    get_product_by_id
)
from recommendation import recommend_products

from query_parser import parse_user_query

from database import (
    add_to_wishlist,
    remove_from_wishlist,
    get_wishlist,
    add_to_cart,
    get_cart,
    remove_from_cart,
    update_cart_quantity,
    create_order,
    get_orders,
    get_order_items,
    record_activity,
    register_user,
    login_user,
)

from database import get_user_activity

from ai_assistant import ask_customer_assistant
from ai_context import build_customer_context
from customer_profile import get_customer_profile
from database import (
    get_connection,
    reset_user_password,
    get_registered_user_count
)
from segmentation import perform_segmentation
from preferences import get_customer_preferences

# --------------------------------------------------
# SESSION STATE INITIALIZATION
# --------------------------------------------------

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "order_id" not in st.session_state:
    st.session_state.order_id = None

if "order_total" not in st.session_state:
    st.session_state.order_total = 0

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "pending_registration" not in st.session_state:
    st.session_state.pending_registration = None
    
if "registration_otp" not in st.session_state:
    st.session_state.registration_otp = None

if "otp_email" not in st.session_state:
    st.session_state.otp_email = None

if "otp_expiry" not in st.session_state:
    st.session_state.otp_expiry = None


# --------------------------------------------------
# SEND OTP EMAIL
# --------------------------------------------------

def send_otp_email(receiver_email, otp):

    sender_email = os.getenv(
        "EMAIL_ADDRESS",
        ""
    ).strip()

    app_password = os.getenv(
        "EMAIL_APP_PASSWORD",
        ""
    ).replace(" ", "").strip()

    if not sender_email or not app_password:
        raise ValueError(
            "EMAIL_ADDRESS or EMAIL_APP_PASSWORD "
            "is missing from .env"
        )

    message = EmailMessage()

    message["Subject"] = (
        "Fashion Store - Email Verification OTP"
    )

    message["From"] = sender_email
    message["To"] = receiver_email

    message.set_content(
        f"""
Hello,

Your Fashion Store verification OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this, please ignore this email.

Fashion Store
"""
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as server:

        server.login(
            sender_email,
            app_password
        )

        server.send_message(message)

# --------------------------------------------------
# FORGOT PASSWORD SESSION STATE
# --------------------------------------------------

if "forgot_password_otp" not in st.session_state:
    st.session_state.forgot_password_otp = None

if "forgot_password_email" not in st.session_state:
    st.session_state.forgot_password_email = None

if "forgot_password_expiry" not in st.session_state:
    st.session_state.forgot_password_expiry = None

if "forgot_password_verified" not in st.session_state:
    st.session_state.forgot_password_verified = False
    
# --------------------------------------------------
# FORGOT PASSWORD
# --------------------------------------------------

if (
    st.session_state.logged_in_user is None
    and st.session_state.current_page == "forgot_password"
):

    # --------------------------------------------------
    # FORGOT PASSWORD
    # --------------------------------------------------

    if (
        st.session_state.logged_in_user is None
        and st.session_state.current_page == "forgot_password"
    ):

        st.title("🔑 Forgot Password")

        # ==================================================
        # OTP VERIFICATION
        # ==================================================

        if (
            st.session_state.forgot_password_otp is not None
            and not st.session_state.forgot_password_verified
        ):

            st.info(
                f"Password reset OTP sent to "
                f"**{st.session_state.forgot_password_email}**"
            )

            st.write(
                "Enter the 6-digit OTP sent to your email."
            )

            entered_otp = st.text_input(
                "Enter 6-digit OTP",
                max_chars=6,
                key="forgot_password_otp_input"
            )

            if st.button(
                "✅ Verify OTP",
                use_container_width=True
            ):

                if (
                    time.time()
                    > st.session_state.forgot_password_expiry
                ):

                    st.error(
                        "OTP expired. Please request a new OTP."
                    )

                elif (
                    entered_otp
                    != st.session_state.forgot_password_otp
                ):

                    st.error(
                        "Invalid OTP. Please try again."
                    )

                else:

                    st.session_state.forgot_password_verified = True

                    st.success(
                        "✅ OTP verified successfully!"
                    )

                    st.rerun()

            if st.button(
                "🔄 Resend OTP",
                use_container_width=True
            ):

                new_otp = str(
                    random.randint(
                        100000,
                        999999
                    )
                )

                try:

                    send_otp_email(
                        st.session_state.forgot_password_email,
                        new_otp
                    )

                    st.session_state.forgot_password_otp = new_otp

                    st.session_state.forgot_password_expiry = (
                        time.time() + 300
                    )

                    st.success(
                        "📧 New OTP sent successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Failed to resend OTP: {error}"
                    )

        # ==================================================
        # SEND RESET OTP
        # ==================================================

        elif not st.session_state.forgot_password_verified:

            st.write(
                "Enter your registered email address to receive "
                "a password reset OTP."
            )

            forgot_email = st.text_input(
                "Email",
                key="forgot_password_email_input"
            )

            if st.button(
                "📧 Send Reset OTP",
                use_container_width=True
            ):

                connection = get_connection()

                user = connection.execute(
                    """
                    SELECT customer_id
                    FROM users
                    WHERE email = ?
                    """,
                    (forgot_email.strip(),)
                ).fetchone()

                connection.close()

                if user is None:

                    st.error(
                        "No account found with this email address."
                    )

                else:

                    otp = str(
                        random.randint(
                            100000,
                            999999
                        )
                    )

                    try:

                        send_otp_email(
                            forgot_email.strip(),
                            otp
                        )

                        st.session_state.forgot_password_otp = otp

                        st.session_state.forgot_password_email = (
                            forgot_email.strip()
                        )

                        st.session_state.forgot_password_expiry = (
                            time.time() + 300
                        )

                        st.session_state.forgot_password_verified = False

                        st.rerun()

                    except Exception as error:

                        st.error(
                            f"Failed to send OTP: {error}"
                        )
        # ==================================================
        # SET NEW PASSWORD
        # ==================================================

        if st.session_state.forgot_password_verified:

            st.success(
                "✅ OTP verified successfully!"
            )

            st.write(
                "Create a new password for your account."
            )

            new_password = st.text_input(
                "New Password",
                type="password",
                key="new_password"
            )

            confirm_password = st.text_input(
                "Confirm New Password",
                type="password",
                key="confirm_new_password"
            )

            if st.button(
                "🔐 Reset Password",
                use_container_width=True
            ):

                if not new_password or not confirm_password:

                    st.warning(
                        "Please enter and confirm your new password."
                    )

                elif new_password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    reset_user_password(
                        st.session_state.forgot_password_email,
                        new_password
                    )

                    st.success(
                        "🎉 Password reset successfully!"
                    )

                    st.session_state.forgot_password_otp = None
                    st.session_state.forgot_password_email = None
                    st.session_state.forgot_password_expiry = None
                    st.session_state.forgot_password_verified = False

                    st.info(
                        "You can now login with your new password."
                    )

                    if st.button(
                        "🔐 Go to Login",
                        use_container_width=True
                    ):

                        st.session_state.current_page = "home"
                        st.rerun()
        if st.button(
            "← Back to Login",
            use_container_width=True
        ):

            st.session_state.current_page = "home"

            st.session_state.forgot_password_otp = None

            st.session_state.forgot_password_email = None

            st.session_state.forgot_password_expiry = None

            st.session_state.forgot_password_verified = False

            st.rerun()

        st.stop()

# --------------------------------------------------
# LOGIN / REGISTER
# --------------------------------------------------

if st.session_state.logged_in_user is None:

    # ==================================================
    # OTP VERIFICATION SCREEN
    # ==================================================

    if st.session_state.registration_otp is not None:

        st.title("📧 Verify Your Email")

        st.info(
            f"An OTP has been sent to "
            f"**{st.session_state.otp_email}**"
        )

        st.write(
            "Enter the 6-digit OTP sent to your email."
        )

        entered_otp = st.text_input(
            "Enter 6-digit OTP",
            max_chars=6,
            key="entered_registration_otp"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✅ Verify & Create Account",
                use_container_width=True
            ):

                if time.time() > st.session_state.otp_expiry:

                    st.error(
                        "OTP expired. Please request a new OTP."
                    )

                    st.session_state.registration_otp = None
                    st.session_state.otp_email = None
                    st.session_state.otp_expiry = None

                    st.rerun()

                elif entered_otp != st.session_state.registration_otp:

                    st.error(
                        "Invalid OTP. Please try again."
                    )

                else:

                    registration = st.session_state.pending_registration

                    success = register_user(
                        registration["name"],
                        registration["email"],
                        registration["password"]
                    )

                    if success:

                        st.success(
                            "🎉 Email verified! "
                            "Your account has been created successfully."
                        )

                        # Clear OTP state
                        st.session_state.registration_otp = None
                        st.session_state.otp_email = None
                        st.session_state.otp_expiry = None
                        st.session_state.pending_registration = None
                        
                        # Clear registration fields
                        st.session_state.register_name = ""
                        st.session_state.register_email = ""
                        st.session_state.register_password = ""

                        st.info(
                            "You can now login using your email and password."
                        )

                    else:

                        st.error(
                            "An account with this email already exists."
                        )

        with col2:

            if st.button(
                "🔄 Resend OTP",
                use_container_width=True
            ):

                new_otp = str(
                    random.randint(
                        100000,
                        999999
                    )
                )

                try:

                    send_otp_email(
                        st.session_state.otp_email,
                        new_otp
                    )

                    st.session_state.registration_otp = new_otp

                    st.session_state.otp_expiry = (
                        time.time() + 300
                    )

                    st.success(
                        "📧 New OTP sent successfully!"
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Failed to resend OTP: {error}"
                    )
        # IMPORTANT:
        # Do not render the shopping application
        # while OTP verification is active.

        st.stop()


    # ==================================================
    # LOGIN / REGISTER SCREEN
    # ==================================================

    st.title("👗 Fashion AI Store")

    login_tab, register_tab = st.tabs(
        ["🔐 Login", "📝 Register"]
    )


    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------

    with login_tab:

        email = st.text_input(
            "Email",
            key="login_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "Login",
            use_container_width=True
        ):

            user = login_user(
                email,
                password
            )

            if user:

                st.session_state.logged_in_user = user

                st.session_state.customer_id = user[0]

                st.success(
                    f"Welcome back, {user[1]}! 🎉"
                )

                st.rerun()

            else:

                st.error(
                    "Invalid email or password."
                )

        if st.button(
            "🔑 Forgot Password?",
            use_container_width=True
        ):
            st.session_state.current_page = "forgot_password"
            st.rerun()
    # --------------------------------------------------
    # REGISTER
    # --------------------------------------------------

    with register_tab:

        name = st.text_input(
            "Name",
            key="registration_name"
        )

        email = st.text_input(
            "Email",
            key="registration_email"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="registration_password"
        )

        if st.button(
            "📧 Send OTP",
            use_container_width=True
        ):

            if not name or not email or not password:

                st.warning(
                    "Please fill in all fields."
                )

            else:

                otp = str(
                    random.randint(
                        100000,
                        999999
                    )
                )

                try:

                    send_otp_email(
                        email,
                        otp
                    )

                    # Store registration information
                    # so it survives Streamlit reruns.

                    st.session_state.pending_registration = {
                        "name": name,
                        "email": email,
                        "password": password
                    }

                    st.session_state.registration_otp = otp

                    st.session_state.otp_email = email

                    st.session_state.otp_expiry = (
                        time.time() + 300
                    )

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Failed to send OTP: {error}"
                    )

    # Stop the rest of the shopping application
    # until the user has logged in or completed registration.

    st.stop()
# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Fashion Store",
    page_icon="👗",
    layout="wide"
)


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_products():
    return pd.read_csv("data/PRODUCTS.csv")


@st.cache_data
def load_customers():
    return pd.read_csv("data/CUSTOMERS.csv")


@st.cache_data
def load_purchases():
    return pd.read_csv("data/PURCHASES.csv")


products = load_products()
customers = load_customers()
purchases = load_purchases()

# --------------------------------------------------
# CUSTOMER SEGMENTATION
# --------------------------------------------------

segmented_customers, cluster_summary, silhouette = (
    perform_segmentation(customers)
)
# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "pending_registration" not in st.session_state:
    st.session_state.pending_registration = None
    
if "forgot_password_otp" not in st.session_state:
    st.session_state.forgot_password_otp = None

if "forgot_password_email" not in st.session_state:
    st.session_state.forgot_password_email = None

if "forgot_password_expiry" not in st.session_state:
    st.session_state.forgot_password_expiry = None

if "forgot_password_verified" not in st.session_state:
    st.session_state.forgot_password_verified = False

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

if "customer_id" not in st.session_state:
    st.session_state.customer_id = None
    
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

if "order_id" not in st.session_state:
    st.session_state.order_id = None

if "order_total" not in st.session_state:
    st.session_state.order_total = 0
    
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "registration_otp" not in st.session_state:
    st.session_state.registration_otp = None

if "otp_email" not in st.session_state:
    st.session_state.otp_email = None

if "otp_expiry" not in st.session_state:
    st.session_state.otp_expiry = None
    
if "forgot_password_otp" not in st.session_state:
    st.session_state.forgot_password_otp = None

if "forgot_password_email" not in st.session_state:
    st.session_state.forgot_password_email = None

if "forgot_password_expiry" not in st.session_state:
    st.session_state.forgot_password_expiry = None

if "forgot_password_verified" not in st.session_state:
    st.session_state.forgot_password_verified = False

# --------------------------------------------------
# SIDEBAR - CUSTOMER LOGIN
# --------------------------------------------------

with st.sidebar:

    st.header("👤 Customer")

    # --------------------------------------------------
    # REGISTERED USER
    # --------------------------------------------------

    if st.session_state.logged_in_user is not None:

        logged_in_customer_id = (
            st.session_state.logged_in_user[0]
        )

        logged_in_name = (
            st.session_state.logged_in_user[1]
        )

        st.session_state.customer_id = (
            logged_in_customer_id
        )

        st.success(
            f"Logged in as {logged_in_name}"
        )

        st.write(
            f"**Customer ID:** "
            f"{logged_in_customer_id}"
        )

        if st.button(
            "🚪 Logout",
            use_container_width=True
        ):
            st.session_state.logged_in_user = None
            st.session_state.customer_id = None
            st.rerun()

    # --------------------------------------------------
    # HISTORICAL / GUEST CUSTOMER
    # --------------------------------------------------

    else:

        customer_options = [
            "Guest Customer"
        ] + customers["Customer_ID"].tolist()

        current_customer = (
            st.session_state.customer_id
        )

        if current_customer is None:

            default_index = 0

        elif current_customer in customer_options:

            default_index = customer_options.index(
                current_customer
            )

        else:

            default_index = 0

        selected_customer = st.selectbox(
            "Select Customer",
            customer_options,
            index=default_index
        )

        if selected_customer == "Guest Customer":

            st.session_state.customer_id = None

            st.info(
                "Shopping as a guest. "
                "Recommendations will use popular products."
            )

        else:

            st.session_state.customer_id = (
                selected_customer
            )

            customer = customers[
                customers["Customer_ID"] == selected_customer
            ].iloc[0]

            st.success(
                f"Logged in as {selected_customer}"
            )

            st.write(
                f"**Age:** {customer['Age']}"
            )

            st.write(
                f"**Gender:** {customer['Gender']}"
            )

            st.write(
                f"**Purchases:** "
                f"{customer['Purchase_Frequency']}"
            )

            st.write(
                f"**Total Spending:** "
                f"₹{customer['Total_Spending']:,.0f}"
            )

    st.divider()

    st.subheader("🛍️ Shopping")


if st.button(
    "Home",
    use_container_width=True
):
    st.session_state.current_page = "home"
    st.session_state.selected_product = None
    st.rerun()


if st.button(
    "📦 My Orders",
    use_container_width=True
):
    st.session_state.current_page = "orders"
    st.session_state.selected_product = None
    st.rerun()


if (
    st.session_state.logged_in_user is not None
    and st.session_state.logged_in_user[3] == "admin"
):

    if st.button(
        "📊 Admin Dashboard",
        use_container_width=True
    ):
        st.session_state.current_page = "admin"
        st.session_state.selected_product = None
        st.rerun()


if st.button(
    "❤️ Wishlist",
    use_container_width=True
):
    st.session_state.current_page = "wishlist"
    st.session_state.selected_product = None
    st.rerun()


if st.button(
    "🛒 Cart",
    use_container_width=True
):
    st.session_state.current_page = "cart"
    st.session_state.selected_product = None
    st.rerun()
    
# --------------------------------------------------
# MY ORDERS PAGE
# --------------------------------------------------

if st.session_state.current_page == "orders":

    st.title("📦 My Orders")

    if not st.session_state.customer_id:

        st.warning(
            "Please select a customer first."
        )

        st.stop()

    orders = get_orders(
        st.session_state.customer_id
    )

    if not orders:

        st.info(
            "You haven't placed any orders yet."
        )

        if st.button(
            "← Continue Shopping",
            use_container_width=True
        ):

            st.session_state.current_page = "home"
            st.rerun()

        st.stop()


    st.write(
        f"**{len(orders)} order(s) found**"
    )

    st.divider()


    for order_id, order_date, status, total_amount in orders:

        st.subheader(
            f"📦 Order #{order_id}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(
                f"**Date:** {order_date[:10]}"
            )

        with col2:
            st.write(
                f"**Status:** {status}"
            )

        with col3:
            st.write(
                f"**Total:** ₹{total_amount:,.0f}"
            )


        items = get_order_items(
            order_id
        )

        for product_id, quantity, price in items:

            product = get_product_by_id(
                products,
                product_id
            )

            if product is None:
                continue

            item_col1, item_col2 = st.columns(
                [1, 3]
            )

            with item_col1:

                st.image(
                    product["Image_URL"],
                    width="stretch"
                )

            with item_col2:

                st.write(
                    f"**{product['Product_Name']}**"
                )

                st.write(
                    f"Quantity: {quantity}"
                )

                st.write(
                    f"Price: ₹{price:,.0f}"
                )

                st.write(
                    f"Item Total: "
                    f"₹{price * quantity:,.0f}"
                )

        st.divider()


    if st.button(
        "← Continue Shopping",
        use_container_width=True
    ):

        st.session_state.current_page = "home"
        st.rerun()


    st.stop()
    
# --------------------------------------------------
# STORE HEADER
# --------------------------------------------------

st.title("👗 Fashion Store")

if st.session_state.customer_id:

    st.write(
        f"Welcome back, "
        f"**{st.session_state.customer_id}** 👋"
    )

else:

    st.write(
        "Discover clothing that matches your style."
    )
# --------------------------------------------------
# CART PAGE
# --------------------------------------------------

if st.session_state.current_page == "cart":

    st.title("🛒 My Cart")

    if not st.session_state.customer_id:

        st.warning(
            "Please select a customer first."
        )

        st.stop()


    cart_items = get_cart(
        st.session_state.customer_id
    )


    if not cart_items:

        st.info(
            "Your cart is empty."
        )

        if st.button(
            "← Continue Shopping"
        ):

            st.session_state.current_page = "home"
            st.rerun()

        st.stop()


    total_amount = 0
    total_items = 0


    for product_id, quantity in cart_items:

        product = get_product_by_id(
            products,
            product_id
        )

        if product is None:
            continue


        item_total = (
            product["Price"] * quantity
        )

        total_amount += item_total
        total_items += quantity


        col1, col2, col3 = st.columns(
            [1, 2, 1]
        )


        with col1:

            st.image(
                product["Image_URL"],
                width="stretch"
            )


        with col2:

            st.subheader(
                product["Product_Name"]
            )

            st.write(
                f"⭐ {product['Rating']:.1f}"
            )

            st.write(
                f"₹{product['Price']:,.0f}"
            )

            st.write(
                f"Quantity: **{quantity}**"
            )


        with col3:

            st.write(
                f"### ₹{item_total:,.0f}"
            )


            if st.button(
                "➖",
                key=f"minus_{product_id}"
            ):

                update_cart_quantity(
                    st.session_state.customer_id,
                    product_id,
                    quantity - 1
                )

                st.rerun()


            if st.button(
                "➕",
                key=f"plus_{product_id}"
            ):

                update_cart_quantity(
                    st.session_state.customer_id,
                    product_id,
                    quantity + 1
                )

                st.rerun()


            if st.button(
                "🗑️ Remove",
                key=f"remove_{product_id}"
            ):

                remove_from_cart(
                    st.session_state.customer_id,
                    product_id
                )

                st.rerun()


        st.divider()


    # --------------------------------------------------
    # CART SUMMARY
    # --------------------------------------------------

    st.subheader("Order Summary")

    summary_col1, summary_col2 = st.columns(2)


    with summary_col1:

        st.write(
            f"**Total Items:** {total_items}"
        )


    with summary_col2:

        st.write(
            f"**Total Amount:** "
            f"₹{total_amount:,.0f}"
        )


    # --------------------------------------------------
    # CHECKOUT
    # --------------------------------------------------

    st.divider()

    if st.button(
        "💳 Proceed to Checkout",
        use_container_width=True
    ):

        try:

            order_id, total_amount = create_order(
                st.session_state.customer_id,
                cart_items,
                products
            )
            
            for product_id, quantity in cart_items:
                record_activity(
                    st.session_state.customer_id,
                    "PURCHASE",
                    product_id
                )
                
            st.session_state.order_id = order_id
            st.session_state.order_total = total_amount

            st.session_state.current_page = "order_success"

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to place order: {error}"
            )

        st.session_state.current_page = "home"
        st.rerun()


    st.stop()
    
# --------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------

if (
    st.session_state.current_page == "admin"
    and st.session_state.logged_in_user is not None
    and st.session_state.logged_in_user[3] == "admin"
):
    st.title("📊 Admin Dashboard")

    st.subheader("Business Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        registered_users = get_registered_user_count()

        total_customers = (
            len(customers)
            + registered_users
        )

        st.metric(
            "Customers",
            f"{total_customers:,}"
        )

    with col2:
        st.metric(
            "Products",
            f"{len(products):,}"
        )

    with col3:
        st.metric(
            "Historical Purchases",
            f"{len(purchases):,}"
        )

    with col4:
        st.metric(
            "Total Revenue",
            f"₹{customers['Total_Spending'].sum():,.0f}"
        )

    st.markdown("---")

    st.subheader("👥 Customer Intelligence")

    st.dataframe(
        customers[
            [
                "Customer_ID",
                "Age",
                "Gender",
                "Annual_Income",
                "Purchase_Frequency",
                "Total_Spending",
                "Average_Order_Value",
                "Days_Since_Last_Purchase"
            ]
        ].head(100),
        use_container_width=True
    )
    # --------------------------------------------------
    # CUSTOMER SEGMENTATION
    # --------------------------------------------------

    st.markdown("---")

    st.subheader("🧠 Customer Segmentation")

    segmented_customers, cluster_summary, silhouette = (
        perform_segmentation(customers)
    )

    segment_counts = (
        segmented_customers["Segment"]
        .value_counts()
    )

    st.bar_chart(segment_counts)

    st.dataframe(
        segmented_customers[
            [
                "Customer_ID",
                "Segment",
                "Purchase_Frequency",
                "Total_Spending",
                "Average_Order_Value",
                "Days_Since_Last_Purchase"
            ]
        ].head(100),
        use_container_width=True
    )
    
    # --------------------------------------------------
    # PRODUCT PERFORMANCE
    # --------------------------------------------------

    st.markdown("---")

    st.subheader("👕 Product Performance")

    product_performance = (
        purchases
        .groupby("Product_ID")
        .agg(
            Purchase_Count=("Purchase_ID", "count"),
            Quantity_Sold=("Quantity", "sum")
        )
        .reset_index()
    )

    product_performance = product_performance.merge(
        products[
            [
                "Product_ID",
                "Product_Name",
                "Category",
                "Price",
                "Rating"
            ]
        ],
        on="Product_ID",
        how="left"
    )

    product_performance["Revenue"] = (
        product_performance["Quantity_Sold"]
        * product_performance["Price"]
    )

    product_performance = product_performance.sort_values(
        "Revenue",
        ascending=False
    )

    st.dataframe(
        product_performance[
            [
                "Product_ID",
                "Product_Name",
                "Category",
                "Price",
                "Rating",
                "Purchase_Count",
                "Quantity_Sold",
                "Revenue"
            ]
        ].head(20),
        use_container_width=True
    )

    # --------------------------------------------------
    # SEGMENT BUSINESS INSIGHTS
    # --------------------------------------------------

    st.markdown("---")

    st.subheader("📊 Segment Business Insights")

    segment_insights = (
        segmented_customers
        .groupby("Segment")
        .agg(
            Customers=("Customer_ID", "count"),
            Avg_Purchases=("Purchase_Frequency", "mean"),
            Avg_Spending=("Total_Spending", "mean"),
            Avg_Order_Value=("Average_Order_Value", "mean"),
            Avg_Recency=("Days_Since_Last_Purchase", "mean")
        )
        .reset_index()
    )

    segment_insights["Avg_Purchases"] = (
        segment_insights["Avg_Purchases"].round(2)
    )

    segment_insights["Avg_Spending"] = (
        segment_insights["Avg_Spending"].round(2)
    )

    segment_insights["Avg_Order_Value"] = (
        segment_insights["Avg_Order_Value"].round(2)
    )

    segment_insights["Avg_Recency"] = (
        segment_insights["Avg_Recency"].round(2)
    )

    st.dataframe(
        segment_insights,
        use_container_width=True
    )
    
    # --------------------------------------------------
# LOAD LIVE CUSTOMER ACTIVITY
# --------------------------------------------------

connection = get_connection()

activity_df = pd.read_sql_query(
    """
    SELECT
        customer_id,
        activity_type,
        product_id,
        search_query,
        activity_date
    FROM user_activity
    ORDER BY activity_date DESC
    """,
    connection
)

connection.close()


# --------------------------------------------------
# LIVE ACTIVITY SUMMARY
# --------------------------------------------------

st.markdown("---")

st.subheader("⚡ Live Activity Summary")

if activity_df.empty:

    st.info(
        "No live customer activity yet."
    )

else:

    activity_counts = (
        activity_df["activity_type"]
        .value_counts()
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "👀 Views",
            activity_counts.get(
                "VIEW_PRODUCT",
                0
            )
        )

    with col2:

        st.metric(
            "🔍 Searches",
            activity_counts.get(
                "SEARCH",
                0
            )
        )

    with col3:

        st.metric(
            "❤️ Wishlist",
            activity_counts.get(
                "WISHLIST",
                0
            )
        )

    with col4:

        st.metric(
            "🛒 Cart",
            activity_counts.get(
                "CART",
                0
            )
        )

    with col5:

        st.metric(
            "🛍️ Purchases",
            activity_counts.get(
                "PURCHASE",
                0
            )
        )

    st.bar_chart(
        activity_counts
    )


# --------------------------------------------------
# LIVE CUSTOMER ACTIVITY
# --------------------------------------------------

st.subheader("🔥 Live Customer Activity")

if activity_df.empty:

    st.info(
        "No live customer activity yet."
    )

else:

    st.dataframe(
        activity_df,
        use_container_width=True,
        hide_index=True
    )


# --------------------------------------------------
# CUSTOMER EXPLORER
# --------------------------------------------------

st.markdown("---")

st.subheader("🔎 Customer Explorer")

selected_admin_customer = st.selectbox(
    "Select a customer",
    customers["Customer_ID"].tolist(),
    key="admin_customer_selector"
)

if selected_admin_customer:

    selected_customer = customers[
        customers["Customer_ID"] == selected_admin_customer
    ].iloc[0]

    customer_segment = segmented_customers[
        segmented_customers["Customer_ID"]
        == selected_admin_customer
    ]

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Purchases",
            int(
                selected_customer[
                    "Purchase_Frequency"
                ]
            )
        )

    with col2:

        st.metric(
            "Total Spending",
            f"₹{selected_customer['Total_Spending']:,.0f}"
        )

    with col3:

        st.metric(
            "Average Order",
            f"₹{selected_customer['Average_Order_Value']:,.0f}"
        )

    with col4:

        if not customer_segment.empty:

            st.metric(
                "Segment",
                customer_segment.iloc[0]["Segment"]
            )

    # --------------------------------------------------
    # CUSTOMER PREFERENCES
    # --------------------------------------------------

    st.write(
        "### 🧠 Customer Preferences"
    )

    preference_result = get_customer_preferences(
        selected_admin_customer,
        purchases,
        products
    )

    if preference_result:

        preferences = (
            preference_result["preferences"]
        )

        strengths = (
            preference_result["strength"]
        )

        preference_df = pd.DataFrame({
            "Attribute": list(
                preferences.keys()
            ),

            "Preferred Value": list(
                preferences.values()
            ),

            "Strength": [
                f"{strengths[key] * 100:.0f}%"
                for key in preferences.keys()
            ]
        })

        st.dataframe(
            preference_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No purchase preferences available."
        )


    # --------------------------------------------------
    # CUSTOMER RECENT ACTIVITY
    # --------------------------------------------------

    st.write(
        "### ⚡ Recent Activity"
    )

    customer_activity = activity_df[
        activity_df["customer_id"]
        == selected_admin_customer
    ]

    if customer_activity.empty:

        st.info(
            "No live activity for this customer."
        )

    else:

        st.dataframe(
            customer_activity.head(20),
            use_container_width=True,
            hide_index=True
        )
        
# --------------------------------------------------
# WISHLIST PAGE
# --------------------------------------------------

if st.session_state.current_page == "wishlist":

    st.title("❤️ My Wishlist")

    if not st.session_state.customer_id:
        st.info("Select a customer to view your wishlist.")

    else:
        wishlist_ids = get_wishlist(
            st.session_state.customer_id
        )

        if not wishlist_ids:
            st.info("Your wishlist is empty.")

        else:
            wishlist_products = products[
                products["Product_ID"].isin(wishlist_ids)
            ]

            st.write(
                f"{len(wishlist_products)} products in your wishlist"
            )

            for _, product in wishlist_products.iterrows():

                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    st.image(
                        product["Image_URL"],
                        use_container_width=True
                    )

                with col2:
                    st.subheader(product["Product_Name"])
                    st.write(f"⭐ {product['Rating']}")
                    st.write(f"₹{product['Price']}")

                with col3:

                    if st.button(
                        "View Product",
                        key=f"wishlist_view_{product['Product_ID']}"
                    ):
                        st.session_state.selected_product = (
                            product["Product_ID"]
                        )
                        st.session_state.current_page = "home"
                        st.rerun()

                    if st.button(
                        "💔 Remove",
                        key=f"wishlist_remove_{product['Product_ID']}"
                    ):
                        remove_from_wishlist(
                            st.session_state.customer_id,
                            product["Product_ID"]
                        )

                        st.success("Removed from wishlist.")
                        st.rerun()

# --------------------------------------------------
# PRODUCT DETAIL PAGE
# --------------------------------------------------

if st.session_state.selected_product:

    product = get_product_by_id(
        products,
        st.session_state.selected_product
    )

        # Record product view
    if (
        product is not None
        and st.session_state.customer_id
    ):

        record_activity(
            st.session_state.customer_id,
            "VIEW_PRODUCT",
            product["Product_ID"]
        )
        
    if product is not None:

        if st.button("← Back to Shopping"):

            st.session_state.selected_product = None

            st.rerun()

        st.divider()

        col1, col2 = st.columns(
            [1, 1]
        )

        with col1:

            st.image(
                product["Image_URL"],
                width="stretch"
            )

        with col2:

            st.title(
                product["Product_Name"]
            )

            st.write(
                f"⭐ **{product['Rating']:.1f} / 5**"
            )

            st.write(
                f"# ₹{product['Price']:,.0f}"
            )

            st.write(
                product["Description"]
            )

            st.divider()

            st.subheader(
                "Product Details"
            )

            st.write(
                f"**Category:** "
                f"{product['Category']}"
            )

            st.write(
                f"**Subcategory:** "
                f"{product['Subcategory']}"
            )

            st.write(
                f"**Fit:** "
                f"{product['Fit']}"
            )

            st.write(
                f"**Color:** "
                f"{product['Color']}"
            )

            st.write(
                f"**Pattern:** "
                f"{product['Pattern']}"
            )

            st.write(
                f"**Material:** "
                f"{product['Material']}"
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                # --------------------------------------------------
                # WISHLIST
                # --------------------------------------------------

                if st.session_state.customer_id:

                    wishlist_products = get_wishlist(
                        st.session_state.customer_id
                    )

                    if product["Product_ID"] in wishlist_products:

                        if st.button(
                            "💔 Remove from Wishlist",
                            use_container_width=True
                        ):

                            remove_from_wishlist(
                                st.session_state.customer_id,
                                product["Product_ID"]
                            )

                            st.success(
                                "Removed from your wishlist."
                            )

                            st.rerun()

                    else:

                        if st.button(
                            "❤️ Add to Wishlist",
                            use_container_width=True
                        ):

                            add_to_wishlist(
                                st.session_state.customer_id,
                                product["Product_ID"]
                            )
                            
                            record_activity(
                                st.session_state.customer_id,
                                "WISHLIST",
                                product["Product_ID"]
                            )    
                            
                            st.success(
                                "Added to your wishlist!"
                            )

                            st.rerun()

                else:

                    st.info(
                        "Select a customer to use the wishlist."
                    )

            with col2:

                # --------------------------------------------------
                # ADD TO CART
                # --------------------------------------------------

                if st.session_state.customer_id:

                    if st.button(
                        "🛒 Add to Cart",
                        use_container_width=True
                    ):

                        add_to_cart(
                            st.session_state.customer_id,
                            product["Product_ID"]
                        )

                        record_activity(
                            st.session_state.customer_id,
                            "CART",
                            product["Product_ID"]
                        )
                        
                        st.success(
                            "Added to your cart! 🛒"
                        )

                else:

                    st.info(
                        "Select a customer to add products to cart."
                    )

    else:

        st.error(
            "Product not found."
        )

    st.stop()

# --------------------------------------------------
# ORDER SUCCESS PAGE
# --------------------------------------------------

if st.session_state.current_page == "order_success":

    st.title("🎉 Order Confirmed!")

    st.success(
        "Your order has been placed successfully."
    )

    st.write(
        f"### Order #{st.session_state.order_id}"
    )

    st.write(
        f"**Order Total:** "
        f"₹{st.session_state.order_total:,.0f}"
    )

    st.write(
        "Thank you for shopping with us! 🛍️"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🛍️ Continue Shopping",
            use_container_width=True
        ):

            st.session_state.current_page = "home"
            st.session_state.order_id = None
            st.session_state.order_total = 0

            st.rerun()

    with col2:

        if st.button(
            "📦 View My Orders",
            use_container_width=True
        ):

            st.session_state.current_page = "orders"

            st.rerun()

    st.stop()
    
# --------------------------------------------------
# AI FASHION SEARCH
# --------------------------------------------------

if st.session_state.customer_id:

    st.divider()

    st.header("🤖 What are you looking for?")

    st.write(
        "Describe what you want in natural language "
        "and we'll find the best matches for you."
    )

    ai_search = st.text_input(
        "Describe your clothing needs",
        placeholder=(
            "Example: I need a slim-fit blue shirt "
            "under ₹1200 for college"
        ),
        key="ai_fashion_search"
    )

    if st.button(
        "✨ Find My Products",
        use_container_width=True
    ):

        if not ai_search.strip():

            st.warning(
                "Please describe what you're looking for."
            )

        else:

            requirements = parse_user_query(
                ai_search
            )

            st.write("### 🔎 Understanding your request")

            display_requirements = {
                key: value
                for key, value in requirements.items()
                if value is not None
            }

            if display_requirements:

                st.json(
                    display_requirements
                )

            recommendations = recommend_products(
                st.session_state.customer_id,
                purchases,
                products,
                top_n=6,
                user_requirements=requirements
            )

            st.write(
                "### 👕 Best Matches"
            )

            if recommendations.empty:

                st.warning(
                    "No products matched your request."
                )

            else:

                recommendation_columns = st.columns(3)

                for index, (_, product) in enumerate(
                    recommendations.iterrows()
                ):

                    with recommendation_columns[
                        index % 3
                    ]:

                        st.image(
                            product["Image_URL"],
                            width="stretch"
                        )

                        st.write(
                            f"**{product['Product_Name']}**"
                        )

                        st.write(
                            f"⭐ {product['Rating']:.1f}"
                        )

                        st.write(
                            f"### ₹{product['Price']:,.0f}"
                        )

                        st.caption(
                            product["Match_Type"]
                        )

                        if st.button(
                            "View Details",
                            key=(
                                f"ai_view_"
                                f"{product['Product_ID']}"
                            ),
                            use_container_width=True
                        ):

                            st.session_state.selected_product = (
                                product["Product_ID"]
                            )

                            st.rerun()
                            

# --------------------------------------------------
# SEARCH
# --------------------------------------------------

with st.form("search_form"):

    search_query = st.text_input(
        "🔍 Search for clothes",
        placeholder=(
            "Try: white shirt, blue jeans, "
            "slim fit, dress..."
        ),
        value=st.session_state.get(
            "active_search",
            ""
        )
    )

    search_submitted = st.form_submit_button(
        "🔍 Search",
        use_container_width=True
    )


if search_submitted:

    st.session_state.active_search = (
        search_query.strip()
    )

    if search_query.strip():

        if st.session_state.customer_id:

            record_activity(
                st.session_state.customer_id,
                "SEARCH",
                search_query=search_query.strip()
            )

        st.rerun()


# --------------------------------------------------
# SEARCH RESULTS
# --------------------------------------------------

active_search = st.session_state.get(
    "active_search",
    ""
)

if active_search:

    search_results = search_products(
        products,
        active_search
    )

    st.subheader(
        f"🔎 Results for: {active_search}"
    )

    if search_results.empty:

        st.warning(
            "No products found. Try another search."
        )

    else:

        st.write(
            f"**{len(search_results)} products found**"
        )

        # Keep your existing product-display code
        # below this section.

# --------------------------------------------------
# RECORD SEARCH ACTIVITY
# --------------------------------------------------

if (
    search_query
    and st.session_state.customer_id
):

    if (
        "last_recorded_search"
        not in st.session_state
        or
        st.session_state.last_recorded_search
        != search_query
    ):

        record_activity(
            st.session_state.customer_id,
            "SEARCH",
            search_query=search_query
        )

        st.session_state.last_recorded_search = (
            search_query
        )


# --------------------------------------------------
# CATEGORY FILTER
# --------------------------------------------------

categories = [
    "All",
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

selected_category = st.selectbox(
    "👕 Category",
    categories
)


# --------------------------------------------------
# FILTER PRODUCTS
# --------------------------------------------------

filtered_products = get_all_products(
    products
)


if selected_category != "All":

    filtered_products = filter_by_category(
        filtered_products,
        selected_category
    )


if search_query:

    filtered_products = search_products(
        filtered_products,
        search_query
    )

# --------------------------------------------------
# PERSONALIZED RECOMMENDATIONS
# --------------------------------------------------

if st.session_state.customer_id:

    st.divider()

    st.header("✨ Recommended for You")

    try:

        recommendations = recommend_products(
            st.session_state.customer_id,
            purchases,
            products,
            top_n=6
        )

        if recommendations.empty:

            st.info(
                "No personalized recommendations "
                "are currently available."
            )

        else:

            st.write(
                "Based on your previous shopping behavior "
                "and learned fashion preferences."
            )

            recommendation_columns = st.columns(3)

            for index, (_, product) in enumerate(
                recommendations.iterrows()
            ):

                with recommendation_columns[index % 3]:

                    st.image(
                        product["Image_URL"],
                        width="stretch"
                    )

                    st.write(
                        f"**{product['Product_Name']}**"
                    )

                    st.write(
                        f"⭐ {product['Rating']:.1f}"
                    )

                    st.write(
                        f"### ₹{product['Price']:,.0f}"
                    )

                    st.caption(
                        product["Match_Type"]
                    )

                    if st.button(
                        "View Details",
                        key=(
                            f"recommend_"
                            f"{product['Product_ID']}"
                        ),
                        use_container_width=True
                    ):

                        st.session_state.selected_product = (
                            product["Product_ID"]
                        )

                        st.rerun()

    except Exception as error:

        st.error(
            f"Recommendation error: {error}"
        )
        
# --------------------------------------------------
# AI FASHION ASSISTANT
# --------------------------------------------------

st.markdown("---")

st.header("🤖 AI Fashion Assistant")

ai_question = st.text_input(
    "Ask me anything about your fashion needs",
    placeholder=(
        "Example: What should I wear for college?"
    ),
    key="ai_assistant_question"
)

if st.button(
    "✨ Ask AI",
    use_container_width=True
):

    if not st.session_state.customer_id:

        st.info(
            "Select a customer first so the AI can "
            "personalize its answer."
        )

    elif not ai_question.strip():

        st.warning("Please enter a question.")

    else:

        profile = get_customer_profile(
        st.session_state.customer_id,
        customers,
        purchases,
        products
    )

    with st.spinner("AI is thinking..."):

        response = ask_customer_assistant(
            profile,
            ai_question,
            recommendations
        )

        st.markdown("### 🤖 AI Recommendation")
        st.write(response)
# --------------------------------------------------
# PRODUCT COUNT
# --------------------------------------------------

st.write(
    f"### {len(filtered_products)} products found"
)


# --------------------------------------------------
# PRODUCT GRID
# --------------------------------------------------

display_products = filtered_products.head(30)

columns = st.columns(5)


for index, (_, product) in enumerate(
    display_products.iterrows()
):

    with columns[index % 5]:

        st.image(
            product["Image_URL"],
            width="stretch"
        )

        st.write(
            f"**{product['Product_Name']}**"
        )

        st.write(
            f"⭐ {product['Rating']:.1f}"
        )

        st.write(
            f"### ₹{product['Price']:,.0f}"
        )

        if st.button(
            "View Details",
            key=f"view_{product['Product_ID']}",
            use_container_width=True
        ):

            st.session_state.selected_product = (
                product["Product_ID"]
            )

            st.rerun()