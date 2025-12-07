import streamlit as st
import pandas as pd
from datetime import datetime
import os
from html import escape
from vehicles import registration_numbers
from drivers import drivers
from db_config import (
    insert_fuel_entry, 
    get_all_fuel_entries, 
    filter_entries_by_driver,
    get_entry_count
)

# --- Constants ---
PRODUCTS = ["Diesel", "Premium", "Lubricants", "Puncture"]
FONT_SIZE = 18
FONT_SIZE_TITLE = 50

# --- Page Configuration ---
st.set_page_config(page_title="Fuel Register", page_icon="⛽", layout="wide")

# --- Global CSS Styling - Simplified for Mobile Compatibility ---
st.markdown(f"""
<style>
/* General App Styling - Simplified */
body {{
    font-size: {FONT_SIZE}px;
}}

/* Title Styling - Using max() instead of clamp() */
h1 {{
    font-size: max(32px, {FONT_SIZE_TITLE}px);
    font-weight: 900;
    margin-bottom: 0.3rem;
}}

/* Section Headers */
h2, h3 {{
    font-weight: 800;
    padding-top: 1rem;
}}

/* Table styling */
table {{
    font-size: {FONT_SIZE - 2}px;
    width: 100%;
}}

td, th {{
    padding: 6px 10px;
}}

/* Labels */
label {{
    font-weight: 900;
}}

/* Responsive Images */
img {{
    max-width: 100%;
    height: auto;
    display: block;
}}

/* Button Styling */
button[kind="primary"] {{
    background-color: #005bbb;
    color: white;
    border-radius: 10px;
    border: none;
}}

/* Preview boxes - Simplified */
.preview-box {{
    padding: 8px 12px;
    border-radius: 8px;
    margin: 8px 0 12px 0;
    font-size: 16px;
    line-height: 1.4;
}}
.preview-info {{ 
    background-color: #e8f4ff; 
    color: #0747a6; 
}}
.preview-success {{ 
    background-color: #e6ffed; 
    color: #05612a; 
}}
.preview-warning {{ 
    background-color: #fff4e5; 
    color: #8a4b00; 
}}
</style>
""", unsafe_allow_html=True)

def render_preview(label: str, value, variant: str = "info"):
    """Render a simple preview box - simplified for mobile compatibility."""
    # Escape special characters
    safe_label = escape(str(label))
    safe_value = escape("" if value is None else str(value))
    
    # Determine CSS class
    cls = "preview-info"
    if variant == "success":
        cls = "preview-success"
    elif variant == "warning":
        cls = "preview-warning"
    
    # Simple HTML structure
    html = f'<div class="preview-box {cls}"><strong>{safe_label}</strong>: {safe_value}</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- Title ---
st.title("Fuel Register")

# Check submission flag
if "show_done_message" not in st.session_state:
    st.session_state.show_done_message = False

if "submission_complete" in st.session_state and st.session_state.submission_complete:
    st.subheader("✅ Submitted Successfully!")
    st.write("Your fuel entry has been recorded.")

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_left:
        if st.button("📝 Submit Another Receipt", key="submit_another", type="primary", width='stretch'):
            st.session_state.submission_complete = False
            st.session_state.show_done_message = False
            st.rerun()

    with col_right:
        if st.button("Done", key="done_btn", width='stretch'):
            st.session_state.show_done_message = True
            st.rerun()

    if st.session_state.show_done_message:
        st.success("Thank you, attach the receipt in the file")

    st.stop()

# --- Add Fuel Entry ---
st.header("Add Fuel Entry")

col1, col2 = st.columns(2)

with col1:
    driver_options = ["Select your name or driver's name..."] + drivers
    driver_name = st.selectbox("Driver's Name *", driver_options, key="driver_name")
    if not driver_name.startswith("Select"):
        render_preview("Driver", driver_name, "success")

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


col_btn1, col_btn2 = st.columns([3, 1])
with col_btn2:
    submit = st.button("Add Entry", type="primary", width='stretch')

if submit:
    errors = []

    if driver_name.startswith("Select"):
        errors.append("Please select your name.")
    if motor_vehicle.startswith("Select"):
        errors.append("Vehicle registration number is required.")
    if product == "Select product":
        errors.append("Please select a product type.")
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

            confirm_data = {
                "Driver": driver_name,
                "Date": date_value.strftime('%B %d, %Y'),
                "Receipt No": receipt_no,
                "Vehicle": motor_vehicle,
                "Product": product,
                "Quantity": f"{quantity} litres",
                "Amount": f"{amount:,.2f}",
                "Distance": f"{distance} km",
            }

            # Display a compact table-like summary (vertical key/value pairs)
            confirm_df = pd.DataFrame.from_dict(confirm_data, orient="index", columns=["Value"])
            st.table(confirm_df)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✓ Confirm & Submit", type="primary", key="confirm_submit"):
                    # Insert into Supabase
                    success = insert_fuel_entry(
                        driver_name=driver_name,
                        date=date_value.isoformat(),
                        receipt_no=receipt_no,
                        registration_no=motor_vehicle,
                        product=product,
                        quantity=quantity,
                        amount=amount,
                        previous_km=previous_km,
                        current_km=current_km,
                        distance=distance,
                    )

                    if success:
                        st.session_state.submission_complete = True
                        st.rerun()
                    else:
                        st.error("Failed to save entry. Please try again.")

            with col2:
                if st.button("✗ Cancel", key="confirm_cancel"):
                    st.rerun()

        confirm_submission()

# --- Entries Viewer ---
total_entries = get_entry_count()

st.header(f"Fuel Entries ({total_entries} total)")

display_columns = ["Date", "Driver Name", "Receipt No", "Registration No", "Product", 
                   "Quantity", "Amount", "Previous Km", "Current Km", "Distance"]

col_filter, col_clear = st.columns([4, 1])
with col_filter:
    driver_filter = st.text_input("🔍 Filter by Driver Name:", placeholder="Type driver name...")
with col_clear:
    if driver_filter:
        if st.button("Clear", width='stretch'):
            st.rerun()

if driver_filter:
    df = filter_entries_by_driver(driver_filter)
    st.caption(f"Showing {len(df)} of {total_entries} entries")
    if len(df) > 0:
        st.dataframe(df[display_columns], hide_index=True, width='stretch')
    else:
        st.info("No entries found for this driver.")
else:
    df = get_all_fuel_entries()
    if len(df) > 0:
        st.dataframe(df[display_columns], hide_index=True, width='stretch')
    else:
        st.info("No fuel entries yet. Add your first entry above!")
