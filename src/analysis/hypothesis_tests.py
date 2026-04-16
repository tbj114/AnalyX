import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union, Any


class HypothesisTests:
    @staticmethod
    def one_sample_t_test(data: pd.Series, popmean: float) -> Dict[str, float]:
        data_clean = data.dropna()
        t_stat, p_value = stats.ttest_1samp(data_clean, popmean)
        
        ci = stats.t.interval(0.95, len(data_clean) - 1, loc=data_clean.mean(), 
                              scale=stats.sem(data_clean))
        
        return {
            '统计量': t_stat,
            'p值': p_value,
            '自由度': len(data_clean) - 1,
            '样本均值': data_clean.mean(),
            '样本标准差': data_clean.std(),
            '标准误': stats.sem(data_clean),
            '置信区间下限': ci[0],
            '置信区间上限': ci[1]
        }
    
    @staticmethod
    def independent_samples_t_test(data1: pd.Series, data2: pd.Series, 
                                    equal_var: bool = True) -> Dict[str, float]:
        data1_clean = data1.dropna()
        data2_clean = data2.dropna()
        
        t_stat, p_value = stats.ttest_ind(data1_clean, data2_clean, equal_var=equal_var)
        
        mean_diff = data1_clean.mean() - data2_clean.mean()
        se = np.sqrt(data1_clean.var() / len(data1_clean) + data2_clean.var() / len(data2_clean))
        df = len(data1_clean) + len(data2_clean) - 2 if equal_var else min(len(data1_clean) - 1, len(data2_clean) - 1)
        ci = stats.t.interval(0.95, df, loc=mean_diff, scale=se)
        
        return {
            '统计量': t_stat,
            'p值': p_value,
            '自由度': df,
            '组1均值': data1_clean.mean(),
            '组2均值': data2_clean.mean(),
            '均值差': mean_diff,
            '标准误': se,
            '置信区间下限': ci[0],
            '置信区间上限': ci[1]
        }
    
    @staticmethod
    def paired_samples_t_test(data1: pd.Series, data2: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([data1, data2], axis=1).dropna()
        data1_clean = data_clean.iloc[:, 0]
        data2_clean = data_clean.iloc[:, 1]
        
        t_stat, p_value = stats.ttest_rel(data1_clean, data2_clean)
        
        diff = data1_clean - data2_clean
        mean_diff = diff.mean()
        se = stats.sem(diff)
        ci = stats.t.interval(0.95, len(diff) - 1, loc=mean_diff, scale=se)
        
        return {
            '统计量': t_stat,
            'p值': p_value,
            '自由度': len(diff) - 1,
            '配对1均值': data1_clean.mean(),
            '配对2均值': data2_clean.mean(),
            '均值差': mean_diff,
            '差值标准差': diff.std(),
            '标准误': se,
            '置信区间下限': ci[0],
            '置信区间上限': ci[1]
        }
    
    @staticmethod
    def chi_square_test(data: pd.DataFrame, var1: str, var2: str) -> Dict[str, Any]:
        contingency_table = pd.crosstab(data[var1], data[var2])
        chi2_stat, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape)
        cramers_v = np.sqrt(chi2_stat / (n * (min_dim - 1)))
        
        return {
            '卡方统计量': chi2_stat,
            'p值': p_value,
            '自由度': dof,
            'Cramer\'s V': cramers_v,
            '期望频数': expected,
            '观测频数': contingency_table.values
        }
    
    @staticmethod
    def chi_square_goodness_of_fit(data: pd.Series, expected_proportions: Optional[List[float]] = None) -> Dict[str, float]:
        data_clean = data.dropna()
        observed = data_clean.value_counts().sort_index()
        
        if expected_proportions is None:
            expected_proportions = [1/len(observed)] * len(observed)
        
        expected = np.array(expected_proportions) * len(data_clean)
        chi2_stat, p_value = stats.chisquare(observed, expected)
        
        return {
            '卡方统计量': chi2_stat,
            'p值': p_value,
            '自由度': len(observed) - 1,
            '观测频数': observed.values,
            '期望频数': expected
        }
    
    @staticmethod
    def f_test(data1: pd.Series, data2: pd.Series) -> Dict[str, float]:
        data1_clean = data1.dropna()
        data2_clean = data2.dropna()
        
        var1 = data1_clean.var()
        var2 = data2_clean.var()
        f_stat = var1 / var2 if var1 >= var2 else var2 / var1
        dfn = len(data1_clean) - 1 if var1 >= var2 else len(data2_clean) - 1
        dfd = len(data2_clean) - 1 if var1 >= var2 else len(data1_clean) - 1
        p_value = 2 * min(stats.f.cdf(f_stat, dfn, dfd), 1 - stats.f.cdf(f_stat, dfn, dfd))
        
        return {
            'F统计量': f_stat,
            'p值': p_value,
            '分子自由度': dfn,
            '分母自由度': dfd,
            '组1方差': var1,
            '组2方差': var2
        }
    
    @staticmethod
    def mann_whitney_u_test(data1: pd.Series, data2: pd.Series) -> Dict[str, float]:
        data1_clean = data1.dropna()
        data2_clean = data2.dropna()
        
        u_stat, p_value = stats.mannwhitneyu(data1_clean, data2_clean, alternative='two-sided')
        
        return {
            'U统计量': u_stat,
            'p值': p_value,
            '组1样本量': len(data1_clean),
            '组2样本量': len(data2_clean)
        }
    
    @staticmethod
    def wilcoxon_signed_rank_test(data1: pd.Series, data2: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat([data1, data2], axis=1).dropna()
        data1_clean = data_clean.iloc[:, 0]
        data2_clean = data_clean.iloc[:, 1]
        
        w_stat, p_value = stats.wilcoxon(data1_clean, data2_clean)
        
        return {
            'W统计量': w_stat,
            'p值': p_value,
            '样本量': len(data_clean)
        }
    
    @staticmethod
    def kruskal_wallis_test(*data: pd.Series) -> Dict[str, float]:
        data_clean = [d.dropna() for d in data]
        
        h_stat, p_value = stats.kruskal(*data_clean)
        
        return {
            'H统计量': h_stat,
            'p值': p_value,
            '组数': len(data_clean),
            '总样本量': sum(len(d) for d in data_clean)
        }
    
    @staticmethod
    def friedman_test(*data: pd.Series) -> Dict[str, float]:
        data_clean = pd.concat(data, axis=1).dropna()
        
        chi2_stat, p_value = stats.friedmanchisquare(*[data_clean.iloc[:, i] for i in range(data_clean.shape[1])])
        
        return {
            '卡方统计量': chi2_stat,
            'p值': p_value,
            '处理数': data_clean.shape[1],
            '区组数': data_clean.shape[0]
        }
