"""
Database configuration and operations for Fuel Register using Supabase.
"""
import os
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

def get_supabase_client() -> Client:
    """
    Initialize and return Supabase client.
    Credentials should be stored in Streamlit secrets or environment variables.
    """
    # Try to get from Streamlit secrets first (for cloud deployment)
    try:
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
    except (FileNotFoundError, KeyError):
        # Fallback to environment variables (for local development)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            st.error("⚠️ Supabase credentials not found. Please configure SUPABASE_URL and SUPABASE_KEY.")
            st.stop()
    
    return create_client(supabase_url, supabase_key)

def create_fuel_entries_table():
    """
    SQL to create the fuel_entries table in Supabase.
    Run this in your Supabase SQL editor:
    
    -- Create the fuel entries table
    CREATE TABLE fuel_entries (
        id BIGSERIAL PRIMARY KEY,
        driver_name TEXT NOT NULL,
        date DATE NOT NULL,
        receipt_no TEXT NOT NULL,
        registration_no TEXT NOT NULL,
        product TEXT NOT NULL,
        quantity NUMERIC DEFAULT 0,
        amount NUMERIC NOT NULL,
        previous_km NUMERIC DEFAULT 0,
        current_km NUMERIC DEFAULT 0,
        distance NUMERIC DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create indexes for faster queries
    CREATE INDEX idx_driver_name ON fuel_entries(driver_name);
    CREATE INDEX idx_date ON fuel_entries(date DESC);
    CREATE INDEX idx_registration_no ON fuel_entries(registration_no);
    
    -- IMPORTANT: Enable Row Level Security and allow public access (no authentication)
    ALTER TABLE fuel_entries ENABLE ROW LEVEL SECURITY;
    
    -- Allow anonymous users to INSERT data
    CREATE POLICY "Allow public insert" ON fuel_entries
        FOR INSERT
        TO anon
        WITH CHECK (true);
    
    -- Allow anonymous users to SELECT (read) data
    CREATE POLICY "Allow public select" ON fuel_entries
        FOR SELECT
        TO anon
        USING (true);
    """
    pass

def insert_fuel_entry(
    driver_name: str,
    date: str,
    receipt_no: str,
    registration_no: str,
    product: str,
    quantity: float,
    amount: float,
    previous_km: float,
    current_km: float,
    distance: float
) -> bool:
    """Insert a new fuel entry into Supabase."""
    try:
        supabase = get_supabase_client()
        
        data = {
            "driver_name": driver_name,
            "date": date,
            "receipt_no": receipt_no,
            "registration_no": registration_no,
            "product": product,
            "quantity": quantity,
            "amount": amount,
            "previous_km": previous_km,
            "current_km": current_km,
            "distance": distance
        }
        
        response = supabase.table("fuel_entries").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error inserting entry: {str(e)}")
        return False

def get_all_fuel_entries() -> pd.DataFrame:
    """Retrieve all fuel entries from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("fuel_entries").select("*").order("date", desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Rename columns to match CSV format
            df = df.rename(columns={
                "driver_name": "Driver Name",
                "date": "Date",
                "receipt_no": "Receipt No",
                "registration_no": "Registration No",
                "product": "Product",
                "quantity": "Quantity",
                "amount": "Amount",
                "previous_km": "Previous Km",
                "current_km": "Current Km",
                "distance": "Distance"
            })
            return df
        else:
            # Return empty DataFrame with proper columns
            return pd.DataFrame(columns=[
                "Driver Name", "Date", "Receipt No", "Registration No", "Product", 
                "Quantity", "Amount", "Previous Km", "Current Km", "Distance"
            ])
    except Exception as e:
        st.error(f"Error retrieving entries: {str(e)}")
        return pd.DataFrame(columns=[
            "Driver Name", "Date", "Receipt No", "Registration No", "Product", 
            "Quantity", "Amount", "Previous Km", "Current Km", "Distance"
        ])

def filter_entries_by_driver(driver_name: str) -> pd.DataFrame:
    """Filter fuel entries by driver name."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("fuel_entries")\
            .select("*")\
            .ilike("driver_name", f"%{driver_name}%")\
            .order("date", desc=True)\
            .execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            df = df.rename(columns={
                "driver_name": "Driver Name",
                "date": "Date",
                "receipt_no": "Receipt No",
                "registration_no": "Registration No",
                "product": "Product",
                "quantity": "Quantity",
                "amount": "Amount",
                "previous_km": "Previous Km",
                "current_km": "Current Km",
                "distance": "Distance"
            })
            return df
        else:
            return pd.DataFrame(columns=[
                "Driver Name", "Date", "Receipt No", "Registration No", "Product", 
                "Quantity", "Amount", "Previous Km", "Current Km", "Distance"
            ])
    except Exception as e:
        st.error(f"Error filtering entries: {str(e)}")
        return pd.DataFrame(columns=[
            "Driver Name", "Date", "Receipt No", "Registration No", "Product", 
            "Quantity", "Amount", "Previous Km", "Current Km", "Distance"
        ])

def get_entry_count() -> int:
    """Get total count of fuel entries."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("fuel_entries").select("id", count="exact").execute()
        return response.count if response.count else 0
    except Exception as e:
        st.error(f"Error getting entry count: {str(e)}")
        return 0
