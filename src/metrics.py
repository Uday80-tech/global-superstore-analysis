import pandas as pd
from typing import Dict, Any

def calculate_total_sales(df: pd.DataFrame) -> float:
    """Calculates total sales revenue."""
    return float(df['sales'].sum()) if not df.empty else 0.0


def calculate_total_profit(df: pd.DataFrame) -> float:
    """Calculates total net profit."""
    return float(df['profit'].sum()) if not df.empty else 0.0


def calculate_profit_margin(df: pd.DataFrame) -> float:
    """
    Calculates overall profit margin percentage:
    (Total Profit / Total Sales) * 100
    """
    if df.empty:
        return 0.0
    sales = float(df['sales'].sum())
    profit = float(df['profit'].sum())
    return (profit / sales * 100) if sales > 0 else 0.0


def calculate_total_orders(df: pd.DataFrame) -> int:
    """
    Calculates total orders using unique order_id count
    consistent with Notebook 03.
    """
    return int(df['order_id'].nunique()) if not df.empty else 0


def calculate_total_customers(df: pd.DataFrame) -> int:
    """
    Calculates total customers using unique customer_id count
    consistent with Notebook 03.
    """
    return int(df['customer_id'].nunique()) if not df.empty else 0


def calculate_aov(df: pd.DataFrame) -> float:
    """
    Calculates Average Order Value (AOV):
    Total Sales / Unique Orders
    """
    if df.empty:
        return 0.0
    sales = float(df['sales'].sum())
    orders = int(df['order_id'].nunique())
    return (sales / orders) if orders > 0 else 0.0


def calculate_total_quantity(df: pd.DataFrame) -> int:
    """Calculates total units sold."""
    return int(df['quantity'].sum()) if not df.empty else 0


def calculate_loss_orders_count(df: pd.DataFrame) -> int:
    """Calculates number of unprofitable order line items."""
    return int((df['profit'] < 0).sum()) if not df.empty else 0


def get_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Aggregates all executive KPIs into a dictionary.
    """
    return {
        "total_sales": calculate_total_sales(df),
        "total_profit": calculate_total_profit(df),
        "profit_margin": calculate_profit_margin(df),
        "total_orders": calculate_total_orders(df),
        "total_customers": calculate_total_customers(df),
        "aov": calculate_aov(df),
        "total_quantity": calculate_total_quantity(df),
        "loss_orders_count": calculate_loss_orders_count(df)
    }

# Alias for backward compatibility
compute_executive_kpis = get_executive_kpis


def format_currency(value: float) -> str:
    """Formats numeric value as USD currency with compact notation for M/K."""
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    elif abs(value) >= 1_000:
        return f"${value / 1_000:,.1f}K"
    else:
        return f"${value:,.2f}"


def format_number(value: int | float) -> str:
    """Formats integers/floats with comma separators or compact M/K."""
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:,.2f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:,.1f}K"
    else:
        return f"{value:,.0f}"
