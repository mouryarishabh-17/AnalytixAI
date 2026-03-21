
import matplotlib.pyplot as plt
import os
import pandas as pd
from utils.logger import logger
from services.visual_style import apply_modern_theme

def generate_finance_charts(df):
    logger.info("Generating MODERN Finance Charts")
    charts = {}
    os.makedirs("charts/finance", exist_ok=True)
    
    apply_modern_theme()

    # Flexible Detection
    amt_col = next((c for c in df.columns if any(k in str(c).lower() for k in ['amount', 'budget', 'cost', 'expense', 'income', 'profit'])), None)
    date_col = next((c for c in df.columns if any(k in str(c).lower() for k in ['date', 'time', 'period'])), None)
    
    # Check for dedicated Income/Expense/Profit columns (from your data)
    inc_col = next((c for c in df.columns if 'income' in str(c).lower()), None)
    exp_col = next((c for c in df.columns if 'expense' in str(c).lower()), None)
    prof_col = next((c for c in df.columns if 'profit' in str(c).lower()), None)

    # 1. Comparison Stacked Bar (Income vs Expense)
    if date_col and inc_col and exp_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)
            
            plt.figure(figsize=(10, 6))
            
            # Use Bar Width for clarity
            width = 0.4
            indices = range(len(df_sorted))
            
            # Income Bars (Green)
            plt.bar([i - width/2 for i in indices], df_sorted[inc_col], width=width, color='#32CD32', label='Income', alpha=0.9)
            # Expense Bars (Red)
            plt.bar([i + width/2 for i in indices], df_sorted[exp_col], width=width, color='#FF4500', label='Expense', alpha=0.9)
            
            plt.title("INCOME vs EXPENSE COMPARISON", fontsize=14, color='#FFD700', fontweight='bold')
            plt.legend(loc='upper right')
            plt.xticks(indices, df_sorted[date_col].dt.strftime('%b'), rotation=45) # Just show Month
            
            path = "charts/finance/income_expense_comp.png"
            plt.tight_layout()
            plt.savefig(path, dpi=120, facecolor='#1e1e2f')
            plt.close()
            charts["income_expense_comparison"] = path
        except Exception as e:
            print(f"Finance Comparison Error: {e}")

    # 2. Financial Trend (Profit) - "Profit Margin Trend"
    target_trend_col = prof_col if prof_col else amt_col
    if date_col and target_trend_col:
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_sorted = df.dropna(subset=[date_col]).sort_values(date_col)
            
            plt.figure(figsize=(10, 6))
            
            # Gold Line
            plt.plot(df_sorted[date_col], df_sorted[target_trend_col], 
                     marker='D', color='#ffd700', linewidth=2, linestyle='-')
            plt.fill_between(df_sorted[date_col], df_sorted[target_trend_col], color='#ffd700', alpha=0.15)
            
            # Draw a Zero Line for Profit reference
            plt.axhline(0, color='white', linestyle='--', alpha=0.5, linewidth=1)

            plt.title(f"FINANCIAL TREND: {target_trend_col.upper()}", fontsize=14, color='#ffd700', fontweight='bold')
            plt.xticks(rotation=45)
            
            path = "charts/finance/monthly_trend_modern.png"
            plt.tight_layout()
            plt.savefig(path, dpi=120, facecolor='#1e1e2f')
            plt.close()
            charts["financial_trend"] = path
        except Exception as e:
            print(f"Finance Trend Error: {e}")

    logger.info("Generated Finance Modern Charts")
    
    # 3. PRE-GENERATE VARIANTS (Safe)
    try:
        if "income_expense_comparison" in charts:
             generate_single_finance_chart(df, "income_expense_comparison", "pie", manual_filename="income_expense_comp_pie.png")
             generate_single_finance_chart(df, "income_expense_comparison", "line", manual_filename="income_expense_comp_line.png")
        
        if "financial_trend" in charts:
             generate_single_finance_chart(df, "financial_trend", "pie", manual_filename="monthly_trend_modern_pie.png")
             generate_single_finance_chart(df, "financial_trend", "bar", manual_filename="monthly_trend_modern_bar.png")
    
    except Exception as e:
        print(f"Finance Variant Error: {e}")
        
    return charts

def generate_single_finance_chart(df, chart_key, chart_type, manual_filename=None):
    apply_modern_theme()
    
    # Check for dedicated columns
    inc_col = next((c for c in df.columns if 'income' in str(c).lower()), None)
    exp_col = next((c for c in df.columns if 'expense' in str(c).lower()), None)
    prof_col = next((c for c in df.columns if 'profit' in str(c).lower()), None)
    amt_col = next((c for c in df.columns if any(k in str(c).lower() for k in ['amount', 'budget', 'cost', 'expense', 'income', 'profit'])), None)
    date_col = next((c for c in df.columns if any(k in str(c).lower() for k in ['date', 'time', 'period'])), None)
    
    target_trend_col = prof_col if prof_col else amt_col

    try:
        plt.figure(figsize=(10, 6))
        
        if chart_key == "income_expense_comparison" and date_col and inc_col and exp_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_s = df.dropna(subset=[date_col]).sort_values(date_col)
            
            if chart_type == "pie":
                # Total Ratio of Income vs Expense
                total_inc = df_s[inc_col].sum()
                total_exp = df_s[exp_col].sum()
                plt.pie([total_inc, total_exp], labels=['Total Income', 'Total Expense'], 
                        autopct='%1.1f%%', colors=['#32CD32', '#FF4500'],
                        textprops={'color':"w", 'fontsize': 10})
                plt.title("TOTAL INCOME vs EXPENSE RATIO", fontweight='bold', color='white')
                
            elif chart_type == "line":
                plt.plot(df_s[date_col], df_s[inc_col], color='#32CD32', marker='o', label='Income')
                plt.plot(df_s[date_col], df_s[exp_col], color='#FF4500', marker='x', label='Expense')
                plt.legend()
                plt.title("INCOME & EXPENSE TREND", fontweight='bold', color='white')
                plt.xticks(rotation=45)
                
        elif chart_key == "financial_trend" and date_col and target_trend_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df_s = df.dropna(subset=[date_col]).sort_values(date_col)
            
            if chart_type == "bar":
                plt.bar(df_s[date_col], df_s[target_trend_col], color='#ffd700', alpha=0.8)
                plt.title(f"MONTHLY {target_trend_col.upper()}", fontweight='bold', color='#ffd700')
                plt.xticks(rotation=45)
                
            elif chart_type == "pie":
                # Maybe share of each month?
                idx = df_s.copy()
                idx['Month'] = idx[date_col].dt.strftime('%b')
                monthly = idx.groupby('Month')[target_trend_col].sum()
                # If negative values (loss), pie fails. Take abs?
                monthly_abs = monthly.abs()
                plt.pie(monthly_abs.values, labels=monthly.index, autopct='%1.1f%%')
                plt.title(f"MONTHLY SHARE (MAGNITUDE)", fontweight='bold', color='white')

        # Save
        if manual_filename:
            filename = manual_filename
        else:
            filename = f"regen_finance_{chart_key}_{chart_type}.png"
            
        path = f"charts/finance/{filename}"
        plt.tight_layout()
        plt.savefig(path, dpi=120, facecolor='#1e1e2f')
        plt.close()
        return path
        
    except Exception as e:
        print(f"Finance Single Chart Error: {e}")
        return None
