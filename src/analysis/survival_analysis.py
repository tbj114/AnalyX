import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class SurvivalAnalysis:
    @staticmethod
    def kaplan_meier_estimator(time: pd.Series, event: pd.Series) -> Dict[str, Any]:
        from lifelines import KaplanMeierFitter
        
        data_clean = pd.concat([time, event], axis=1).dropna()
        
        kmf = KaplanMeierFitter()
        kmf.fit(data_clean.iloc[:, 0], event_observed=data_clean.iloc[:, 1])
        
        return {
            '模型': kmf,
            '生存函数': kmf.survival_function_,
            '累计风险': kmf.cumulative_density_,
            '中位生存时间': kmf.median_survival_time_
        }
    
    @staticmethod
    def log_rank_test(time1: pd.Series, event1: pd.Series, 
                      time2: pd.Series, event2: pd.Series) -> Dict[str, float]:
        from lifelines.statistics import logrank_test
        
        data1_clean = pd.concat([time1, event1], axis=1).dropna()
        data2_clean = pd.concat([time2, event2], axis=1).dropna()
        
        result = logrank_test(data1_clean.iloc[:, 0], data2_clean.iloc[:, 0],
                              data1_clean.iloc[:, 1], data2_clean.iloc[:, 1])
        
        return {
            '卡方统计量': result.test_statistic,
            'p值': result.p_value,
            '自由度': result.degrees_of_freedom
        }
    
    @staticmethod
    def cox_ph_regression(data: pd.DataFrame, time_var: str, event_var: str, 
                          covariates: List[str]) -> Dict[str, Any]:
        from lifelines import CoxPHFitter
        
        data_clean = data[[time_var, event_var] + covariates].dropna()
        
        cph = CoxPHFitter()
        cph.fit(data_clean, duration_col=time_var, event_col=event_var)
        
        return {
            '模型': cph,
            '摘要': cph.summary(),
            '系数': cph.params_,
            '风险比': np.exp(cph.params_),
            'p值': cph.pvalues_,
            'AIC': cph.AIC_partial_,
            '一致性指数': cph.concordance_index_
        }
    
    @staticmethod
    def weibull_aft_model(data: pd.DataFrame, time_var: str, event_var: str, 
                          covariates: List[str]) -> Dict[str, Any]:
        from lifelines import WeibullAFTFitter
        
        data_clean = data[[time_var, event_var] + covariates].dropna()
        
        model = WeibullAFTFitter()
        model.fit(data_clean, duration_col=time_var, event_col=event_var)
        
        return {
            '模型': model,
            '摘要': model.summary(),
            '系数': model.params_,
            'AIC': model.AIC_,
            '一致性指数': model.concordance_index_
        }
    
    @staticmethod
    def nelson_aalen_estimator(time: pd.Series, event: pd.Series) -> Dict[str, Any]:
        from lifelines import NelsonAalenFitter
        
        data_clean = pd.concat([time, event], axis=1).dropna()
        
        naf = NelsonAalenFitter()
        naf.fit(data_clean.iloc[:, 0], event_observed=data_clean.iloc[:, 1])
        
        return {
            '模型': naf,
            '累计风险函数': naf.cumulative_hazard_
        }
