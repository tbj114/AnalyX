import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class SpatialAnalysis:
    @staticmethod
    def morans_i(data: pd.Series, weights_matrix) -> Dict[str, float]:
        try:
            from libpysal.weights import W
            from esda.moran import Moran
        except ImportError:
            raise ImportError("libpysal and esda are required for spatial analysis. "
                            "Please install with: pip install libpysal esda")
        
        data_clean = data.dropna()
        
        moran = Moran(data_clean, weights_matrix)
        
        return {
            'Moran\'s I': moran.I,
            '期望值': moran.EI,
            '方差': moran.VI,
            'z值': moran.z_sim,
            'p值': moran.p_sim
        }
    
    @staticmethod
    def gearys_c(data: pd.Series, weights_matrix) -> Dict[str, float]:
        try:
            from libpysal.weights import W
            from esda.geary import Geary
        except ImportError:
            raise ImportError("libpysal and esda are required for spatial analysis. "
                            "Please install with: pip install libpysal esda")
        
        data_clean = data.dropna()
        
        geary = Geary(data_clean, weights_matrix)
        
        return {
            'Geary\'s C': geary.C,
            '期望值': geary.EC,
            '方差': geary.VC,
            'z值': geary.z,
            'p值': geary.p_sim
        }
    
    @staticmethod
    def getis_ord_g(data: pd.Series, weights_matrix) -> Dict[str, float]:
        try:
            from libpysal.weights import W
            from esda.getisord import G
        except ImportError:
            raise ImportError("libpysal and esda are required for spatial analysis. "
                            "Please install with: pip install libpysal esda")
        
        data_clean = data.dropna()
        
        g = G(data_clean, weights_matrix)
        
        return {
            'Getis-Ord G': g.G,
            '期望值': g.EG,
            '方差': g.VG,
            'z值': g.z,
            'p值': g.p_sim
        }
    
    @staticmethod
    def spatial_lag_model(data: pd.DataFrame, y_var: str, x_vars: List[str],
                        weights_matrix) -> Dict[str, Any]:
        try:
            from libpysal.weights import W
            from spreg import ML_Lag
        except ImportError:
            raise ImportError("libpysal and spreg are required for spatial regression. "
                            "Please install with: pip install libpysal spreg")
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        y = data_clean[y_var].values.reshape(-1, 1)
        X = data_clean[x_vars].values
        
        model = ML_Lag(y, X, w=weights_matrix)
        
        return {
            '模型': model,
            '系数': model.betas,
            '对数似然': model.logll,
            'AIC': model.aic,
            'Schwarz准则': model.schwarz
        }
    
    @staticmethod
    def spatial_error_model(data: pd.DataFrame, y_var: str, x_vars: List[str],
                         weights_matrix) -> Dict[str, Any]:
        try:
            from libpysal.weights import W
            from spreg import ML_Error
        except ImportError:
            raise ImportError("libpysal and spreg are required for spatial regression. "
                            "Please install with: pip install libpysal spreg")
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        y = data_clean[y_var].values.reshape(-1, 1)
        X = data_clean[x_vars].values
        
        model = ML_Error(y, X, w=weights_matrix)
        
        return {
            '模型': model,
            '系数': model.betas,
            '对数似然': model.logll,
            'AIC': model.aic,
            'Schwarz准则': model.schwarz
        }
