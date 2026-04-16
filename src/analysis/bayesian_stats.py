import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class BayesianStats:
    @staticmethod
    def bayesian_linear_regression(data: pd.DataFrame, y_var: str, x_vars: List[str],
                                    draws: int = 1000, tune: int = 1000,
                                    chains: int = 2) -> Dict[str, Any]:
        try:
            import pymc as pm
            import arviz as az
        except ImportError:
            raise ImportError("PyMC3 and ArviZ are required for Bayesian analysis. "
                            "Please install with: pip install pymc arviz")
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        with pm.Model() as model:
            sigma = pm.HalfNormal('sigma', 10)
            intercept = pm.Normal('intercept', mu=0, sigma=10)
            
            beta = pm.Normal('beta', mu=0, sigma=10, shape=len(x_vars))
            
            mu = intercept + pm.math.dot(data_clean[x_vars].values, beta)
            
            likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, 
                                   observed=data_clean[y_var].values)
            
            trace = pm.sample(draws, tune=tune, chains=chains, return_inferencedata=True)
        
        summary = az.summary(trace)
        
        return {
            '模型': model,
            '追踪': trace,
            '摘要': summary,
            '后验预测': pm.sample_posterior_predictive(trace, model=model)
        }
    
    @staticmethod
    def bayesian_logistic_regression(data: pd.DataFrame, y_var: str, x_vars: List[str],
                                      draws: int = 1000, tune: int = 1000,
                                      chains: int = 2) -> Dict[str, Any]:
        try:
            import pymc as pm
            import arviz as az
        except ImportError:
            raise ImportError("PyMC3 and ArviZ are required for Bayesian analysis. "
                            "Please install with: pip install pymc arviz")
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        with pm.Model() as model:
            intercept = pm.Normal('intercept', mu=0, sigma=10)
            beta = pm.Normal('beta', mu=0, sigma=10, shape=len(x_vars))
            
            mu = pm.math.sigmoid(intercept + pm.math.dot(data_clean[x_vars].values, beta))
            
            likelihood = pm.Bernoulli('likelihood', p=mu, 
                                      observed=data_clean[y_var].values)
            
            trace = pm.sample(draws, tune=tune, chains=chains, return_inferencedata=True)
        
        summary = az.summary(trace)
        
        return {
            '模型': model,
            '追踪': trace,
            '摘要': summary,
            '后验预测': pm.sample_posterior_predictive(trace, model=model)
        }
    
    @staticmethod
    def bayesian_t_test(data1: pd.Series, data2: pd.Series,
                       draws: int = 1000, tune: int = 1000,
                       chains: int = 2) -> Dict[str, Any]:
        try:
            import pymc as pm
            import arviz as az
        except ImportError:
            raise ImportError("PyMC3 and ArviZ are required for Bayesian analysis. "
                            "Please install with: pip install pymc arviz")
        
        data1_clean = data1.dropna()
        data2_clean = data2.dropna()
        
        pooled_mean = np.mean(np.concatenate([data1_clean, data2_clean]))
        pooled_std = np.std(np.concatenate([data1_clean, data2_clean]))
        
        with pm.Model() as model:
            group1_mean = pm.Normal('group1_mean', mu=pooled_mean, sigma=pooled_std * 2)
            group2_mean = pm.Normal('group2_mean', mu=pooled_mean, sigma=pooled_std * 2)
            
            group1_std = pm.HalfNormal('group1_std', sigma=pooled_std * 2)
            group2_std = pm.HalfNormal('group2_std', sigma=pooled_std * 2)
            
            nu = pm.Exponential('nu', lam=1/29) + 1
            
            group1 = pm.StudentT('group1', nu=nu, mu=group1_mean, 
                                 sigma=group1_std, observed=data1_clean)
            group2 = pm.StudentT('group2', nu=nu, mu=group2_mean, 
                                 sigma=group2_std, observed=data2_clean)
            
            diff_of_means = pm.Deterministic('diff_of_means', group1_mean - group2_mean)
            diff_of_stds = pm.Deterministic('diff_of_stds', group1_std - group2_std)
            effect_size = pm.Deterministic('effect_size', 
                                           diff_of_means / np.sqrt((group1_std**2 + group2_std**2) / 2))
            
            trace = pm.sample(draws, tune=tune, chains=chains, return_inferencedata=True)
        
        summary = az.summary(trace)
        
        return {
            '模型': model,
            '追踪': trace,
            '摘要': summary
        }
    
    @staticmethod
    def bayesian_anova(data: pd.DataFrame, group_var: str, value_var: str,
                      draws: int = 1000, tune: int = 1000,
                      chains: int = 2) -> Dict[str, Any]:
        try:
            import pymc as pm
            import arviz as az
        except ImportError:
            raise ImportError("PyMC3 and ArviZ are required for Bayesian analysis. "
                            "Please install with: pip install pymc arviz")
        
        data_clean = data[[group_var, value_var]].dropna()
        groups = data_clean[group_var].unique()
        n_groups = len(groups)
        
        group_indices = pd.Categorical(data_clean[group_var]).codes
        grand_mean = data_clean[value_var].mean()
        grand_std = data_clean[value_var].std()
        
        with pm.Model() as model:
            sigma = pm.HalfNormal('sigma', sigma=grand_std * 2)
            
            group_means = pm.Normal('group_means', mu=grand_mean, sigma=grand_std * 2, shape=n_groups)
            
            mu = group_means[group_indices]
            
            likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, 
                                   observed=data_clean[value_var].values)
            
            trace = pm.sample(draws, tune=tune, chains=chains, return_inferencedata=True)
        
        summary = az.summary(trace)
        
        return {
            '模型': model,
            '追踪': trace,
            '摘要': summary
        }
