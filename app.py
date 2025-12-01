import streamlit as st
import pandas as pd
from datetime import datetime
import os
from html import escape
from vehicles import registration_numbers

# --- Constants ---
DATA_FILE = "fuel_register.csv"
PRODUCTS = ["Diesel", "Premium", "Lubricants", "Puncture"]
FONT_SIZE = 18
FONT_SIZE_TITLE = 50

# --- Initialize CSV ---
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=[
        "Driver Name", "Date", "Receipt No", "Registration No", "Product", "Quantity", "Amount",
        "Previous Km", "Current Km", "Distance", "Receipt Image"
    ])
    df_init.to_csv(DATA_FILE, index=False)

# --- Page Configuration ---
st.set_page_config(page_title="Fuel Register", page_icon="⛽", layout="wide")

# --- Global CSS Styling moved to st.html ---
st.html(f"""
<style>
/* General App Styling */
div[data-testid="stApp"] * {{
    font-size: {FONT_SIZE}px !important;
    box-sizing: border-box;
}}

/* Title Styling */
div[data-testid="stApp"] h1 {{
    font-size: clamp(32px, 6vw, {FONT_SIZE_TITLE}px) !important;
    font-weight: 900 !important;
    margin-bottom: 0.3rem;
}}

/* Polished Section Headers */
h2, h3 {{
    font-weight: 800 !important;
    padding-top: 1rem;
}}

/* Table improvements */
.stDataFrame [data-testid="stTable"] td, 
.stDataFrame [data-testid="stTable"] th {{
    font-size: {FONT_SIZE - 2}px !important;
    white-space: nowrap;
    padding: 6px 10px !important;
}}

/* File uploader and labels */
label {{
    font-weight: 900 !important;
}}

/* Responsive Images */
img {{
    max-width: 100%;
    height: auto;
    display: block;
}}

/* Primary Button Coloring */
.stForm button[kind="primaryFormSubmit"] {{
    background-color: #005bbb !important;
    color: white !important;
    border-radius: 10px;
}}
.stForm button[kind="primaryFormSubmit"]:hover {{
    background-color: #004999 !important;
}}

/* Hide "Press Enter to submit form" instructions */
.stForm [data-testid="InputInstructions"] {{
    display: none !important;
}}

/* Preview boxes */
.preview-box {{
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    margin: 0.45rem 0 0.75rem 0;
    font-size: 0.95rem;
    line-height: 1.25;
}}
.preview-info {{ background: #e8f4ff; color: #0747a6; }}
.preview-success {{ background: #e6ffed; color: #05612a; }}
.preview-warning {{ background: #fff4e5; color: #8a4b00; }}
</style>
""")

def render_preview(label: str, value, variant: str = "info"):
    """Render a safe HTML preview box."""
    safe_label = escape(str(label))
    safe_value = escape("" if value is None else str(value))
    cls = "preview-info"
    if variant == "success":
        cls = "preview-success"
    elif variant == "warning":
        cls = "preview-warning"

    html = f"<div class='preview-box {cls}'><strong>{safe_label}</strong>: {safe_value}</div>"
    st.markdown(html, unsafe_allow_html=True)

# --- Title ---
st.title("Fuel Register")

# Check submission flag
if "submission_complete" in st.session_state and st.session_state.submission_complete:
    st.subheader("✅ Submitted Successfully!")
    st.write("Your fuel entry has been recorded.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Submit Another Receipt", type="primary", use_container_width=True):
            st.session_state.submission_complete = False
            st.rerun()
    
    st.stop()

# --- Add Fuel Entry ---
st.header("Add Fuel Entry")

col1, col2 = st.columns(2)

with col1:
    driver_name = st.text_input("Driver's Name [Full Name] *", key="driver_name")
    if driver_name:
        render_preview("Driver", driver_name)

    date_value = st.date_input("Date of Receipt *", value=datetime.today().date(), key="date_value")
    render_preview("Date", date_value.strftime('%B %d, %Y'))

    receipt_no = st.text_input("Receipt No *", placeholder="Enter receipt number", key="receipt_no")
    if receipt_no:
        render_preview("Receipt No", receipt_no)

    product = st.selectbox("Product *", ["Select product"] + PRODUCTS, key="product")
    if product != "Select product":
        render_preview("Product", product, "success")

    quantity = st.number_input("Quantity (Litres)", min_value=0, key="quantity")
    if quantity > 0:
        render_preview("Quantity", f"{quantity} litres")

