import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class MachineLearning:
    @staticmethod
    def linear_regression(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                          test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        from sklearn.linear_model import LinearRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars]
        y = data_clean[y_var]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                random_state=random_state)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        return {
            '模型': model,
            '系数': pd.Series(model.coef_, index=x_vars),
            '截距': model.intercept_,
            '训练集R平方': model.score(X_train, y_train),
            '测试集R平方': r2_score(y_test, y_pred),
            '均方误差': mean_squared_error(y_test, y_pred),
            '均方根误差': np.sqrt(mean_squared_error(y_test, y_pred)),
            '平均绝对误差': mean_absolute_error(y_test, y_pred)
        }
    
    @staticmethod
    def logistic_regression(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                            test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
        from sklearn.preprocessing import StandardScaler
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars]
        y = data_clean[y_var]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                random_state=random_state)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = LogisticRegression(random_state=random_state, max_iter=1000)
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        return {
            '模型': model,
            '系数': pd.Series(model.coef_[0], index=x_vars),
            '截距': model.intercept_[0],
            '准确率': accuracy_score(y_test, y_pred),
            '精确率': precision_score(y_test, y_pred, average='weighted'),
            '召回率': recall_score(y_test, y_pred, average='weighted'),
            'F1分数': f1_score(y_test, y_pred, average='weighted'),
            'AUC': roc_auc_score(y_test, y_proba) if len(set(y)) == 2 else np.nan,
            '混淆矩阵': confusion_matrix(y_test, y_pred)
        }
    
    @staticmethod
    def random_forest(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                      n_estimators: int = 100, test_size: float = 0.2, 
                      random_state: int = 42, classification: bool = True) -> Dict[str, Any]:
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, r2_score, mean_squared_error
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars]
        y = data_clean[y_var]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                random_state=random_state)
        
        if classification:
            model = RandomForestClassifier(n_estimators=n_estimators, random_state=random_state)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1] if len(set(y)) == 2 else None
            
            return {
                '模型': model,
                '特征重要性': pd.Series(model.feature_importances_, index=x_vars),
                '准确率': accuracy_score(y_test, y_pred),
                '精确率': precision_score(y_test, y_pred, average='weighted'),
                '召回率': recall_score(y_test, y_pred, average='weighted'),
                'F1分数': f1_score(y_test, y_pred, average='weighted'),
                'AUC': roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan
            }
        else:
            model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            return {
                '模型': model,
                '特征重要性': pd.Series(model.feature_importances_, index=x_vars),
                'R平方': r2_score(y_test, y_pred),
                '均方误差': mean_squared_error(y_test, y_pred),
                '均方根误差': np.sqrt(mean_squared_error(y_test, y_pred))
            }
    
    @staticmethod
    def support_vector_machine(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                               kernel: str = 'rbf', test_size: float = 0.2, 
                               random_state: int = 42, classification: bool = True) -> Dict[str, Any]:
        from sklearn.svm import SVC, SVR
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, r2_score, mean_squared_error
        from sklearn.preprocessing import StandardScaler
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars]
        y = data_clean[y_var]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                random_state=random_state)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if classification:
            model = SVC(kernel=kernel, probability=True, random_state=random_state)
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1] if len(set(y)) == 2 else None
            
            return {
                '模型': model,
                '准确率': accuracy_score(y_test, y_pred),
                '精确率': precision_score(y_test, y_pred, average='weighted'),
                '召回率': recall_score(y_test, y_pred, average='weighted'),
                'F1分数': f1_score(y_test, y_pred, average='weighted'),
                'AUC': roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan
            }
        else:
            model = SVR(kernel=kernel)
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            return {
                '模型': model,
                'R平方': r2_score(y_test, y_pred),
                '均方误差': mean_squared_error(y_test, y_pred),
                '均方根误差': np.sqrt(mean_squared_error(y_test, y_pred))
            }
    
    @staticmethod
    def gradient_boosting(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                          n_estimators: int = 100, learning_rate: float = 0.1,
                          test_size: float = 0.2, random_state: int = 42, 
                          classification: bool = True) -> Dict[str, Any]:
        from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, r2_score, mean_squared_error
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars]
        y = data_clean[y_var]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                random_state=random_state)
        
        if classification:
            model = GradientBoostingClassifier(n_estimators=n_estimators, 
                                                learning_rate=learning_rate, 
                                                random_state=random_state)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)[:, 1] if len(set(y)) == 2 else None
            
            return {
                '模型': model,
                '特征重要性': pd.Series(model.feature_importances_, index=x_vars),
                '准确率': accuracy_score(y_test, y_pred),
                '精确率': precision_score(y_test, y_pred, average='weighted'),
                '召回率': recall_score(y_test, y_pred, average='weighted'),
                'F1分数': f1_score(y_test, y_pred, average='weighted'),
                'AUC': roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan
            }
        else:
            model = GradientBoostingRegressor(n_estimators=n_estimators, 
                                               learning_rate=learning_rate, 
                                               random_state=random_state)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            return {
                '模型': model,
                '特征重要性': pd.Series(model.feature_importances_, index=x_vars),
                'R平方': r2_score(y_test, y_pred),
                '均方误差': mean_squared_error(y_test, y_pred),
                '均方根误差': np.sqrt(mean_squared_error(y_test, y_pred))
            }
    
    @staticmethod
    def k_nearest_neighbors(data: pd.DataFrame, y_var: str, x_vars: List[str], 
                            n_neighbors: int = 5, test_size: float = 0.2, 
                            random_state: int = 42, classification: bool = True) -> Dict[str, Any]:
        from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, r2_score, mean_squared_error
        from sklearn.preprocessing import StandardScaler
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars]
        y = data_clean[y_var]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, 
                                                                random_state=random_state)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        if classification:
            model = KNeighborsClassifier(n_neighbors=n_neighbors)
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_proba = model.predict_proba(X_test_scaled)[:, 1] if len(set(y)) == 2 else None
            
            return {
                '模型': model,
                '准确率': accuracy_score(y_test, y_pred),
                '精确率': precision_score(y_test, y_pred, average='weighted'),
                '召回率': recall_score(y_test, y_pred, average='weighted'),
                'F1分数': f1_score(y_test, y_pred, average='weighted'),
                'AUC': roc_auc_score(y_test, y_proba) if y_proba is not None else np.nan
            }
        else:
            model = KNeighborsRegressor(n_neighbors=n_neighbors)
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            return {
                '模型': model,
                'R平方': r2_score(y_test, y_pred),
                '均方误差': mean_squared_error(y_test, y_pred),
                '均方根误差': np.sqrt(mean_squared_error(y_test, y_pred))
            }
