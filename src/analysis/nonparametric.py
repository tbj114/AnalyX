import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union, Any


class NonparametricTests:
    @staticmethod
    def sign_test(data1: pd.Series, data2: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([data1, data2], axis=1).dropna()
        diff = data_clean.iloc[:, 0] - data_clean.iloc[:, 1]
        
        n_pos = (diff > 0).sum()
        n_neg = (diff < 0).sum()
        n = n_pos + n_neg
        
        p_value = 2 * min(stats.binom.cdf(min(n_pos, n_neg), n, 0.5), 
                          1 - stats.binom.cdf(max(n_pos, n_neg) - 1, n, 0.5))
        
        return {
            '正差值数': n_pos,
            '负差值数': n_neg,
            '有效对数': n,
            'p值': p_value
        }
    
    @staticmethod
    def runs_test(data: pd.Series) -> Dict[str, float]:
        from statsmodels.sandbox.stats.runs import runstest_1samp
        
        data_clean = data.dropna()
        median = data_clean.median()
        runs_data = (data_clean > median).astype(int)
        
        z_stat, p_value = runstest_1samp(runs_data)
        
        return {
            'Z统计量': z_stat,
            'p值': p_value
        }
    
    @staticmethod
    def kolmogorov_smirnov_test(data: pd.Series, dist: str = 'norm') -> Dict[str, float]:
        data_clean = data.dropna()
        
        if dist == 'norm':
            d_stat, p_value = stats.kstest(data_clean, 'norm', 
                                           args=(data_clean.mean(), data_clean.std()))
        else:
            d_stat, p_value = stats.kstest(data_clean, dist)
        
        return {
            'D统计量': d_stat,
            'p值': p_value
        }
    
    @staticmethod
    def shapiro_wilk_test(data: pd.Series) -> Dict[str, float]:
        data_clean = data.dropna()
        
        w_stat, p_value = stats.shapiro(data_clean)
        
        return {
            'W统计量': w_stat,
            'p值': p_value
        }
    
    @staticmethod
    def mood_median_test(*data: pd.Series) -> Dict[str, float]:
        data_clean = [d.dropna() for d in data]
        all_data = np.concatenate(data_clean)
        median = np.median(all_data)
        
        from scipy.stats import median_test
        stat, p_value, med, table = median_test(*data_clean)
        
        return {
            '统计量': stat,
            'p值': p_value,
            '总中位数': med,
            '列联表': table
        }
    
    @staticmethod
    def cochran_q_test(*data: pd.Series) -> Dict[str, float]:
        from statsmodels.stats.contingency_tables import cochrans_q
        
        data_clean = pd.concat(data, axis=1).dropna()
        
        result = cochrans_q(data_clean)
        
        return {
            'Q统计量': result.statistic,
            'p值': result.pvalue,
            '自由度': result.df
        }
