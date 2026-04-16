import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class MultilevelModels:
    @staticmethod
    def linear_mixed_model(data: pd.DataFrame, dep_var: str, 
                        fixed_effects: List[str], 
                        random_effects: List[str],
                        group_var: str) -> Dict[str, Any]:
        try:
            import statsmodels.api as sm
            import statsmodels.formula.api as smf
        except ImportError:
            raise ImportError("statsmodels is required for mixed models. "
                            "Please install with: pip install statsmodels")
        
        data_clean = data[[dep_var, group_var] + fixed_effects + random_effects].dropna()
        
        fixed_part = ' + '.join(fixed_effects)
        random_part = ' + '.join([f'(1 | {group_var})'])
        
        formula = f'{dep_var} ~ {fixed_part}'
        
        model = smf.mixedlm(formula, data=data_clean, groups=data_clean[group_var])
        result = model.fit()
        
        return {
            '模型': model,
            '结果': result,
            '摘要': result.summary(),
            '固定效应系数': result.fe_params,
            '随机效应方差': result.cov_re,
            'AIC': result.aic,
            'BIC': result.bic
        }
    
    @staticmethod
    def two_level_model(data: pd.DataFrame, dep_var: str,
                       level1_vars: List[str],
                       level2_vars: List[str],
                       group_var: str) -> Dict[str, Any]:
        try:
            import statsmodels.api as sm
            import statsmodels.formula.api as smf
        except ImportError:
            raise ImportError("statsmodels is required for mixed models. "
                            "Please install with: pip install statsmodels")
        
        all_vars = level1_vars + level2_vars
        data_clean = data[[dep_var, group_var] + all_vars].dropna()
        
        fixed_part = ' + '.join(all_vars)
        formula = f'{dep_var} ~ {fixed_part}'
        
        model = smf.mixedlm(formula, data=data_clean, groups=data_clean[group_var])
        result = model.fit()
        
        return {
            '模型': model,
            '结果': result,
            '摘要': result.summary(),
            '系数': result.fe_params,
            '随机效应': result.cov_re,
            'AIC': result.aic,
            'BIC': result.bic,
            '组内相关系数': result.scale / (result.scale + result.cov_re.iloc[0, 0])
        }
    
    @staticmethod
    def random_slope_model(data: pd.DataFrame, dep_var: str,
                          fixed_effects: List[str],
                          random_slope_var: str,
                          group_var: str) -> Dict[str, Any]:
        try:
            import statsmodels.api as sm
            import statsmodels.formula.api as smf
        except ImportError:
            raise ImportError("statsmodels is required for mixed models. "
                            "Please install with: pip install statsmodels")
        
        data_clean = data[[dep_var, group_var, random_slope_var] + fixed_effects].dropna()
        
        fixed_part = ' + '.join(fixed_effects + [random_slope_var])
        formula = f'{dep_var} ~ {fixed_part}'
        
        model = smf.mixedlm(formula, data=data_clean, groups=data_clean[group_var],
                            re_formula=f'~ {random_slope_var}')
        result = model.fit()
        
        return {
            '模型': model,
            '结果': result,
            '摘要': result.summary(),
            '固定效应': result.fe_params,
            '随机效应': result.cov_re,
            'AIC': result.aic,
            'BIC': result.bic
        }
    
    @staticmethod
    def growth_curve_model(data: pd.DataFrame, dep_var: str,
                          time_var: str,
                          group_var: str,
                          covariates: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            import statsmodels.api as sm
            import statsmodels.formula.api as smf
        except ImportError:
            raise ImportError("statsmodels is required for growth curve models. "
                            "Please install with: pip install statsmodels")
        
        all_vars = [time_var] + (covariates or [])
        data_clean = data[[dep_var, group_var] + all_vars].dropna()
        
        formula_parts = [dep_var, '~', time_var]
        if covariates:
            formula_parts.extend([' + ' + ' + '.join(covariates)])
        
        formula = ''.join(formula_parts)
        
        model = smf.mixedlm(formula, data=data_clean, groups=data_clean[group_var],
                            re_formula=f'~ {time_var}')
        result = model.fit()
        
        return {
            '模型': model,
            '结果': result,
            '摘要': result.summary(),
            '固定效应': result.fe_params,
            '随机效应': result.cov_re,
            'AIC': result.aic,
            'BIC': result.bic
        }
