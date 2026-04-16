import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union, Any


class DescriptiveStats:
    @staticmethod
    def summary(data: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
        cols = columns if columns else data.select_dtypes(include=[np.number]).columns
        results = []
        
        for col in cols:
            col_data = data[col].dropna()
            if len(col_data) == 0:
                continue
            
            result = {
                '变量': col,
                '样本量': len(col_data),
                '缺失值': data[col].isna().sum(),
                '均值': col_data.mean(),
                '标准差': col_data.std(),
                '方差': col_data.var(),
                '标准误': col_data.sem(),
                '中位数': col_data.median(),
                '众数': col_data.mode().iloc[0] if len(col_data.mode()) > 0 else np.nan,
                '最小值': col_data.min(),
                '最大值': col_data.max(),
                '25%分位数': col_data.quantile(0.25),
                '75%分位数': col_data.quantile(0.75),
                '偏度': col_data.skew(),
                '峰度': col_data.kurtosis()
            }
            results.append(result)
        
        return pd.DataFrame(results)
    
    @staticmethod
    def frequency_table(data: pd.Series, include_missing: bool = True) -> pd.DataFrame:
        freq = data.value_counts(dropna=not include_missing)
        freq_df = pd.DataFrame({
            '频数': freq,
            '百分比': (freq / len(data) * 100).round(2),
            '累积频数': freq.cumsum(),
            '累积百分比': (freq.cumsum() / len(data) * 100).round(2)
        })
        return freq_df
    
    @staticmethod
    def cross_table(data: pd.DataFrame, row_var: str, col_var: str, 
                    margins: bool = True, normalize: bool = False) -> pd.DataFrame:
        table = pd.crosstab(data[row_var], data[col_var], margins=margins, normalize=normalize)
        return table
    
    @staticmethod
    def normality_test(data: pd.Series) -> Dict[str, float]:
        data_clean = data.dropna()
        
        shapiro_stat, shapiro_p = stats.shapiro(data_clean) if len(data_clean) <= 5000 else (np.nan, np.nan)
        ks_stat, ks_p = stats.kstest(data_clean, 'norm', args=(data_clean.mean(), data_clean.std()))
        dagostino_stat, dagostino_p = stats.normaltest(data_clean) if len(data_clean) >= 20 else (np.nan, np.nan)
        
        return {
            'Shapiro-Wilk统计量': shapiro_stat,
            'Shapiro-Wilk p值': shapiro_p,
            'Kolmogorov-Smirnov统计量': ks_stat,
            'Kolmogorov-Smirnov p值': ks_p,
            'D\'Agostino-Pearson统计量': dagostino_stat,
            'D\'Agostino-Pearson p值': dagostino_p
        }
    
    @staticmethod
    def percentile(data: pd.Series, percentiles: List[float] = [0, 10, 25, 50, 75, 90, 100]) -> pd.Series:
        data_clean = data.dropna()
        return data_clean.quantile([p / 100 for p in percentiles])
    
    @staticmethod
    def cv(data: pd.Series) -> float:
        data_clean = data.dropna()
        return data_clean.std() / data_clean.mean() if data_clean.mean() != 0 else np.nan
    
    @staticmethod
    def iqr(data: pd.Series) -> float:
        data_clean = data.dropna()
        return data_clean.quantile(0.75) - data_clean.quantile(0.25)
    
    @staticmethod
    def outlier_detection(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> pd.Series:
        data_clean = data.dropna()
        
        if method == 'iqr':
            q1 = data_clean.quantile(0.25)
            q3 = data_clean.quantile(0.75)
            iqr_val = q3 - q1
            lower = q1 - threshold * iqr_val
            upper = q3 + threshold * iqr_val
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(data_clean))
            return data[z_scores > threshold]
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return data[(data < lower) | (data > upper)]
