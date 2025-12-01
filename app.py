import streamlit as st
import pandas as pd
from datetime import datetime
import os
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

# --- Global CSS Styling ---
st.markdown(f"""
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
</style>
""", unsafe_allow_html=True)

# --- Title ---
st.title("Fuel Register")

# Check if submission was just completed
if "submission_complete" in st.session_state and st.session_state.submission_complete:
    st.success("## ✅ Submitted Successfully!")
    st.write("")
    st.write("Your fuel entry has been recorded.")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Submit Another Receipt", type="primary", use_container_width=True):
            # Clear the submission flag and rerun
            st.session_state.submission_complete = False
            st.rerun()
    
    st.stop()  # Stop rendering the rest of the page

# --- Add Fuel Entry ---
st.header("Add Fuel Entry")

col1, col2 = st.columns(2)

with col1:
    driver_name = st.text_input("Driver's Name [Full Name] *", key="driver_name")
    if driver_name:
        st.info(f"👤 {driver_name}")
    
    date_value = st.date_input(
        "Date of Receipt *", value=datetime.today().date(), key="date_value")
    st.info(f"📅 {date_value.strftime('%B %d, %Y')}")
    
    receipt_no = st.text_input(
        "Receipt No *", placeholder="Enter receipt number", key="receipt_no")
    if receipt_no:
        st.info(f"🧾 Receipt #{receipt_no}")
    
    product = st.selectbox("Product *", ["Select product"] + PRODUCTS, key="product")
    
    # Immediate visual feedback for product selection
    if product != "Select product":
        st.success(f"✓ {product}")
    
    quantity = st.number_input("Quantity (Litres)", min_value=0, key="quantity")
    if quantity > 0:
        st.info(f"⛽ {quantity} litres")

with col2:
    vehicle_options = [
        "Select Vehicle Reg Number..." ] + registration_numbers
    motor_vehicle = st.selectbox("Vehicle Reg No *", vehicle_options, key="motor_vehicle")
    
    # Immediate visual feedback for vehicle selection
    if not motor_vehicle.startswith("Select"):
        st.success(f"✓ {motor_vehicle}")
    
    amount = st.number_input("Amount (Currency) *", min_value=0, key="amount")
    if amount > 0:
        st.info(f"💰 {amount:,.2f}")
    
    previous_km = st.number_input("Previous Kilometers", min_value=0, key="previous_km")
    if previous_km > 0:
        st.info(f"📍 Start: {previous_km:,} km")
    
    current_km = st.number_input("Current Kilometers", min_value=0, key="current_km")
    if current_km > 0:
        st.info(f"📍 End: {current_km:,} km")
    
    # Inline validation for kilometers
    if previous_km > 0 and current_km > 0:
        if current_km < previous_km:
            st.error("⚠️ Current km must be greater than previous km")
        elif current_km > previous_km:
            distance_preview = current_km - previous_km
            st.info(f"📏 Distance: {distance_preview} km")
    
    receipt_image = st.file_uploader(
        "Upload Receipt Image",
        type=["png", "jpg", "jpeg", "pdf"],
        help="Upload a clear picture or PDF of the fuel receipt.",
        key="receipt_image"
    )
    if receipt_image:
        st.info(f"📎 {receipt_image.name}")

# Submit button outside form for immediate feedback
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
        errors.append(
            "Current kilometers cannot be less than previous kilometers.")

    if errors:
        for err in errors:
            st.error(f"⚠️ {err}")
    else:
        distance = current_km - previous_km
        
        # Show confirmation dialog
        @st.dialog("⚠️ Confirm Entry Details")
        def confirm_submission():
            st.write("Please review your entry before submitting:")
            st.write("")
            st.info(f"**Driver:** {driver_name}")
            st.info(f"**Date:** {date_value.strftime('%B %d, %Y')}")
            st.info(f"**Receipt No:** {receipt_no}")
            st.info(f"**Vehicle:** {motor_vehicle}")
            st.info(f"**Product:** {product}")
            st.info(f"**Quantity:** {quantity} litres")
            st.info(f"**Amount:** {amount:,.2f}")
            st.info(f"**Distance:** {distance} km (from {previous_km:,} to {current_km:,} km)")
            if receipt_image:
                st.info(f"**Receipt Image:** {receipt_image.name}")
            
            st.write("")
            st.warning("Are all details accurate?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Confirm & Submit", type="primary", use_container_width=True):
                    # Save the entry
                    image_path = ""
                    if receipt_image:
                        os.makedirs("receipts", exist_ok=True)
                        image_path = os.path.join(
                            "receipts", f"{receipt_no}_{receipt_image.name}"
                        )
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

# Filter Area
col_filter, col_clear = st.columns([4, 1])
with col_filter:
    driver_filter = st.text_input("🔍 Filter by Driver Name:", placeholder="Type driver name...")
with col_clear:
    if driver_filter:
        st.write("")
        st.write("")
        if st.button("Clear", use_container_width=True):
            st.rerun()

if driver_filter:
    filtered = df[df["Driver Name"].str.contains(driver_filter, case=False, na=False)]
    st.caption(f"Showing {len(filtered)} of {total_entries} entries")
    st.dataframe(filtered[display_columns].sort_values(
        "Date", ascending=False), hide_index=True, use_container_width=True)
else:
    st.dataframe(df[display_columns].sort_values(
        "Date", ascending=False), hide_index=True, use_container_width=True)
