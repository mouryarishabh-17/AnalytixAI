
import matplotlib.pyplot as plt
import seaborn as sns
import os
from utils.logger import logger
import pandas as pd
from services.visual_style import apply_modern_theme

def generate_sales_charts(df):
    logger.info("Generating MODERN Sales Charts")
    charts = {}
    os.makedirs("charts/sales", exist_ok=True)
    
    apply_modern_theme()

    # Detect Columns
    amt_col = next((c for c in df.columns if any(k in c.lower() for k in ['sales', 'revenue', 'amount'])), None)
    cat_col = next((c for c in df.columns if any(k in c.lower() for k in ['product', 'category', 'item'])), None)
    date_col = next((c for c in df.columns if any(k in c.lower() for k in ['date', 'time'])), None)
    region_col = next((c for c in df.columns if 'region' in c.lower()), None)

    # 1. Bar Chart (Category vs Sales) - "Top Selling Products"
    if cat_col and amt_col:
        try:
            grouped = df.groupby(cat_col)[amt_col].sum().sort_values(ascending=False).head(10)
            plt.figure(figsize=(10, 6))
            bars = plt.bar(grouped.index, grouped.values, color='#00f2ea', edgecolor='#00f2ea', alpha=0.9)
            plt.title(f"TOP {cat_col.upper()} BY REVENUE", fontsize=14, color='#00f2ea', fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            
            # Remove spines
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            
            path = "charts/sales/cat_impact_modern.png"
            plt.tight_layout()
            plt.savefig(path, dpi=120, facecolor='#1e1e2f')
            plt.close()
            charts["sales_by_category"] = path
        except Exception as e:
            print(f"Sales Bar Error: {e}")

    # 2. Line Chart (Trend) - "Monthly Sales Trend"
    if date_col and amt_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)
            
            if not df_sorted.empty:
                plt.figure(figsize=(10, 6))
                plt.plot(df_sorted[date_col], df_sorted[amt_col], 
                         marker='o', color='#ff00ff', linewidth=2.5)
                plt.fill_between(df_sorted[date_col], df_sorted[amt_col], color='#ff00ff', alpha=0.15)
                
                plt.title("REVENUE TREND OVER TIME", fontsize=14, color='#ff00ff', fontweight='bold')
                plt.xticks(rotation=45)
                
                plt.gca().spines['top'].set_visible(False)
                plt.gca().spines['right'].set_visible(False)
                
                path = "charts/sales/sales_trend_modern.png"
                plt.tight_layout()
                plt.savefig(path, dpi=120, facecolor='#1e1e2f')
                plt.close()
                charts["sales_trend"] = path
        except Exception as e:
            print(f"Sales Line Error: {e}")

    # 3. Heatmap (Region vs Category) - "Sales Intensity by Region"
    if region_col and cat_col and amt_col:
        try:
            pivot_table = df.pivot_table(index=region_col, columns=cat_col, values=amt_col, aggfunc='sum', fill_value=0)
            
            plt.figure(figsize=(10, 6))
            sns.heatmap(pivot_table, cmap='cool_r', annot=True, fmt='g', linewidths=.5)
            
            plt.title("SALES INTENSITY: REGION vs PRODUCT", fontsize=14, color='#00ced1', fontweight='bold')
            plt.xlabel(cat_col.upper())
            plt.ylabel(region_col.upper())
            
            path = "charts/sales/region_heatmap.png"
            plt.tight_layout()
            plt.savefig(path, dpi=120, facecolor='#1e1e2f')
            plt.close()
            charts["region_heatmap"] = path
        except Exception as e:
            print(f"Sales Heatmap Error: {e}")

    logger.info(f"Generated {len(charts)} Sales charts.")
    
    # 4. PRE-GENERATE VARIANTS (Safe)
    try:
        if "sales_by_category" in charts:
             generate_single_sales_chart(df, "sales_by_category", "pie", manual_filename="cat_impact_modern_pie.png")
             generate_single_sales_chart(df, "sales_by_category", "line", manual_filename="cat_impact_modern_line.png")
        
        if "sales_trend" in charts:
             generate_single_sales_chart(df, "sales_trend", "pie", manual_filename="sales_trend_modern_pie.png")
             generate_single_sales_chart(df, "sales_trend", "bar", manual_filename="sales_trend_modern_bar.png")
    
    except Exception as e:
        print(f"Sales Variant Error: {e}")
        
    return charts

def generate_single_sales_chart(df, chart_key, chart_type, manual_filename=None):
    apply_modern_theme()
    
    amt_col = next((c for c in df.columns if any(k in c.lower() for k in ['sales', 'revenue', 'amount'])), None)
    cat_col = next((c for c in df.columns if any(k in c.lower() for k in ['product', 'category', 'item'])), None)
    date_col = next((c for c in df.columns if any(k in c.lower() for k in ['date', 'time'])), None)
    
    try:
        plt.figure(figsize=(10, 6))
        
        if chart_key == "sales_by_category" and cat_col and amt_col:
            grouped = df.groupby(cat_col)[amt_col].sum().sort_values(ascending=False).head(10)
            
            if chart_type == "pie":
                plt.pie(grouped.values, labels=grouped.index, autopct='%1.1f%%', 
                        colors=sns.color_palette('bright'), startangle=140,
                        textprops={'color':"w", 'fontsize': 10})
                plt.title(f"REVENUE SHARE: TOP {cat_col.upper()}", fontweight='bold', color='white')
                
            elif chart_type == "line":
                plt.plot(grouped.index, grouped.values, marker='o', linestyle='-', color='#00f2ea', linewidth=3)
                plt.fill_between(range(len(grouped)), grouped.values, color='#00f2ea', alpha=0.2)
                plt.title(f"REVENUE TREND: TOP {cat_col.upper()}", fontweight='bold', color='#00f2ea')
                plt.xticks(rotation=45, ha='right')
                
        elif chart_key == "sales_trend" and date_col and amt_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            idx = df.dropna(subset=[date_col]).sort_values(date_col)
            
            if chart_type == "bar":
                # Convert to month string if many points? Or just plot
                # For simplicity, bar plot of time points
                plt.bar(idx[date_col], idx[amt_col], color='#ff00ff', alpha=0.8)
                plt.title("REVENUE OVER TIME", fontweight='bold', color='#ff00ff')
                plt.xticks(rotation=45)
                
            elif chart_type == "pie":
                # Pie for time series makes no sense, but user wants it?
                # Aggregate by Month
                idx['Month'] = idx[date_col].dt.strftime('%b')
                monthly = idx.groupby('Month')[amt_col].sum()
                plt.pie(monthly.values, labels=monthly.index, autopct='%1.1f%%')
                plt.title("REVENUE SHARE BY MONTH", fontweight='bold', color='white')

        # Save
        if manual_filename:
            filename = manual_filename
        else:
            filename = f"regen_sales_{chart_key}_{chart_type}.png"
            
        path = f"charts/sales/{filename}"
        plt.tight_layout()
        plt.savefig(path, dpi=120, facecolor='#1e1e2f')
        plt.close()
        return path
        
    except Exception as e:
        print(f"Sales Single Chart Error: {e}")
        return None
