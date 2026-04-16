import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class CausalInference:
    @staticmethod
    def propensity_score_matching(data: pd.DataFrame, treatment_var: str, 
                                  outcome_var: str, covariates: List[str],
                                  method: str = 'nearest', caliper: float = 0.05) -> Dict[str, Any]:
        try:
            from causalinference import CausalModel
        except ImportError:
            try:
                from sklearn.linear_model import LogisticRegression
                from sklearn.preprocessing import StandardScaler
                from scipy.spatial.distance import cdist
                
                data_clean = data[[treatment_var, outcome_var] + covariates].dropna()
                
                X = data_clean[covariates]
                y = data_clean[treatment_var]
                
                scaler = StandardScaler()
                X_scaled = scaler.fit_transform(X)
                
                ps_model = LogisticRegression(max_iter=1000)
                ps_model.fit(X_scaled, y)
                
                propensity_scores = ps_model.predict_proba(X_scaled)[:, 1]
                data_clean['propensity_score'] = propensity_scores
                
                treated = data_clean[data_clean[treatment_var] == 1]
                control = data_clean[data_clean[treatment_var] == 0]
                
                matched_pairs = []
                for _, treated_row in treated.iterrows():
                    ps_treated = treated_row['propensity_score']
                    distances = np.abs(control['propensity_score'] - ps_treated)
                    
                    if method == 'nearest':
                        min_dist_idx = distances.idxmin()
                        if distances[min_dist_idx] <= caliper:
                            matched_pairs.append((treated_row.name, min_dist_idx))
                            control = control.drop(min_dist_idx)
                
                matched_data = pd.concat([
                    data_clean.loc[idx] for pair in matched_pairs for idx in pair
                ], axis=1).T
                
                att = matched_data[matched_data[treatment_var] == 1][outcome_var].mean() - \
                      matched_data[matched_data[treatment_var] == 0][outcome_var].mean()
                
                return {
                    '倾向得分': propensity_scores,
                    '匹配数据': matched_data,
                    '匹配对数': len(matched_pairs),
                    '处理组平均效应(ATT)': att
                }
            except ImportError:
                raise ImportError("causalinference or scikit-learn is required for PSM. "
                                "Please install with: pip install causalinference or pip install scikit-learn")
        
        data_clean = data[[treatment_var, outcome_var] + covariates].dropna()
        
        Y = data_clean[outcome_var].values
        D = data_clean[treatment_var].values
        X = data_clean[covariates].values
        
        causal_model = CausalModel(Y, D, X)
        causal_model.est_propensity()
        causal_model.est_via_matching()
        
        return {
            '模型': causal_model,
            '倾向得分': causal_model.propensity['fitted'],
            '处理组平均效应(ATT)': causal_model.estimates['matching']['att'],
            '对照组平均效应(ATC)': causal_model.estimates['matching']['atc'],
            '平均处理效应(ATE)': causal_model.estimates['matching']['ate']
        }
    
    @staticmethod
    def difference_in_differences(data: pd.DataFrame, outcome_var: str, 
                                  treatment_var: str, time_var: str,
                                  covariates: Optional[List[str]] = None) -> Dict[str, Any]:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
        
        data_clean = data[[outcome_var, treatment_var, time_var] + (covariates or [])].dropna()
        
        formula = f'{outcome_var} ~ {treatment_var} * {time_var}'
        if covariates:
            formula += ' + ' + ' + '.join(covariates)
        
        model = ols(formula, data=data_clean).fit()
        
        return {
            '模型': model,
            '摘要': model.summary(),
            'DID效应': model.params[f'{treatment_var}:{time_var}'] if f'{treatment_var}:{time_var}' in model.params else None,
            'p值': model.pvalues[f'{treatment_var}:{time_var}'] if f'{treatment_var}:{time_var}' in model.pvalues else None
        }
    
    @staticmethod
    def instrumental_variables(data: pd.DataFrame, outcome_var: str, 
                              endogenous_var: str, instrument: str,
                              covariates: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            from linearmodels.iv import IV2SLS
        except ImportError:
            raise ImportError("linearmodels is required for instrumental variables. "
                            "Please install with: pip install linearmodels")
        
        data_clean = data[[outcome_var, endogenous_var, instrument] + (covariates or [])].dropna()
        
        formula_parts = [outcome_var, '~']
        if covariates:
            formula_parts.extend([f'1 + {" + ".join(covariates)} +'])
        else:
            formula_parts.append('1 +')
        
        formula_parts.extend([f'[{endogenous_var} ~ {instrument}]'])
        formula = ' '.join(formula_parts)
        
        model = IV2SLS.from_formula(formula, data=data_clean).fit()
        
        return {
            '模型': model,
            '摘要': model.summary,
            '系数': model.params,
            'p值': model.pvalues
        }
    
    @staticmethod
    def regression_discontinuity(data: pd.DataFrame, outcome_var: str, 
                                 running_var: str, cutoff: float,
                                 bandwidth: Optional[float] = None,
                                 polynomial_order: int = 1) -> Dict[str, Any]:
        import statsmodels.api as sm
        from statsmodels.formula.api import ols
        
        data_clean = data[[outcome_var, running_var]].dropna()
        
        if bandwidth is not None:
            data_clean = data_clean[(data_clean[running_var] >= cutoff - bandwidth) & 
                                   (data_clean[running_var] <= cutoff + bandwidth)]
        
        data_clean['treatment'] = (data_clean[running_var] >= cutoff).astype(int)
        data_clean['running_centered'] = data_clean[running_var] - cutoff
        
        formula_parts = [f'{outcome_var} ~ treatment + running_centered']
        for i in range(2, polynomial_order + 1):
            data_clean[f'running_centered_{i}'] = data_clean['running_centered'] ** i
            formula_parts.append(f' + running_centered_{i}')
        
        formula = ''.join(formula_parts)
        model = ols(formula, data=data_clean).fit()
        
        return {
            '模型': model,
            '摘要': model.summary(),
            '处理效应': model.params['treatment'] if 'treatment' in model.params else None,
            'p值': model.pvalues['treatment'] if 'treatment' in model.pvalues else None,
            '样本量': len(data_clean)
        }
