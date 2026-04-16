import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class StatsLibrary:
    def __init__(self, data: Optional[pd.DataFrame] = None):
        self.data = data
        self._validate_data()
    
    def _validate_data(self):
        if self.data is not None and not isinstance(self.data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")
    
    def set_data(self, data: pd.DataFrame):
        self.data = data
        self._validate_data()
    
    def get_data(self) -> pd.DataFrame:
        return self.data
    
    def get_numeric_columns(self) -> List[str]:
        if self.data is None:
            return []
        return list(self.data.select_dtypes(include=[np.number]).columns)
    
    def get_categorical_columns(self) -> List[str]:
        if self.data is None:
            return []
        return list(self.data.select_dtypes(include=['object', 'category']).columns)
    
    def drop_missing(self, subset: Optional[List[str]] = None):
        if self.data is None:
            return
        self.data = self.data.dropna(subset=subset)
    
    def fill_missing(self, method: str = 'mean', columns: Optional[List[str]] = None):
        if self.data is None:
            return
        cols = columns if columns else self.get_numeric_columns()
        for col in cols:
            if method == 'mean':
                self.data[col] = self.data[col].fillna(self.data[col].mean())
            elif method == 'median':
                self.data[col] = self.data[col].fillna(self.data[col].median())
            elif method == 'mode':
                self.data[col] = self.data[col].fillna(self.data[col].mode().iloc[0])
    
    def normalize_column(self, column: str, method: str = 'zscore') -> pd.Series:
        if self.data is None or column not in self.data.columns:
            raise ValueError("Invalid data or column")
        
        col_data = self.data[column].dropna()
        
        if method == 'zscore':
            return (col_data - col_data.mean()) / col_data.std()
        elif method == 'minmax':
            return (col_data - col_data.min()) / (col_data.max() - col_data.min())
        elif method == 'robust':
            median = col_data.median()
            iqr = col_data.quantile(0.75) - col_data.quantile(0.25)
            return (col_data - median) / iqr
        else:
            raise ValueError(f"Unknown normalization method: {method}")
