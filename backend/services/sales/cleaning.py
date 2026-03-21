import pandas as pd
from utils.logger import logger


def clean_sales_data(df):
    summary = {}
    logger.info("Sales cleaning started")

    missing_before = int(df.isnull().sum().sum())
    df = df.ffill()
    missing_after = int(df.isnull().sum().sum())
    summary["missing_values_handled"] = missing_before - missing_after

    duplicates_before = int(df.duplicated().sum())
    df.drop_duplicates(inplace=True)
    summary["duplicates_removed"] = duplicates_before

    numeric_cols = ["Sales", "Profit", "Quantity"]
    corrected = []

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            corrected.append(col)

    summary["data_types_corrected"] = corrected

    if "Sales" in df.columns:
        df = df[df["Sales"] >= 0]

    if "Quantity" in df.columns:
        df = df[df["Quantity"] > 0]

    logger.info("Sales cleaning completed")
    return df, summary
