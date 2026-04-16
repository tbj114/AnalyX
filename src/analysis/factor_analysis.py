import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class FactorAnalysis:
    @staticmethod
    def kaiser_meyer_olkin(data: pd.DataFrame) -> Dict[str, Any]:
        from factor_analyzer.factor_analyzer import calculate_kmo
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        kmo_all, kmo_model = calculate_kmo(data_clean)
        
        return {
            'KMO模型': kmo_model,
            'KMO变量': pd.Series(kmo_all, index=numeric_cols)
        }
    
    @staticmethod
    def bartlett_sphericity(data: pd.DataFrame) -> Dict[str, float]:
        from factor_analyzer.factor_analyzer import calculate_bartlett_sphericity
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        chi2_stat, p_value = calculate_bartlett_sphericity(data_clean)
        
        return {
            '卡方统计量': chi2_stat,
            'p值': p_value
        }
    
    @staticmethod
    def factor_analysis(data: pd.DataFrame, n_factors: int, method: str = 'principal',
                        rotation: str = 'varimax') -> Dict[str, Any]:
        from factor_analyzer import FactorAnalyzer
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        fa = FactorAnalyzer(n_factors=n_factors, rotation=rotation, method=method)
        fa.fit(data_clean)
        
        loadings = pd.DataFrame(fa.loadings_, 
                               index=numeric_cols, 
                               columns=[f'因子{i+1}' for i in range(n_factors)])
        
        variance = pd.DataFrame({
            '特征值': fa.get_eigenvalues()[0],
            '方差贡献率': fa.get_factor_variance()[0],
            '累积方差贡献率': fa.get_factor_variance()[2]
        }, index=[f'因子{i+1}' for i in range(len(fa.get_eigenvalues()[0]))])
        
        return {
            '模型': fa,
            '载荷矩阵': loadings,
            '方差解释': variance,
            '特征值': fa.get_eigenvalues()[0],
            '共同度': fa.get_communalities()
        }
    
    @staticmethod
    def parallel_analysis(data: pd.DataFrame) -> Dict[str, Any]:
        from factor_analyzer import FactorAnalyzer
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        fa = FactorAnalyzer()
        fa.fit(data_clean)
        
        ev, _ = fa.get_eigenvalues()
        
        return {
            '特征值': ev
        }
