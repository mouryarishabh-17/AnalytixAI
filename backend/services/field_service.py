import os
import numpy as np
import pandas as pd
from utils.logger import logger

class FieldService:
    @staticmethod
    def _sanitize_dict(data):
        """
        Recursively replaces NaN, Inf, and -Inf with 0 to ensure JSON compliance.
        Handles both standard float and numpy float types.
        """
        if isinstance(data, dict):
            return {k: FieldService._sanitize_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [FieldService._sanitize_dict(v) for v in data]
        elif isinstance(data, (float, np.floating)):
            if pd.isna(data) or np.isinf(data):
                return 0
            return float(data)
        return data

    @staticmethod
    def deep_analyze(df, domain):
        """
        Performs deep domain-specific analysis based on field-work columns.
        """
        results = {
            "summary_stats": {},
            "key_insights": [],
            "ml_insights": {}
        }
        
        # Lazy imports for Analytics
        from services.sales.analytics import analyze_sales_data
        from services.finance.analytics import analyze_finance_data
        from services.student.analytics import analyze_student_data
        from services.employee.analytics import analyze_employee_data

        def safe_round(val, digits=2):
            try:
                num = pd.to_numeric(val, errors='coerce')
                if pd.isna(num): return 0
                return round(float(num), digits)
            except:
                return 0

        # 1. DOMAIN SPECIFIC ANALYSIS (Delegated)
        try:
            if domain == "student":
                specialized_stats = analyze_student_data(df)
                results["summary_stats"].update(specialized_stats)
            elif domain == "sales":
                specialized_stats = analyze_sales_data(df)
                results["summary_stats"].update(specialized_stats)
            elif domain == "finance":
                specialized_stats = analyze_finance_data(df)
                results["summary_stats"].update(specialized_stats)
            elif domain == "employee":
                specialized_stats = analyze_employee_data(df)
                results["summary_stats"].update(specialized_stats)
        except Exception as e:
            logger.error(f"Deep Analysis Error for {domain}: {e}")
            results["summary_stats"]["status"] = "Partial analysis due to error"

        # 2. Generic Fallback & Key Insights
        if not results["summary_stats"]:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if not numeric_cols.empty:
                results["summary_stats"]["metrics"] = {c: safe_round(df[c].mean()) for c in numeric_cols[:5]}
        
        if not results["key_insights"] and domain == "student":
             if 'Daily_Screen_Time' in df.columns and 'Stress_Level' in df.columns:
                high_screen = df[df['Daily_Screen_Time'].isin(['More than 6', '4–6'])]
                if not high_screen.empty:
                    results["key_insights"].append({
                        "title": "Screen-Stress Link",
                        "observation": f"Average stress for high screen users is {safe_round(high_screen['Stress_Level'].mean())}/5"
                    })

        # 3. Trigger Domain-Specific ML Analysis
        # Lazy imports for ML Services
        from services.ml_service import ml_service
        from services.sales.ml_model import sales_ml_service
        from services.finance.ml_model import finance_ml_service
        from services.student.ml_model import student_ml_service
        from services.employee.ml_model import employee_ml_service

        if domain == "sales":
            results["ml_insights"] = sales_ml_service.extract_patterns(df)
        elif domain == "finance":
            results["ml_insights"] = finance_ml_service.extract_patterns(df)
        elif domain == "student":
            results["ml_insights"] = student_ml_service.extract_patterns(df)
        elif domain == "employee":
            results["ml_insights"] = employee_ml_service.extract_patterns(df)
        else:
            results["ml_insights"] = ml_service.extract_patterns(df)

        return FieldService._sanitize_dict(results)

    @staticmethod
    def clean_data(df, domain):
        """
        Standardizes data types and applies domain-specific cleaning logic.
        """
        summary = {"rows_processed": len(df)}
        
        # Lazy imports for Cleaning Services
        from services.sales.cleaning import clean_sales_data
        from services.finance.cleaning import clean_finance_data
        from services.student.cleaning import clean_student_data
        from services.employee.cleaning import clean_employee_data

        try:
            # 1. ROBUST QUANTIZATION: Clean currency, %, and commas for ALL columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        # Check if first valid entry looks like a number with symbols
                        sample = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else ""
                        if any(c in sample for c in ['$', '€', '£', '%', ',']):
                            # Remove non-numeric chars except . and -
                            clean_col = df[col].str.replace(r'[$,£€%]', '', regex=True).str.replace(',', '', regex=False)
                            # Convert to numeric, keep strings if they fail quantization
                            df[col] = pd.to_numeric(clean_col, errors='coerce').fillna(df[col])
                    except:
                        pass

            # 2. DOMAIN CLEANING
            if domain == "sales":
                df, clean_summary = clean_sales_data(df)
            elif domain == "finance":
                df, clean_summary = clean_finance_data(df)
            elif domain == "student":
                df, clean_summary = clean_student_data(df)
            elif domain == "employee":
                df, clean_summary = clean_employee_data(df)
            else:
                clean_summary = {"status": "Generic cleaning (no domain module found)"}
            
            summary.update(clean_summary)
        except Exception as e:
            logger.error(f"Cleaning Error for {domain}: {e}")
            summary["status"] = f"Cleaning failed: {str(e)}"
            
        return df, FieldService._sanitize_dict(summary)
        
    @staticmethod
    def generate_field_charts(df, domain):
        """
        Generates visualized field data charts.
        """
        # Lazy imports for Visualization
        import matplotlib
        matplotlib.use('Agg')  # Set backend for server-side rendering
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        from services.sales.visuals import generate_sales_charts
        from services.finance.visuals import generate_finance_charts
        from services.student.visuals import generate_student_charts
        from services.employee.visuals import generate_employee_charts

        charts = {}
        chart_dir = f"charts/{domain}"
        os.makedirs(chart_dir, exist_ok=True)
        
        plt.style.use('ggplot')

        try:
            plt.close('all') # Safety clear
            if domain == "sales":
                domain_charts = generate_sales_charts(df)
            elif domain == "finance":
                domain_charts = generate_finance_charts(df)
            elif domain == "student":
                domain_charts = generate_student_charts(df)
            elif domain == "employee":
                domain_charts = generate_employee_charts(df)
            else:
                domain_charts = {}

            # Process domain specific charts
            for key, path in domain_charts.items():
                if not path.startswith('/'):
                    charts[key] = f"/{path}"
                else:
                    charts[key] = path

            # Generic Fallback if no domain charts generated
            if not charts:
                numeric_cols = df.select_dtypes(include=['number']).columns[:2]
                for col in numeric_cols:
                    plt.figure(figsize=(8, 5))
                    df[col].hist(color='coral', bins=15)
                    plt.title(f'Stat Profile: {col.replace("_", " ")}')
                    plt.grid(True, alpha=0.3)
                    path = f"{chart_dir}/generic_{col}.png"
                    plt.savefig(path, bbox_inches='tight')
                    plt.close()
                    charts[f"{col}_distribution"] = f"/{path}"

        except Exception as e:
            logger.error(f"Charting Error: {str(e)}")
            plt.close('all')
            pass

        plt.close('all')
        return charts
        
    @staticmethod
    def regenerate_specific_chart(df, domain, chart_name, chart_type):
        """
        New method to handle on-demand chart regeneration (pie/bar/line)
        """
        # Lazy imports for Visualization
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        try:
            plt.close('all')
            # Detect numeric column from chart name (heuristic)
            # e.g. "sales_distribution" -> "sales"
            # This is a simplification; ideally we pass column details from frontend
            # For now, we reuse the generic plotting logic based on likely columns
            
            target_col = None
            for col in df.columns:
                 if col.lower() in chart_name.lower():
                      target_col = col
                      break
            
            if not target_col:
                # Fallback: finding first numeric column
                numeric_cols = df.select_dtypes(include=['number']).columns
                if not numeric_cols.empty:
                    target_col = numeric_cols[0]
            
            if not target_col:
                 return None
                 
            chart_path = f"charts/{domain}/{chart_name}_{chart_type}.png"
            os.makedirs(f"charts/{domain}", exist_ok=True)
            
            plt.figure(figsize=(10, 6))
            
            if chart_type == 'pie':
                 # Bin data for pie chart if too many unique values
                 if df[target_col].nunique() > 10:
                      data = df[target_col].value_counts().nlargest(10)
                 else:
                      data = df[target_col].value_counts()
                 
                 plt.pie(data, labels=data.index, autopct='%1.1f%%', startangle=90)
                 plt.title(f'{target_col} Distribution')
                 
            elif chart_type == 'line':
                 # Need a time axis for line chart ideally, else just index
                 plt.plot(df[target_col].values)
                 plt.title(f'{target_col} Trend')
                 plt.grid(True)
                 
            elif chart_type == 'bar':
                 if df[target_col].nunique() > 20:
                      data = df[target_col].value_counts().nlargest(15)
                 else:
                      data = df[target_col].value_counts()
                 data.plot(kind='bar', color='skyblue')
                 plt.title(f'{target_col} Count')
                 plt.xticks(rotation=45)
            
            plt.tight_layout()
            plt.savefig(chart_path)
            plt.close()
            
            return f"/{chart_path}"
            
        except Exception as e:
            print(f"Regen Error: {e}")
            return None

field_service = FieldService()
