"""
Data Context Builder - Prepares data context for AI analysis
"""
import pandas as pd
from typing import Dict, Any, List


class DataContextBuilder:
    """Builds context from DataFrame for AI consumption"""
    
    @staticmethod
    def build_context(df: pd.DataFrame, domain: str, max_rows: int = 5) -> str:
        """
        Build a comprehensive context string from DataFrame
        
        Args:
            df: Pandas DataFrame
            domain: Data domain (sales, finance, student, employee)
            max_rows: Number of sample rows to include
            
        Returns:
            Context string for AI
        """
        context_parts = []
        
        # 1. Basic Information
        context_parts.append(f"DATA DOMAIN: {domain.upper()}")
        context_parts.append(f"TOTAL ROWS: {len(df)}")
        context_parts.append(f"TOTAL COLUMNS: {len(df.columns)}")
        context_parts.append("")
        
        # 2. Column Information
        context_parts.append("COLUMNS:")
        for col in df.columns:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            
            col_info = f"  - {col} ({dtype})"
            if null_count > 0:
                col_info += f" - {null_pct:.1f}% missing"
            context_parts.append(col_info)
        context_parts.append("")
        
        # 3. Statistical Summary for Numeric Columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            context_parts.append("NUMERIC STATISTICS:")
            for col in numeric_cols:
                stats = df[col].describe()
                context_parts.append(f"  {col}:")
                context_parts.append(f"    - Mean: {stats['mean']:.2f}")
                context_parts.append(f"    - Min: {stats['min']:.2f}")
                context_parts.append(f"    - Max: {stats['max']:.2f}")
                context_parts.append(f"    - Std Dev: {stats['std']:.2f}")
            context_parts.append("")
        
        # 4. Categorical Columns Info
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            context_parts.append("CATEGORICAL COLUMNS:")
            for col in categorical_cols[:5]:  # Limit to first 5
                unique_count = df[col].nunique()
                top_values = df[col].value_counts().head(3)
                context_parts.append(f"  {col}: {unique_count} unique values")
                context_parts.append(f"    Top values: {', '.join(map(str, top_values.index.tolist()))}")
            context_parts.append("")
        
        # 5. Sample Data
        context_parts.append(f"SAMPLE DATA (first {max_rows} rows):")
        sample_df = df.head(max_rows)
        
        # Convert to readable string format
        for idx, row in sample_df.iterrows():
            row_str = ", ".join([f"{col}={row[col]}" for col in df.columns])
            context_parts.append(f"  Row {idx + 1}: {row_str}")
        
        return "\n".join(context_parts)
    
    @staticmethod
    def get_column_summary(df: pd.DataFrame) -> Dict[str, Any]:
        """Get a structured summary of columns"""
        summary = {
            'numeric_columns': [],
            'categorical_columns': [],
            'datetime_columns': [],
            'total_rows': len(df)
        }
        
        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': float((df[col].isnull().sum() / len(df)) * 100)
            }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['stats'] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median())
                }
                summary['numeric_columns'].append(col_info)
            
            elif pd.api.types.is_object_dtype(df[col]):
                col_info['unique_count'] = int(df[col].nunique())
                col_info['top_values'] = df[col].value_counts().head(5).to_dict()
                summary['categorical_columns'].append(col_info)
            
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info['min_date'] = str(df[col].min())
                col_info['max_date'] = str(df[col].max())
                summary['datetime_columns'].append(col_info)
        
        return summary
