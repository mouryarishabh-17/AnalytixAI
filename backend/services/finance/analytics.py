import pandas as pd
from utils.logger import logger

def analyze_finance_data(df,):
    """
    Domain-aware finance analytics using schema mapping
    """
    logger.info("📊 Finance analytics started")

    result = {}

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()

    logger.info(f"Detected numeric columns: {numeric_cols}")
    logger.info(f"Detected date columns: {date_cols}")

    # --- INCOME ---
    income_col = next((c for c in numeric_cols if "income" in str(c).lower()), None)
    if income_col:
        logger.info(f"Using income column: {income_col}")
        result["total_income"] = float(df[income_col].sum())
        result["average_income"] = float(df[income_col].mean())

    # --- EXPENSE ---
    expense_col = next((c for c in numeric_cols if "expense" in str(c).lower()), None)
    if expense_col:
        logger.info(f"Using expense column: {expense_col}")
        result["total_expense"] = float(df[expense_col].sum())
        result["average_expense"] = float(df[expense_col].mean())

    # --- PROFIT ---
    profit_col = next(
        (c for c in numeric_cols if "profit" in str(c).lower()), None
    )

    # If profit not present, derive it
    if not profit_col and income_col and expense_col:
        logger.info("Profit column not found, deriving Profit = Income - Expense")
        df["__derived_profit__"] = df[income_col] - df[expense_col]
        profit_col = "__derived_profit__"

    if profit_col:
        logger.info(f"Using profit column: {profit_col}")
        result["total_profit"] = float(df[profit_col].sum())
        result["average_profit"] = float(df[profit_col].mean())

        total_income = df[income_col].sum()
        if total_income != 0 and not pd.isna(total_income):
            result["profit_margin_percent"] = float(
                (df[profit_col].sum() / total_income) * 100
            )

    # --- TREND ANALYSIS ---
    if date_cols and profit_col:
        date_col = date_cols[0]
        logger.info(f"Using date column for trend: {date_col}")

        df_sorted = df.sort_values(date_col)

        if len(df_sorted) >= 2:
            result["profit_trend"] = (
                "increasing"
                if df_sorted[profit_col].iloc[-1] > df_sorted[profit_col].iloc[0]
                else "decreasing"
            )

    if not result:
        logger.info("No specific financial KPIs found, providing basic numeric summary.")
        numeric_cols = df.select_dtypes(include=['number']).columns[:3]
        for col in numeric_cols:
            result[f"avg_{col.lower()}"] = float(df[col].mean())
            result[f"total_{col.lower()}"] = float(df[col].sum())

    logger.info("✅ Finance analytics completed")
    return result
