import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class DeepLearning:
    @staticmethod
    def neural_network_classifier(data: pd.DataFrame, y_var: str, x_vars: List[str],
                                  hidden_layers: List[int] = [64, 32], 
                                  activation: str = 'relu',
                                  epochs: int = 100, batch_size: int = 32,
                                  test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout
            from tensorflow.keras.optimizers import Adam
            from tensorflow.keras.utils import to_categorical
        except ImportError:
            raise ImportError("TensorFlow/Keras is required for deep learning models. "
                            "Please install it with: pip install tensorflow")
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars].values
        y = data_clean[y_var].values
        
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        n_classes = len(le.classes_)
        
        if n_classes == 2:
            y_categorical = y_encoded
            loss = 'binary_crossentropy'
            output_activation = 'sigmoid'
        else:
            y_categorical = to_categorical(y_encoded)
            loss = 'categorical_crossentropy'
            output_activation = 'softmax'
        
        X_train, X_test, y_train, y_test = train_test_split(X, y_categorical, 
                                                                test_size=test_size, 
                                                                random_state=random_state,
                                                                stratify=y_encoded if n_classes > 1 else None)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = Sequential()
        model.add(Dense(hidden_layers[0], input_dim=X.shape[1], activation=activation))
        model.add(Dropout(0.5))
        
        for units in hidden_layers[1:]:
            model.add(Dense(units, activation=activation))
            model.add(Dropout(0.5))
        
        if n_classes == 2:
            model.add(Dense(1, activation=output_activation))
        else:
            model.add(Dense(n_classes, activation=output_activation))
        
        model.compile(loss=loss, optimizer=Adam(), metrics=['accuracy'])
        
        history = model.fit(X_train_scaled, y_train, 
                           epochs=epochs, batch_size=batch_size, 
                           validation_split=0.2, verbose=0)
        
        y_pred_proba = model.predict(X_test_scaled, verbose=0)
        
        if n_classes == 2:
            y_pred = (y_pred_proba > 0.5).astype(int).flatten()
            y_test_class = y_test
        else:
            y_pred = np.argmax(y_pred_proba, axis=1)
            y_test_class = np.argmax(y_test, axis=1)
        
        return {
            '模型': model,
            '历史': history.history,
            '标签编码器': le,
            '类别数': n_classes,
            '准确率': accuracy_score(y_test_class, y_pred),
            '精确率': precision_score(y_test_class, y_pred, average='weighted'),
            '召回率': recall_score(y_test_class, y_pred, average='weighted'),
            'F1分数': f1_score(y_test_class, y_pred, average='weighted'),
            'AUC': roc_auc_score(y_test, y_pred_proba, multi_class='ovr') if n_classes > 2 else roc_auc_score(y_test, y_pred_proba)
        }
    
    @staticmethod
    def neural_network_regressor(data: pd.DataFrame, y_var: str, x_vars: List[str],
                                hidden_layers: List[int] = [64, 32], 
                                activation: str = 'relu',
                                epochs: int = 100, batch_size: int = 32,
                                test_size: float = 0.2, random_state: int = 42) -> Dict[str, Any]:
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        
        try:
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Dense, Dropout
            from tensorflow.keras.optimizers import Adam
        except ImportError:
            raise ImportError("TensorFlow/Keras is required for deep learning models. "
                            "Please install it with: pip install tensorflow")
        
        data_clean = data[[y_var] + x_vars].dropna()
        
        X = data_clean[x_vars].values
        y = data_clean[y_var].values
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                                test_size=test_size, 
                                                                random_state=random_state)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        y_scaler = StandardScaler()
        y_train_scaled = y_scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
        
        model = Sequential()
        model.add(Dense(hidden_layers[0], input_dim=X.shape[1], activation=activation))
        model.add(Dropout(0.5))
        
        for units in hidden_layers[1:]:
            model.add(Dense(units, activation=activation))
            model.add(Dropout(0.5))
        
        model.add(Dense(1, activation='linear'))
        
        model.compile(loss='mean_squared_error', optimizer=Adam())
        
        history = model.fit(X_train_scaled, y_train_scaled, 
                           epochs=epochs, batch_size=batch_size, 
                           validation_split=0.2, verbose=0)
        
        y_pred_scaled = model.predict(X_test_scaled, verbose=0).flatten()
        y_pred = y_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        
        return {
            '模型': model,
            '历史': history.history,
            'R平方': r2_score(y_test, y_pred),
            '均方误差': mean_squared_error(y_test, y_pred),
            '均方根误差': np.sqrt(mean_squared_error(y_test, y_pred)),
            '平均绝对误差': mean_absolute_error(y_test, y_pred)
        }
