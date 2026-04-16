import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols, logit
from scipy import stats
from typing import Dict, List, Tuple, Optional, Union, Any


class RegressionAnalysis:
    @staticmethod
    def simple_linear_regression(data: pd.DataFrame, x_var: str, y_var: str) -> Dict[str, Any]:
        data_clean = data[[x_var, y_var]].dropna()
        
        X = sm.add_constant(data_clean[x_var])
        model = sm.OLS(data_clean[y_var], X).fit()
        
        return {
            '模型': model,
            '摘要': model.summary(),
            '系数': model.params,
            'p值': model.pvalues,
            'R平方': model.rsquared,
            '调整R平方': model.rsquared_adj,
            'F统计量': model.fvalue,
            'F统计量p值': model.f_pvalue,
            'AIC': model.aic,
            'BIC': model.bic
        }
    
    @staticmethod
    def multiple_linear_regression(data: pd.DataFrame, y_var: str, x_vars: List[str]) -> Dict[str, Any]:
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = sm.add_constant(data_clean[x_vars])
        model = sm.OLS(data_clean[y_var], X).fit()
        
        vif = pd.DataFrame()
        vif['变量'] = x_vars
        from statsmodels.stats.outliers_influence import variance_inflation_factor
        vif['VIF'] = [variance_inflation_factor(X.values, i+1) for i in range(len(x_vars))]
        
        return {
            '模型': model,
            '摘要': model.summary(),
            '系数': model.params,
            'p值': model.pvalues,
            'R平方': model.rsquared,
            '调整R平方': model.rsquared_adj,
            'F统计量': model.fvalue,
            'F统计量p值': model.f_pvalue,
            'AIC': model.aic,
            'BIC': model.bic,
            'VIF': vif
        }
    
    @staticmethod
    def logistic_regression(data: pd.DataFrame, y_var: str, x_vars: List[str]) -> Dict[str, Any]:
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = sm.add_constant(data_clean[x_vars])
        model = sm.Logit(data_clean[y_var], X).fit()
        
        odds_ratios = np.exp(model.params)
        ci = np.exp(model.conf_int())
        ci.columns = ['OR_下限', 'OR_上限']
        
        return {
            '模型': model,
            '摘要': model.summary(),
            '系数': model.params,
            'p值': model.pvalues,
            '优势比': odds_ratios,
            '优势比置信区间': ci,
            '伪R平方': model.prsquared,
            'AIC': model.aic,
            'BIC': model.bic
        }
    
    @staticmethod
    def ridge_regression(data: pd.DataFrame, y_var: str, x_vars: List[str], alpha: float = 1.0) -> Dict[str, Any]:
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data_clean[x_vars])
        
        model = Ridge(alpha=alpha)
        model.fit(X_scaled, data_clean[y_var])
        
        r2 = model.score(X_scaled, data_clean[y_var])
        
        return {
            '模型': model,
            '系数': pd.Series(model.coef_, index=x_vars),
            '截距': model.intercept_,
            'R平方': r2,
            'alpha': alpha
        }
    
    @staticmethod
    def lasso_regression(data: pd.DataFrame, y_var: str, x_vars: List[str], alpha: float = 1.0) -> Dict[str, Any]:
        from sklearn.linear_model import Lasso
        from sklearn.preprocessing import StandardScaler
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data_clean[x_vars])
        
        model = Lasso(alpha=alpha)
        model.fit(X_scaled, data_clean[y_var])
        
        r2 = model.score(X_scaled, data_clean[y_var])
        
        return {
            '模型': model,
            '系数': pd.Series(model.coef_, index=x_vars),
            '截距': model.intercept_,
            'R平方': r2,
            'alpha': alpha
        }
    
    @staticmethod
    def elastic_net_regression(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                                alpha: float = 1.0, l1_ratio: float = 0.5) -> Dict[str, Any]:
        from sklearn.linear_model import ElasticNet
        from sklearn.preprocessing import StandardScaler
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(data_clean[x_vars])
        
        model = ElasticNet(alpha=alpha, l1_ratio=l1_ratio)
        model.fit(X_scaled, data_clean[y_var])
        
        r2 = model.score(X_scaled, data_clean[y_var])
        
        return {
            '模型': model,
            '系数': pd.Series(model.coef_, index=x_vars),
            '截距': model.intercept_,
            'R平方': r2,
            'alpha': alpha,
            'l1_ratio': l1_ratio
        }
    
    @staticmethod
    def quantile_regression(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                            quantile: float = 0.5) -> Dict[str, Any]:
        data_clean = data[[y_var] + x_vars].dropna()
        
        formula = f'{y_var} ~ {" + ".join(x_vars)}'
        model = sm.QuantReg.from_formula(formula, data=data_clean).fit(q=quantile)
        
        return {
            '模型': model,
            '摘要': model.summary(),
            '系数': model.params,
            'p值': model.pvalues,
            '分位数': quantile
        }
