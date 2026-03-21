from utils.logger import logger

def analyze_sales_data(df):
    result = {}
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # Smart detection
    sales_col = next((c for c in numeric_cols if any(k in c.lower() for k in ['sales', 'revenue', 'amount', 'price'])), None)
    profit_col = next((c for c in numeric_cols if 'profit' in c.lower()), None)
    cat_col = next((c for c in df.columns if any(k in c.lower() for k in ['region', 'category', 'segment', 'item'])), None)

    if sales_col:
        result["total_sales"] = float(df[sales_col].sum())
        result["average_sales_per_deal"] = float(df[sales_col].mean())
    
    if profit_col:
        result["total_profit"] = float(df[profit_col].sum())
        if sales_col and df[sales_col].sum() != 0:
            result["overall_margin_percent"] = float((df[profit_col].sum() / df[sales_col].sum()) * 100)

    if cat_col and sales_col:
        grouped = df.groupby(cat_col)[sales_col].sum()
        top_cat = grouped.idxmax()
        result["best_performing_category"] = str(top_cat)
        result["top_category_revenue"] = float(grouped.max())

    return result
