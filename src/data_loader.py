import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_superstore_data() -> pd.DataFrame:
    """
    Loads and preprocesses the cleaned Global Superstore dataset.
    Cached for fast multi-page performance.
    """
    # Determine base directory dynamically
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))
    data_path = os.path.join(project_root, "Data", "cleaned_superstore_data.csv")
    
    if not os.path.exists(data_path):
        # Fallback to local Data path
        data_path = os.path.join("Data", "cleaned_superstore_data.csv")

    df = pd.read_csv(data_path)
    
    # 1. Parse dates to standard datetime
    df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['ship_date'] = pd.to_datetime(df['ship_date'], errors='coerce')
    
    # 2. Preprocess delivery days duration
    if 'delivery_days' not in df.columns:
        df['delivery_days'] = (df['ship_date'] - df['order_date']).dt.days
    
    # 3. Ensure profit margin consistency (Percentage: Profit / Sales * 100)
    df['profit_margin'] = (df['profit'] / df['sales']) * 100
    
    # 4. Ensure order_year exists
    if 'order_year' not in df.columns:
        df['order_year'] = df['order_date'].dt.year

    return df
