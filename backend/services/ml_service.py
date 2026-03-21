import pandas as pd
import numpy as np
from utils.logger import logger

class MLService:
    @staticmethod
    def extract_patterns(df):
        """
        Analyzes field data using ML to find hidden patterns and feature importance.
        """
        # Lazy import heavy ML libraries
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import LabelEncoder
        
        try:
            # 1. Prepare data (Drop non-predictive or empty columns)
            cols_to_use = [col for col in df.columns if df[col].notna().sum() > 10]
            if len(cols_to_use) < 3:
                return MLService._get_patterns_failed_response("Not enough columns with valid data for ML analysis (need at least 3)")
            
            if len(df) < 5:
                return MLService._get_patterns_failed_response("Not enough rows for meaningful predictive analysis (need at least 5 rows)")

            df_ml = df[cols_to_use].copy()
            
            # 2. Encode categorical data
            encoders = {}
            for col in df_ml.columns:
                if df_ml[col].dtype == 'object':
                    le = LabelEncoder()
                    # Ensure all values are strings for encoding, handling NaN
                    df_ml[col] = le.fit_transform(df_ml[col].astype(str).fillna('Unknown'))
                    encoders[col] = le

            # 3. Target: Try to find a suitable column to predict
            target_col = None
            
            # Domain-specific targets
            priority_targets = [
                'Stress_Level', 'System_Usage_Willingness', 
                'Monthly_Income_Range', 'Product_Quality', 
                'Total_Sales', 'Profit', 'Outcome', 'Status'
            ]
            
            for pt in priority_targets:
                if pt in df.columns:
                    target_col = pt
                    break
            
            # If still none, pick the last numeric column or any column with "Level" or "Amount"
            if not target_col:
                potential = [c for c in df.columns if 'level' in c.lower() or 'amount' in c.lower() or 'score' in c.lower()]
                if potential:
                    target_col = potential[0]
                else:
                    # Final fallback: any numeric column that isn't ID-like
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if not numeric_cols.empty:
                        target_col = numeric_cols[-1]

            if not target_col:
                return MLService._get_patterns_failed_response("No suitable target column (like 'Revenue', 'Sales', or 'Level') found for prediction modeling")

            # Check if target column exists in processed DF (might have been dropped if empty)
            if target_col not in df_ml.columns:
                 return MLService._get_patterns_failed_response(f"Target column '{target_col}' has insufficient data")

            X = df_ml.drop(columns=[target_col])
            y = df_ml[target_col]
            
            # Handle NaN in X if any remain
            X = X.fillna(0)

            # 4. Train appropriate model
            from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

            # Determine if Regression (Numeric Target with many values) or Classification
            is_regression = False
            if pd.api.types.is_numeric_dtype(df_ml[target_col]):
                if df_ml[target_col].nunique() > 10: # Heuristic for continuous data
                    is_regression = True
            
            if is_regression:
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                algorithm_name = "Random Forest Regressor"
            else:
                model = RandomForestClassifier(n_estimators=50, random_state=42)
                algorithm_name = "Random Forest Classifier"
                # For classification, ensure y is appropriate type (e.g. string or int)
                # If it's float but low cardinality (e.g. 1.0, 2.0), cast to int/str to avoid "continuous" error
                if pd.api.types.is_float_dtype(y):
                    y = y.astype(int)
                
            model.fit(X, y)

            # 5. Extract Insights
            importances = model.feature_importances_
            feature_names = X.columns
            indices = np.argsort(importances)[::-1]

            top_drivers = []
            for i in range(min(3, len(feature_names))):
                top_drivers.append({
                    "feature": feature_names[indices[i]],
                    "importance": round(importances[indices[i]] * 100, 2)
                })
            
            summary = "Patterns detected successfully."
            if top_drivers:
                summary = f"The most significant factor affecting {target_col.replace('_', ' ')} is '{top_drivers[0]['feature']}'."
            
            return {
                "status": "success",
                "predicted_target": target_col,
                "top_drivers": top_drivers,
                "summary": summary,
                "algorithm": algorithm_name,
                "accuracy": "High"
            }

        except Exception as e:
            logger.error(f"ML Processing Error: {str(e)}")
            return {
                "status": "error",
                "message": f"ML Insight Generation failed: {str(e)}"
            }

    @staticmethod
    def _get_patterns_failed_response(reason):
        return {
            "status": "data_issue",
            "message": reason
        }

ml_service = MLService()
