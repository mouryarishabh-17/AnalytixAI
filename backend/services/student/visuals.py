
import matplotlib
matplotlib.use('Agg')  # Server-side rendering
import matplotlib.pyplot as plt
import seaborn as sns
import os
import pandas as pd
import numpy as np
from services.visual_style import apply_modern_theme

def generate_student_charts(df):
    """
    Generate charts for student domain data, handling both numeric and categorical ranges.
    """
    charts = {}
    os.makedirs("charts/student", exist_ok=True)
    
    # Modern Style
    os.makedirs("charts/student", exist_ok=True)
    
    # Modern Style
    apply_modern_theme()
    student_color = '#00CED1' # Neon Dark Turquoise
    
    # Text-based ranges order
    study_order = ['Less than 2', '2 to 4', '4 to 6', 'More than 6']
    screen_order = ['Less than 2', '2 to 4', '4 to 6', 'More than 6']
    
    # 1. DAILY STUDY HOURS (Bar Chart for Categories)
    col = next((c for c in df.columns if 'study' in c.lower()), None)
    if col:
        plt.figure(figsize=(10, 6))
        
        # Check if numeric or categorical
        if pd.to_numeric(df[col], errors='coerce').notna().all():
            sns.histplot(df[col], kde=True, color=student_color)
        else:
            # Count and reorder for correct display
            counts = df[col].astype(str).value_counts()
            # Sort if possible
            existing_order = [x for x in study_order if x in counts.index]
            other_order = [x for x in counts.index if x not in study_order]
            final_order = existing_order + other_order
            
            sns.countplot(y=df[col], order=final_order, color=student_color, alpha=0.8)
            
        plt.title("DAILY STUDY PATTERNS", fontweight='bold', color='#2F4F4F')
        plt.xlabel("Count")
        plt.ylabel("Hours per Day")
        plt.tight_layout()
        path = "charts/student/dist_Daily_Study_Hours.png"
        plt.savefig(path)
        plt.close()
        charts['Daily_Study_Hours'] = path

    # 2. SCREEN TIME (Bar Chart)
    col = next((c for c in df.columns if 'screen' in c.lower()), None)
    if col:
        plt.figure(figsize=(10, 6))
        if pd.to_numeric(df[col], errors='coerce').notna().all():
            sns.histplot(df[col], kde=True, color='#FF6347') # Tomato red
        else:
            counts = df[col].astype(str).value_counts()
            existing_order = [x for x in screen_order if x in counts.index]
            other_order = [x for x in counts.index if x not in screen_order]
            final_order = existing_order + other_order
            
            sns.countplot(y=df[col], order=final_order, color='#FF6347', alpha=0.8)
            
        plt.title("DAILY SCREEN TIME", fontweight='bold', color='#8B0000')
        plt.xlabel("Count")
        plt.tight_layout()
        path = "charts/student/dist_Daily_Screen_Time.png"
        plt.savefig(path)
        plt.close()
        charts['Daily_Screen_Time'] = path

    # 3. STRESS LEVEL (Histogram - since it is 1-5)
    col = next((c for c in df.columns if 'stress' in c.lower()), None)
    if col:
        plt.figure(figsize=(10, 6))
        # Ensure numeric
        numeric_stress = pd.to_numeric(df[col], errors='coerce')
        sns.histplot(numeric_stress, bins=5, kde=True, color='#9370DB') # Purple
        plt.title("STRESS LEVEL DISTRIBUTION (1-5)", fontweight='bold', color='#4B0082')
        plt.xlabel("Stress Scale")
        plt.tight_layout()
        path = "charts/student/dist_Stress_Level.png"
        plt.savefig(path)
        plt.close()
        charts['Stress_Level'] = path

    # 4. SCATTER PLOT: STUDY vs SCREEN TIME
    study_col = next((c for c in df.columns if 'study' in c.lower()), None)
    screen_col = next((c for c in df.columns if 'screen' in c.lower()), None)
    
    if study_col and screen_col:
        try:
            plt.figure(figsize=(10, 6))
            
            # Use our parsing logic? Or simpler approach
            def quick_parse(val):
                if 'less' in str(val).lower(): return 1
                if 'more' in str(val).lower(): return 7
                if 'to' in str(val).lower(): return float(str(val).split(' to ')[0]) + 1
                return 0 # fallback
                
            x_vals = df[study_col].apply(quick_parse)
            y_vals = df[screen_col].apply(quick_parse)
            
            # Jitter to avoid Overlap
            x_vals += np.random.normal(0, 0.2, size=len(x_vals))
            y_vals += np.random.normal(0, 0.2, size=len(y_vals))
            
            plt.scatter(x_vals, y_vals, alpha=0.7, color='#FFD700', s=100, edgecolors='white')
            
            plt.title("CORRELATION: STUDY vs SCREEN TIME", fontweight='bold', color='#FFD700', fontsize=14)
            plt.xlabel("Daily Study Hours (Approx)", color='white')
            plt.ylabel("Daily Screen Time (Approx)", color='white')
            
            # Add trend line
            z = np.polyfit(x_vals, y_vals, 1)
            p = np.poly1d(z)
            plt.plot(x_vals, p(x_vals), "r--", alpha=0.8, linewidth=2)
            
            path = "charts/student/scatter_study_screen.png"
            plt.tight_layout()
            plt.savefig(path, dpi=120, facecolor='#1e1e2f')
            plt.close()
            charts['Study_vs_Screen_Scatter'] = path
        except Exception as e:
            print(f"Student Scatter Error: {e}")

    # PRE-GENERATE VARIANTS (For instant switching without session)
    try:
        generate_single_student_chart(df, 'Daily_Study_Hours', 'pie', manual_filename='dist_Daily_Study_Hours_pie.png')
        generate_single_student_chart(df, 'Daily_Study_Hours', 'line', manual_filename='dist_Daily_Study_Hours_line.png')
        
        generate_single_student_chart(df, 'Daily_Screen_Time', 'pie', manual_filename='dist_Daily_Screen_Time_pie.png')
        generate_single_student_chart(df, 'Daily_Screen_Time', 'line', manual_filename='dist_Daily_Screen_Time_line.png')
        
        generate_single_student_chart(df, 'Stress_Level', 'pie', manual_filename='dist_Stress_Level_pie.png')
        generate_single_student_chart(df, 'Stress_Level', 'line', manual_filename='dist_Stress_Level_line.png')
    except Exception as e:
        print(f"⚠️ Variant generation warning: {e}")

    print(f"📊 Student charts generated: {list(charts.keys())}")
    return charts

