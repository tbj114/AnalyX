import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from typing import Dict, List, Tuple, Optional, Union, Any


class ANOVA:
    @staticmethod
    def one_way_anova(data: pd.DataFrame, group_var: str, value_var: str) -> Dict[str, Any]:
        groups = [group[value_var].dropna() for _, group in data.groupby(group_var)]
        
        f_stat, p_value = stats.f_oneway(*groups)
        
        df_between = len(groups) - 1
        df_within = sum(len(g) for g in groups) - len(groups)
        
        ss_between = sum(len(g) * (g.mean() - data[value_var].mean())**2 for g in groups)
        ss_within = sum((g - g.mean()).pow(2).sum() for g in groups)
        
        ms_between = ss_between / df_between
        ms_within = ss_within / df_within
        
        eta_squared = ss_between / (ss_between + ss_within)
        
        return {
            'F统计量': f_stat,
            'p值': p_value,
            '组间自由度': df_between,
            '组内自由度': df_within,
            '组间平方和': ss_between,
            '组内平方和': ss_within,
            '组间均方': ms_between,
            '组内均方': ms_within,
            'Eta平方': eta_squared
        }
    
    @staticmethod
    def two_way_anova(data: pd.DataFrame, dep_var: str, factor1: str, factor2: str) -> Dict[str, Any]:
        formula = f'{dep_var} ~ C({factor1}) + C({factor2}) + C({factor1}):C({factor2})'
        model = ols(formula, data=data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        
        return {
            'ANOVA表': anova_table,
            '模型': model
        }
    
    @staticmethod
    def repeated_measures_anova(data: pd.DataFrame, dep_var: str, subject_var: str, within_var: str) -> Dict[str, Any]:
        from statsmodels.stats.anova import AnovaRM
        
        aovrm = AnovaRM(data, dep_var, subject_var, within=[within_var])
        fit = aovrm.fit()
        
        return {
            'ANOVA表': fit.anova_table,
            '结果': fit
        }
    
    @staticmethod
    def ancova(data: pd.DataFrame, dep_var: str, factor_var: str, covariate: str) -> Dict[str, Any]:
        formula = f'{dep_var} ~ C({factor_var}) + {covariate}'
        model = ols(formula, data=data).fit()
        anova_table = sm.stats.anova_lm(model, typ=2)
        
        return {
            'ANOVA表': anova_table,
            '模型': model
        }
    
    @staticmethod
    def tukey_hsd(data: pd.DataFrame, group_var: str, value_var: str) -> Dict[str, Any]:
        from statsmodels.stats.multicomp import pairwise_tukeyhsd
        
        data_clean = data[[group_var, value_var]].dropna()
        tukey = pairwise_tukeyhsd(endog=data_clean[value_var], groups=data_clean[group_var], alpha=0.05)
        
        return {
            '结果': tukey,
            '摘要': tukey.summary()
        }
    
    @staticmethod
    def levene_test(*data: pd.Series) -> Dict[str, float]:
        data_clean = [d.dropna() for d in data]
        
        w_stat, p_value = stats.levene(*data_clean)
        
        return {
            'W统计量': w_stat,
            'p值': p_value
        }
