
import matplotlib
matplotlib.use('Agg')  # Server-side rendering
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np
from services.visual_style import apply_modern_theme

def generate_employee_charts(df):
    """
    Generate charts for employee domain data, handling both numeric and categorical ranges.
    """
    charts = {}
    os.makedirs("charts/employee", exist_ok=True)
    
    # Modern Style
    os.makedirs("charts/employee", exist_ok=True)
    
    # Modern Style
    apply_modern_theme()
    emp_color = '#DA70D6' # Neon Orchid
    
    # Text-based ranges order
    exp_order = ['Less than 1', '1 to 3', '3 to 5', 'More than 5']
    age_order = ['18-25', '26-30', 'Above 30']
    
    # 1. WORK EXPERIENCE (Bar Chart for Categories)
    col = next((c for c in df.columns if any(k in c.lower() for k in ['experience', 'years'])), None)
    if col:
        plt.figure(figsize=(10, 6))
        
        # Check if numeric or categorical
        if pd.to_numeric(df[col], errors='coerce').notna().all():
            sns.histplot(df[col], kde=True, color=emp_color)
        else:
            # Count and reorder for correct display
            counts = df[col].astype(str).value_counts()
            existing_order = [x for x in exp_order if x in counts.index]
            other_order = [x for x in counts.index if x not in exp_order]
            final_order = existing_order + other_order
            
            sns.countplot(y=df[col], order=final_order, color=emp_color, alpha=0.8)
            
        plt.title("WORK EXPERIENCE DISTRIBUTION", fontweight='bold', color='#4B0082')
        plt.xlabel("Count")
        plt.ylabel("Years")
        plt.tight_layout()
        path = "charts/employee/dist_Work_Experience_Years.png"
        plt.savefig(path)
        plt.close()
        charts['Work_Experience_Years'] = path

    # 2. AGE GROUP (Bar Chart)
    col = next((c for c in df.columns if 'age' in c.lower()), None)
    if col:
        plt.figure(figsize=(10, 6))
        
        # Check if numeric or categorical
        if pd.to_numeric(df[col], errors='coerce').notna().all():
            sns.histplot(df[col], kde=True, color='#8A2BE2') # BlueViolet
        else:
            counts = df[col].astype(str).value_counts()
            existing_order = [x for x in age_order if x in counts.index]
            other_order = [x for x in counts.index if x not in age_order]
            final_order = existing_order + other_order
            
            sns.countplot(y=df[col], order=final_order, color='#8A2BE2', alpha=0.8)
            
        plt.title("AGE GROUP DISTRIBUTION", fontweight='bold', color='#4B0082')
        plt.xlabel("Count")
        plt.tight_layout()
        path = "charts/employee/dist_Age_Group.png"
        plt.savefig(path)
        plt.close()
        charts['Age_Group'] = path

    # 3. JOB SATISFACTION (Histogram - since it is 1-5)
    col = next((c for c in df.columns if 'satisfaction' in c.lower()), None)
    if col:
        plt.figure(figsize=(10, 6))
        # Ensure numeric
        numeric_satis = pd.to_numeric(df[col], errors='coerce')
        sns.histplot(numeric_satis, bins=5, kde=True, color='#BA55D3') # MediumOrchid
        plt.title("JOB SATISFACTION (1-5)", fontweight='bold', color='#4B0082')
        plt.xlabel("Satisfaction Level")
        plt.tight_layout()
        path = "charts/employee/dist_Job_Satisfaction.png"
        plt.savefig(path)
        plt.close()
        charts['Job_Satisfaction'] = path

    # 4. LINE CHART: EXPERIENCE vs INCOME TREND
    exp_col = next((c for c in df.columns if any(k in c.lower() for k in ['experience', 'years'])), None)
    inc_col = next((c for c in df.columns if any(k in c.lower() for k in ['income', 'salary'])), None)
    
    if exp_col and inc_col:
        try:
            plt.figure(figsize=(10, 6))
            
            # Simple Parse for Experience
            def parse_exp(val):
                if 'less' in str(val).lower(): return 0.5
                if 'more' in str(val).lower(): return 6
                if 'to' in str(val).lower(): return float(str(val).split(' to ')[0]) + 1
                return 0
            
            df_chart = df.copy()
            df_chart['exp_numeric'] = df_chart[exp_col].apply(parse_exp)
            
            # Group by Experience Level and get Mean Income
            trend = df_chart.groupby('exp_numeric')[inc_col].mean().sort_index()
            
            plt.plot(trend.index, trend.values, marker='o', linestyle='-', color='#00FF00', linewidth=3, markersize=8)
            plt.fill_between(trend.index, trend.values, color='#00FF00', alpha=0.1)
            
            plt.title("INCOME GROWTH by EXPERIENCE", fontweight='bold', color='#00FF00', fontsize=14)
            plt.xlabel("Years of Experience (Approx)", color='white')
            plt.ylabel("Average Income", color='white')
            plt.grid(True, linestyle='--', alpha=0.2)
            
            path = "charts/employee/line_exp_income.png"
            plt.tight_layout()
            plt.savefig(path, dpi=120, facecolor='#1e1e2f')
            plt.close()
            charts['Income_Growth_Trend'] = path
        except Exception as e:
            print(f"Employee Trend Error: {e}")

    # PRE-GENERATE VARIANTS
    try:
        generate_single_employee_chart(df, 'Work_Experience_Years', 'pie', manual_filename='dist_Work_Experience_Years_pie.png')
        generate_single_employee_chart(df, 'Work_Experience_Years', 'line', manual_filename='dist_Work_Experience_Years_line.png')
        
        generate_single_employee_chart(df, 'Age_Group', 'pie', manual_filename='dist_Age_Group_pie.png')
        generate_single_employee_chart(df, 'Age_Group', 'line', manual_filename='dist_Age_Group_line.png')
        
        generate_single_employee_chart(df, 'Job_Satisfaction', 'pie', manual_filename='dist_Job_Satisfaction_pie.png')
        generate_single_employee_chart(df, 'Job_Satisfaction', 'pie', manual_filename='dist_Job_Satisfaction_pie.png')
        generate_single_employee_chart(df, 'Job_Satisfaction', 'line', manual_filename='dist_Job_Satisfaction_line.png')
        
        # New: Income Trend Variants
        generate_single_employee_chart(df, 'Income_Growth_Trend', 'bar', manual_filename='line_exp_income_bar.png')
        generate_single_employee_chart(df, 'Income_Growth_Trend', 'pie', manual_filename='line_exp_income_pie.png')
    except Exception as e:
        import traceback
        with open("debug_error.log", "a") as f:
             f.write(f"Employee Variant Error: {e}\n{traceback.format_exc()}\n")
        print(f"⚠️ Employee variant generation warning: {e}")

    print(f"📊 Employee charts generated: {list(charts.keys())}")
    return charts

