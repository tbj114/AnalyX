import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union, Any


class CorrelationAnalysis:
    @staticmethod
    def pearson_correlation(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([x, y], axis=1).dropna()
        x_clean = data_clean.iloc[:, 0]
        y_clean = data_clean.iloc[:, 1]
        
        r, p_value = stats.pearsonr(x_clean, y_clean)
        
        n = len(data_clean)
        se = np.sqrt((1 - r**2) / (n - 2))
        z = np.arctanh(r)
        ci_z_low = z - stats.norm.ppf(0.975) * np.sqrt(1 / (n - 3))
        ci_z_high = z + stats.norm.ppf(0.975) * np.sqrt(1 / (n - 3))
        ci_low = np.tanh(ci_z_low)
        ci_high = np.tanh(ci_z_high)
        
        return {
            'Pearson相关系数': r,
            'p值': p_value,
            '样本量': n,
            '标准误': se,
            '置信区间下限': ci_low,
            '置信区间上限': ci_high
        }
    
    @staticmethod
    def spearman_correlation(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([x, y], axis=1).dropna()
        x_clean = data_clean.iloc[:, 0]
        y_clean = data_clean.iloc[:, 1]
        
        rho, p_value = stats.spearmanr(x_clean, y_clean)
        
        return {
            'Spearman秩相关系数': rho,
            'p值': p_value,
            '样本量': len(data_clean)
        }
    
    @staticmethod
    def kendall_correlation(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([x, y], axis=1).dropna()
        x_clean = data_clean.iloc[:, 0]
        y_clean = data_clean.iloc[:, 1]
        
        tau, p_value = stats.kendalltau(x_clean, y_clean)
        
        return {
            'Kendall tau系数': tau,
            'p值': p_value,
            '样本量': len(data_clean)
        }
    
    @staticmethod
    def partial_correlation(data: pd.DataFrame, x_var: str, y_var: str, control_vars: List[str]) -> Dict[str, float]:
        from pingouin import partial_corr
        
        data_clean = data[[x_var, y_var] + control_vars].dropna()
        
        result = partial_corr(data=data_clean, x=x_var, y=y_var, covar=control_vars)
        
        return {
            '偏相关系数': result['r'].values[0],
            'p值': result['p-val'].values[0],
            '自由度': result['df'].values[0],
            '置信区间下限': result['CI95%'].values[0][0],
            '置信区间上限': result['CI95%'].values[0][1]
        }
    
    @staticmethod
    def correlation_matrix(data: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        return data[numeric_cols].corr(method=method)
    
    @staticmethod
    def point_biserial_correlation(x: pd.Series, y: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([x, y], axis=1).dropna()
        x_clean = data_clean.iloc[:, 0]
        y_clean = data_clean.iloc[:, 1]
        
        r, p_value = stats.pointbiserialr(x_clean, y_clean)
        
        return {
            '点二列相关系数': r,
            'p值': p_value,
            '样本量': len(data_clean)
        }