with col2:
    vehicle_options = ["Select Vehicle Reg Number..."] + registration_numbers
    motor_vehicle = st.selectbox("Vehicle Reg No *", vehicle_options, key="motor_vehicle")
    if not motor_vehicle.startswith("Select"):
        render_preview("Vehicle", motor_vehicle, "success")

    amount = st.number_input("Amount (Currency) *", min_value=0, key="amount")
    if amount > 0:
        render_preview("Amount", f"{amount:,.2f}")

    previous_km = st.number_input("Previous Kilometers", min_value=0, key="previous_km")
    if previous_km > 0:
        render_preview("Start", f"{previous_km:,} km")

    current_km = st.number_input("Current Kilometers", min_value=0, key="current_km")
    if current_km > 0:
        render_preview("End", f"{current_km:,} km")

    if previous_km > 0 and current_km > 0:
        if current_km < previous_km:
            st.error("⚠️ Current km must be greater than previous km")
        else:
            render_preview("Distance", f"{current_km - previous_km} km", "success")

    receipt_image = st.file_uploader("Upload Receipt Image", type=["png", "jpg", "jpeg", "pdf"], key="receipt_image")
    if receipt_image:
        render_preview("Receipt Image", receipt_image.name)

col_btn1, col_btn2 = st.columns([3, 1])
with col_btn2:
    submit = st.button("Add Entry", type="primary", use_container_width=True)

if submit:
    errors = []

    if motor_vehicle.startswith("Select"):
        errors.append("Vehicle registration number is required.")
    if product == "Select product":
        errors.append("Please select a product type.")
    if not driver_name:
        errors.append("Driver name is required.")
    if not receipt_no:
        errors.append("Receipt number is required.")
    if current_km < previous_km:
        errors.append("Current kilometers cannot be less than previous kilometers.")

    if errors:
        for err in errors:
            st.error(f"⚠️ {err}")
    else:
        distance = current_km - previous_km

        @st.dialog("⚠️ Confirm Entry Details")
        def confirm_submission():
            st.write("Review before submitting:")
            render_preview("Driver", driver_name)
            render_preview("Date", date_value.strftime('%B %d, %Y'))
            render_preview("Receipt No", receipt_no)
            render_preview("Vehicle", motor_vehicle, "success")
            render_preview("Product", product, "success")
            render_preview("Quantity", f"{quantity} litres")
            render_preview("Amount", f"{amount:,.2f}")
            render_preview("Distance", f"{distance} km", "success")
            if receipt_image:
                render_preview("Receipt Image", receipt_image.name)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Confirm & Submit", type="primary", use_container_width=True):

                    image_path = ""
                    if receipt_image:
                        os.makedirs("receipts", exist_ok=True)
                        image_path = os.path.join("receipts", f"{receipt_no}_{receipt_image.name}")
                        with open(image_path, "wb") as f:
                            f.write(receipt_image.getbuffer())

                    new_row = pd.DataFrame([{
                        "Driver Name": driver_name,
                        "Date": date_value.isoformat(),
                        "Receipt No": receipt_no,
                        "Registration No": motor_vehicle,
                        "Product": product,
                        "Quantity": quantity,
                        "Amount": amount,
                        "Previous Km": previous_km,
                        "Current Km": current_km,
                        "Distance": distance,
                        "Receipt Image": image_path
                    }])

                    df = pd.read_csv(DATA_FILE)
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_csv(DATA_FILE, index=False)

                    st.session_state.submission_complete = True
                    st.rerun()

            with col2:
                if st.button("✗ Cancel", use_container_width=True):
                    st.rerun()

        confirm_submission()

# --- Entries Viewer ---
df = pd.read_csv(DATA_FILE)
total_entries = len(df)

st.header(f"Fuel Entries ({total_entries} total)")

display_columns = ["Receipt No", "Registration No", "Driver Name", "Date"]

col_filter, col_clear = st.columns([4, 1])
with col_filter:
    driver_filter = st.text_input("🔍 Filter by Driver Name:", placeholder="Type driver name...")
with col_clear:
    if driver_filter:
        if st.button("Clear", use_container_width=True):
            st.rerun()

if driver_filter:
    filtered = df[df["Driver Name"].str.contains(driver_filter, case=False, na=False)]
    st.caption(f"Showing {len(filtered)} of {total_entries} entries")
    st.dataframe(filtered[display_columns].sort_values("Date", ascending=False),
                 hide_index=True, use_container_width=True)
else:
    st.dataframe(df[display_columns].sort_values("Date", ascending=False),
                 hide_index=True, use_container_width=True)
