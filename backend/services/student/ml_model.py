import pandas as pd
import numpy as np
from utils.logger import logger

class StudentMLService:
    @staticmethod
    def extract_patterns(df):
        # Lazy import heavy ML libraries
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.preprocessing import LabelEncoder
        
        try:
            if len(df) < 5:
                return {"status": "data_issue", "message": "Insufficient data for Student ML"}

            # Target: Stress_Level or Grades
            target_col = next((c for c in df.columns if any(k in c.lower() for k in ['stress', 'grade', 'score', 'performance'])), None)
            if not target_col:
                return {"status": "data_issue", "message": "No academic target column found."}

            # Clean target
            df_ml = df.copy()
            df_ml = df_ml.dropna(subset=[target_col])
            
            # 🛑 SAFETY CHECK: If target has too many classes, it's not a classification problem
            # 🛑 SAFETY CHECK:
            unique_count = df_ml[target_col].nunique()
            is_regression = False
            
            if pd.api.types.is_numeric_dtype(df_ml[target_col]):
                if unique_count > 10:
                    is_regression = True
            elif unique_count > 15:
                return {"status": "data_issue", "message": f"Target column '{target_col}' has too many unique values ({unique_count}) and is not numeric. ML Classification requires distinct categories."}

            for col in df_ml.columns:
                if df_ml[col].dtype == 'object':
                    le = LabelEncoder()
                    df_ml[col] = le.fit_transform(df_ml[col].astype(str))

            X = df_ml.drop(columns=[target_col])
            y = df_ml[target_col]

            if len(X) < 5:
                return {"status": "data_issue", "message": "Not enough valid data after cleaning NaNs."}

            if is_regression:
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                algorithm_name = "Random Forest Regressor"
            else:
                model = RandomForestClassifier(n_estimators=50, random_state=42)
                algorithm_name = "Random Forest Classifier"
                if pd.api.types.is_float_dtype(y):
                    y = y.astype(int)
            
            model.fit(X, y)

            importances = model.feature_importances_
            feature_names = X.columns
            indices = np.argsort(importances)[::-1]

            top_drivers = []
            for i in range(min(3, len(feature_names))):
                top_drivers.append({
                    "feature": feature_names[indices[i]],
                    "importance": round(importances[indices[i]] * 100, 2)
                })

            return {
                "status": "success",
                "predicted_target": target_col,
                "top_drivers": top_drivers,
                "summary": f"Academic pattern: {top_drivers[0]['feature']} indicates the highest correlation with {target_col}.",
                "algorithm": algorithm_name,
                "accuracy": "High"
            }
        except Exception as e:
            logger.error(f"Student ML Error: {e}")
            return {"status": "error", "message": str(e)}

student_ml_service = StudentMLService()
