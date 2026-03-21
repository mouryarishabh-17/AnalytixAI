import pandas as pd
from utils.logger import logger

def clean_finance_data(df):
    """
    Cleans and prepares finance data for analytics and ML.
    """
    logger.info("Finance cleaning started")
    summary = {}

    # Standardize column names (Cast to str to handle numeric headers)
    df.columns = [str(col).strip().title() for col in df.columns]

    # Handle Date column
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Convert numeric columns
    numeric_cols = ["Income", "Expense", "Profit"]
    converted = []

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            converted.append(col)

    summary["numeric_columns_converted"] = converted

    # Handle missing values
    missing_before = int(df.isnull().sum().sum())
    df = df.ffill()
    missing_after = int(df.isnull().sum().sum())

    summary["missing_values_filled"] = missing_before - missing_after

    # Compute Profit if missing
    if "Profit" not in df.columns and {"Income", "Expense"}.issubset(df.columns):
        df["Profit"] = df["Income"] - df["Expense"]
        summary["profit_computed"] = True
    else:
        summary["profit_computed"] = False

    # Remove invalid rows
    if "Expense" in df.columns:
        df = df[df["Expense"] >= 0]

    logger.info("Finance cleaning completed")
    return df, summary
