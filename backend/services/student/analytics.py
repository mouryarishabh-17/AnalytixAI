import pandas as pd
from utils.logger import logger

def analyze_student_data(df):
    """
    Domain-specific student analytics with meaningful insights
    """
    logger.info("📚 Student analytics started")
    
    result = {}
    result["total_students"] = len(df)
    result["columns_analyzed"] = list(df.columns)
    
    def parse_range(val):
        val = str(val).lower()
        if 'less than 2' in val: return 1.5
        if '2 to 4' in val or '2-4' in val or '2–4' in val: return 3.0 # Handle 'to' and hyphens
        if '4 to 6' in val or '4-6' in val or '4–6' in val: return 5.0
        if 'more than 6' in val: return 7.0
        try:
            return float(val)
        except:
            return None

    # ======================
    # STUDY PATTERNS
    # ======================
    study_cols = [c for c in df.columns if any(k in c.lower() for k in ['study', 'hours'])]
    if study_cols:
        study_col = study_cols[0]
        
        # Try numeric first
        study_data = pd.to_numeric(df[study_col], errors='coerce')
        
        # If mostly NaN (text ranges), use parser
        if study_data.isna().mean() > 0.5:
             study_data = df[study_col].apply(parse_range)
        
        study_data = study_data.dropna()
        
        if len(study_data) > 0:
            result["avg_study_hours"] = round(float(study_data.mean()), 1)
            result["max_study_hours"] = float(study_data.max())
            
            low_study = (study_data < 3).sum()
            moderate_study = ((study_data >= 3) & (study_data <= 6)).sum()
            high_study = (study_data > 6).sum()
            
            result["low_study_count"] = int(low_study)
            result["moderate_study_count"] = int(moderate_study)
            result["high_study_count"] = int(high_study)
    
    # ======================
    # SCREEN TIME ANALYSIS
    # =======================
    screen_cols = [c for c in df.columns if 'screen' in c.lower()]
    if screen_cols:
        screen_col = screen_cols[0]
        
        screen_data = pd.to_numeric(df[screen_col], errors='coerce')
        if screen_data.isna().mean() > 0.5:
             screen_data = df[screen_col].apply(parse_range)
             
        screen_data = screen_data.dropna()
        
        if len(screen_data) > 0:
            result["avg_screen_time"] = round(float(screen_data.mean()), 1)
            result["max_screen_time"] = float(screen_data.max())
            
            excessive_screen = (screen_data > 6).sum()
            result["excessive_screen_time_students"] = int(excessive_screen)
            result["excessive_screen_time_pct"] = round(float((excessive_screen / len(screen_data)) * 100), 1)
    
    # ======================
    # STRESS LEVEL ANALYSIS
    # ======================
    stress_cols = [c for c in df.columns if 'stress' in c.lower()]
    if stress_cols:
        stress_col = stress_cols[0]
        stress_data = pd.to_numeric(df[stress_col], errors='coerce').dropna()
        
        if len(stress_data) > 0:
            result["avg_stress_level"] = round(float(stress_data.mean()), 2)
            result["max_stress_level"] = float(stress_data.max())
            
            high_stress = (stress_data > 3).sum()
            result["high_stress_count"] = int(high_stress)
            result["high_stress_pct"] = round(float((high_stress / len(stress_data)) * 100), 1)
    
    # ======================
    # GENDER DISTRIBUTION
    # ======================
    gender_cols = [c for c in df.columns if 'gender' in c.lower()]
    if gender_cols:
        gender_col = gender_cols[0]
        gender_dist = df[gender_col].value_counts()
        result["gender_distribution"] = {str(k): int(v) for k, v in gender_dist.items()}
    
    # ======================
    # KEY FINDINGS
    # ======================
    insights = []
    
    if "high_stress_pct" in result and result["high_stress_pct"] > 40:
        insights.append(f"High Stress Alert: {result['high_stress_pct']}% of students report stress > 3/5")
    
    if "avg_study_hours" in result:
        avg_study = result["avg_study_hours"]
        if avg_study < 3:
            insights.append(f"Low Study Engagement: Average only {avg_study} hours/day")
        elif avg_study > 5:
            insights.append(f"High Study Engagement: Average {avg_study} hours/day")
    
    if "excessive_screen_time_pct" in result and result["excessive_screen_time_pct"] > 30:
        insights.append(f"Screen Time Concern: {result['excessive_screen_time_pct']}% have >6 hours daily")
    
    if insights:
        result["key_findings"] = insights
    
    logger.info(f"✅ Student analytics completed metrics: {list(result.keys())}")
    return result
