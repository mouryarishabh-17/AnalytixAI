import pandas as pd
from utils.logger import logger

def analyze_employee_data(df):
    """
    Domain-specific employee analytics with meaningful workforce insights
    """
    logger.info("👔 Employee analytics started")
    
    result = {}
    result["total_employees"] = len(df)
    result["columns_analyzed"] = list(df.columns)
    
    # ======================
    # AGE DEMOGRAPHICS
    # ======================
    
    # Helper to parse experience ranges
    def parse_experience_range(val):
        val = str(val).lower()
        if 'less than 1' in val: return 0.5
        if '1 to 3' in val or '1-3' in val: return 2.0
        if '3 to 5' in val or '3-5' in val: return 4.0
        if 'more than 5' in val: return 7.0
        try:
            return float(val)
        except:
            return None
    age_cols = [c for c in df.columns if 'age' in c.lower()]
    if age_cols:
        age_col = age_cols[0]
        logger.info(f"Found age column: {age_col}")
        
        # Check if it's categorical (age groups) or numeric
        if df[age_col].dtype == 'object' or df[age_col].dtype.name == 'category':
            # Categorical age groups (e.g., "18-25", "26-30")
            age_dist = df[age_col].value_counts()
            result["age_distribution"] = {str(k): int(v) for k, v in age_dist.items()}
            result["largest_age_group"] = str(age_dist.idxmax())
            result["largest_age_group_count"] = int(age_dist.max())
        else:
            # Numeric age
            age_data = pd.to_numeric(df[age_col], errors='coerce').dropna()
            if len(age_data) > 0:
                result["avg_age"] = round(float(age_data.mean()), 1)
                result["youngest_employee"] = float(age_data.min())
                result["oldest_employee"] = float(age_data.max())
                
                # Age brackets
                young = (age_data < 30).sum()
                mid_career = ((age_data >= 30) & (age_data < 45)).sum()
                senior = (age_data >= 45).sum()
                
                result["young_professionals"] = int(young)
                result["mid_career_professionals"] = int(mid_career)
                result["senior_professionals"] = int(senior)
    
    # ======================
    # WORK EXPERIENCE
    # ======================
    exp_cols = [c for c in df.columns if any(k in c.lower() for k in ['experience', 'years'])]
    if exp_cols:
        exp_col = exp_cols[0]
        logger.info(f"Found experience column: {exp_col}")
        
        # Always try to get numeric stats first
        exp_data_numeric = pd.to_numeric(df[exp_col], errors='coerce')
        
        # If mostly NaN (text ranges), use parser
        if exp_data_numeric.isna().mean() > 0.5:
             exp_data_numeric = df[exp_col].apply(parse_experience_range)
        
        exp_data_numeric = exp_data_numeric.dropna()

        # Categorical distribution (Always good to have)
        exp_dist = df[exp_col].value_counts()
        result["experience_distribution"] = {str(k): int(v) for k, v in exp_dist.items()}
        result["most_common_experience"] = str(exp_dist.idxmax())

        # Numeric stats (from parsed values)
        if len(exp_data_numeric) > 0:
            result["avg_experience_years"] = round(float(exp_data_numeric.mean()), 1)
            result["max_experience_years"] = float(exp_data_numeric.max())
            
            # Experience levels (based on parsed numeric values)
            entry = (exp_data_numeric < 2).sum()
            intermediate = ((exp_data_numeric >= 2) & (exp_data_numeric < 5)).sum()
            experienced = (exp_data_numeric >= 5).sum()
            
            result["entry_level_count"] = int(entry)
            result["intermediate_level_count"] = int(intermediate)
            result["experienced_level_count"] = int(experienced)
    
    # ======================
    # SYSTEM USAGE/WILLINGNESS
    # ======================
    usage_cols = [c for c in df.columns if any(k in c.lower() for k in ['usage', 'willing', 'adoption', 'system'])]
    if usage_cols:
        usage_col = usage_cols[0]
        logger.info(f"Found usage/willingness column: {usage_col}")
        
        # Typically Yes/No or 1/0
        usage_data = df[usage_col].value_counts()
        result["usage_willingness_distribution"] = {str(k): int(v) for k, v in usage_data.items()}
        
        # Calculate adoption rate
        total = len(df[usage_col].dropna())
        if total > 0:
            # Try to identify positive responses
            positive_responses = 0
            for val in df[usage_col].dropna():
                val_str = str(val).lower()
                if val_str in ['yes', '1', '1.0', 'true', 'willing', 'high']:
                    positive_responses += 1
            
            if positive_responses > 0:
                adoption_rate = (positive_responses / total) * 100
                result[" system_adoption_rate"] = round(float(adoption_rate), 1)
                result["willing_employees_count"] = int(positive_responses)
                result["unwilling_employees_count"] = int(total - positive_responses)
    
    # ======================
    # GENDER DIVERSITY
    # ======================
    gender_cols = [c for c in df.columns if 'gender' in c.lower()]
    if gender_cols:
        gender_col = gender_cols[0]
        gender_dist = df[gender_col].value_counts()
        result["gender_distribution"] = {str(k): int(v) for k, v in gender_dist.items()}
        
        # Diversity score (closer to 50/50 is better)
        if len(gender_dist) >= 2:
            values = list(gender_dist.values)
            total = sum(values)
            percentages = [(v/total)*100 for v in values]
            # If two genders, check how close to 50/50
            if len(percentages) == 2:
                diversity_score = 100 - abs(percentages[0] - 50)
                result["gender_diversity_score"] = round(float(diversity_score), 1)
    
    # ======================
    # KEY FINDINGS
    # ======================
    insights = []
    
    if "system_adoption_rate" in result:
        if result["system_adoption_rate"] > 70:
            insights.append(f"Strong system adoption: {result['system_adoption_rate']}% of employees willing")
        elif result["system_adoption_rate"] < 50:
            insights.append(f"Low system adoption: Only {result['system_adoption_rate']}% willing")
    
    if "avg_experience_years" in result:
        if result["avg_experience_years"] < 2:
            insights.append(f"Workforce is junior (avg {result['avg_experience_years']} years)")
        elif result["avg_experience_years"] > 8:
            insights.append(f"Highly experienced workforce (avg {result['avg_experience_years']} years)")
    
    if "gender_diversity_score" in result:
        if result["gender_diversity_score"] > 80:
            insights.append(f"Excellent gender diversity (score: {result['gender_diversity_score']}/100)")
        elif result["gender_diversity_score"] < 60:
            insights.append(f"Gender imbalance detected (diversity score: {result['gender_diversity_score']}/100)")
    
    if "largest_age_group" in result:
        insights.append(f"Largest demographic: {result['largest_age_group']} age group")
    
    if insights:
        result["key_workforce_insights"] = insights
    
    logger.info(f"✅ Employee analytics completed - {len(result)} metrics generated")
    return result
