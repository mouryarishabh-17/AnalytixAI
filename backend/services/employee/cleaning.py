import pandas as pd
from utils.logger import logger

def clean_employee_data(df):
    logger.info("Employee data cleaning started")

    df = df.copy()
    df.drop_duplicates(inplace=True)

    # Fill missing values safely
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")

    for col in df.select_dtypes(include="number").columns:
        df[col] = df[col].fillna(df[col].mean())

    logger.info("Employee data cleaning completed")
    return df, {"rows_after_cleaning": int(len(df))}