def generate_single_employee_chart(df, chart_name, chart_type, manual_filename=None):
    """
    Dynamically regenerate a single chart with a specific type.
    """
    apply_modern_theme()
    
    # 1. Identify Column
    col = None
    chart_name_lower = chart_name.lower()
    
    if 'experience' in chart_name_lower:
         col = next((c for c in df.columns if any(k in c.lower() for k in ['experience', 'years'])), None)
    elif 'age' in chart_name_lower:
         col = next((c for c in df.columns if 'age' in c.lower()), None)
    elif 'satisfaction' in chart_name_lower:
         col = next((c for c in df.columns if 'satisfaction' in c.lower()), None)
    elif 'income' in chart_name_lower or 'trend' in chart_name_lower:
         # Special handling for trend (requires TWO columns)
         col = "TREND_PLACEHOLDER"
         exp_col = next((c for c in df.columns if any(k in c.lower() for k in ['experience', 'years'])), None)
         inc_col = next((c for c in df.columns if any(k in c.lower() for k in ['income', 'salary'])), None)
         
    if not col:
        print(f"❌ Chart regeneration failed: Column not found for {chart_name}")
        return None

    try:
        plt.figure(figsize=(10, 6))
        
        # SPECIAL CASE: TREND
        if col == "TREND_PLACEHOLDER" and exp_col and inc_col:
             def parse_exp(val):
                if 'less' in str(val).lower(): return 0.5
                if 'more' in str(val).lower(): return 6
                if 'to' in str(val).lower(): return float(str(val).split(' to ')[0]) + 1
                return 0
             
             df_chart = df.copy()
             df_chart['exp_numeric'] = df_chart[exp_col].apply(parse_exp)
             trend = df_chart.groupby('exp_numeric')[inc_col].mean().sort_index()
             
             if chart_type == 'bar':
                 plt.bar(trend.index.astype(str), trend.values, color='#00FF00', alpha=0.8)
                 plt.title("INCOME GROWTH by EXPERIENCE", fontweight='bold', color='#00FF00')
                 
             elif chart_type == 'pie':
                 # Pie makes little sense, but for demo completeness:
                 # Share of Average Income by Level
                 plt.pie(trend.values, labels=trend.index.astype(str), autopct='%1.1f%%')
                 plt.title("AVG INCOME SHARE by EXPERIENCE", fontweight='bold', color='white')
                 
             elif chart_type == 'line': # Default
                 plt.plot(trend.index, trend.values, marker='o', linestyle='-', color='#00FF00', linewidth=3)
                 plt.fill_between(trend.index, trend.values, color='#00FF00', alpha=0.1)
                 plt.title("INCOME GROWTH by EXPERIENCE", fontweight='bold', color='#00FF00')
                 
             plt.grid(True, linestyle='--', alpha=0.2)
             plt.xlabel("Years of Experience (Approx)", color='white')
             plt.ylabel("Average Income", color='white')

        # 2. Logic (Standard Single Column)
        elif chart_type == 'pie' and col != "TREND_PLACEHOLDER":
            counts = df[col].value_counts()
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', 
                    colors=sns.color_palette('pastel'), startangle=140,
                    textprops={'color':"w", 'fontsize': 10})
            plt.title(f"{col} DISTRIBUTION", fontweight='bold', color='white')
            
        elif chart_type == 'line':
            if pd.to_numeric(df[col], errors='coerce').notna().all():
                 sns.kdeplot(df[col], fill=True, color='#DA70D6', alpha=0.3, linewidth=3)
            else:
                 counts = df[col].value_counts()
                 sorted_index = sorted(counts.index)
                 counts = counts.reindex(sorted_index)
                 plt.plot(counts.index.astype(str), counts.values, marker='o', linestyle='-', color='#DA70D6', linewidth=3)
                 plt.fill_between(range(len(counts)), counts.values, color='#DA70D6', alpha=0.2)
            plt.grid(True, linestyle='--', alpha=0.2)
            plt.title(f"{col} TREND", fontweight='bold', color='#DA70D6')
            plt.xticks(rotation=45, color='white')
            
        else: # Bar
            if pd.to_numeric(df[col], errors='coerce').notna().all():
                 sns.histplot(df[col], kde=True, color='#BA55D3')
            else:
                 sns.countplot(y=df[col], order=df[col].value_counts().index, color='#BA55D3')
            plt.title(f"{col} DISTRIBUTION", fontweight='bold', color='#BA55D3')
            plt.xlabel("Count", color='white')

        # 3. Save
        if manual_filename:
            filename = manual_filename
        else:
            filename = f"regen_{chart_name}_{chart_type}.png"
            
        path = f"charts/employee/{filename}"
        plt.tight_layout()
        plt.savefig(path, dpi=120, facecolor='#1e1e2f')
        plt.close()
        
        return f"/charts/employee/{filename}"
    except Exception as e:
        print(f"❌ Regeneration Error: {e}")
        return None
