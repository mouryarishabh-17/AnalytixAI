import pandas as pd
from utils.logger import logger

def analyze_schema(df: pd.DataFrame) -> dict:
    """
    Analyze CSV schema and classify columns by role and datatype.
    This is DOMAIN-INDEPENDENT.
    """

    logger.info("📊 Schema analysis started")

    schema = {
        "total_columns": len(df.columns),
        "total_rows": len(df),
        "columns": {},
        "numeric_columns": [],
        "categorical_columns": [],
        "date_columns": [],
        "text_columns": []
    }

    for col in df.columns:
        logger.info(f"🔍 Analyzing column: {col}")

        col_info = {
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isna().sum()),
            "sample_values": df[col].dropna().unique()[:3].tolist()
        }

        # ---- DATE DETECTION ----
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            schema["date_columns"].append(col)
            col_info["role"] = "date"
            logger.info(f"📅 Detected DATE column: {col}")

        # ---- NUMERIC DETECTION ----
        elif pd.api.types.is_numeric_dtype(df[col]):
            schema["numeric_columns"].append(col)
            col_info["role"] = "numeric"
            logger.info(f"🔢 Detected NUMERIC column: {col}")

        # ---- CATEGORICAL vs TEXT ----
        else:
            unique_ratio = df[col].nunique() / max(len(df), 1)

            if unique_ratio < 0.2:
                schema["categorical_columns"].append(col)
                col_info["role"] = "categorical"
                logger.info(f"🏷️ Detected CATEGORICAL column: {col}")
            else:
                schema["text_columns"].append(col)
                col_info["role"] = "text"
                logger.info(f"📝 Detected TEXT column: {col}")

        schema["columns"][col] = col_info

    logger.info("✅ Schema analysis completed")
    logger.info(f"📄 Rows: {schema['total_rows']}, Columns: {schema['total_columns']}")
    logger.info(
        f"Summary → Numeric: {schema['numeric_columns']}, "
        f"Categorical: {schema['categorical_columns']}, "
        f"Dates: {schema['date_columns']}"
    )

    return schema