def generate_single_student_chart(df, chart_name, chart_type, manual_filename=None):
    """
    Dynamically regenerate a single chart with a specific type.
    """
    apply_modern_theme()
    
    # 1. Identify Column based on chart_name
    col = None
    chart_name_lower = chart_name.lower()
    
    if 'study' in chart_name_lower:
         col = next((c for c in df.columns if 'study' in c.lower()), None)
    elif 'screen' in chart_name_lower:
         col = next((c for c in df.columns if 'screen' in c.lower()), None)
    elif 'stress' in chart_name_lower:
         col = next((c for c in df.columns if 'stress' in c.lower()), None)
         
    if not col:
        print(f"❌ Chart regeneration failed: Column not found for {chart_name}")
        return None

    try:
        plt.figure(figsize=(10, 6))
        
        # 2. Plot Logic
        if chart_type == 'pie':
            counts = df[col].value_counts()
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', 
                    colors=sns.color_palette('bright'), startangle=140,
                    textprops={'color':"w", 'fontsize': 10})
            plt.title(f"{col} DISTRIBUTION", fontweight='bold', color='white')
            
        elif chart_type == 'line':
            # Trend of counts (Frequency Polygon)
            # Need to categorize first
            if pd.to_numeric(df[col], errors='coerce').notna().all():
                 # Numeric: Histogram-like line
                 sns.kdeplot(df[col], fill=True, color='#00FFFF', alpha=0.3, linewidth=3)
            else:
                 # Categorical: Count plot line
                 counts = df[col].value_counts()
                 # Try to sort logically if possible (ranges)
                 sorted_index = sorted(counts.index)
                 counts = counts.reindex(sorted_index)
                 
                 plt.plot(counts.index, counts.values, marker='o', linestyle='-', color='#00FFFF', linewidth=3)
                 plt.fill_between(range(len(counts)), counts.values, color='#00FFFF', alpha=0.2)
                 
            plt.grid(True, linestyle='--', alpha=0.2)
            plt.title(f"{col} TREND", fontweight='bold', color='#00FFFF')
            plt.xticks(rotation=45, color='white')
            plt.yticks(color='white')
            
        else: # Default Bar
            if pd.to_numeric(df[col], errors='coerce').notna().all():
                 sns.histplot(df[col], kde=True, color='#00CED1')
            else:
                 sns.countplot(y=df[col], order=df[col].value_counts().index, color='#00CED1')
            plt.title(f"{col} DISTRIBUTION", fontweight='bold', color='#00CED1')
            plt.xlabel("Count", color='white')

        # 3. Save
        if manual_filename:
            filename = manual_filename
        else:
            filename = f"regen_{chart_name}_{chart_type}.png"
            
        path = f"charts/student/{filename}"
        plt.tight_layout()
        plt.savefig(path, dpi=120, facecolor='#1e1e2f')
        plt.close()
        
        return f"/charts/student/{filename}"
    except Exception as e:
        print(f"❌ Regeneration Error: {e}")
        return None
