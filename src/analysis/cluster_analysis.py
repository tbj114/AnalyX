import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class ClusterAnalysis:
    @staticmethod
    def kmeans_clustering(data: pd.DataFrame, n_clusters: int, 
                          random_state: int = 42) -> Dict[str, Any]:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_clean)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        clusters = kmeans.fit_predict(data_scaled)
        
        centroids = pd.DataFrame(scaler.inverse_transform(kmeans.cluster_centers_), 
                                 columns=numeric_cols,
                                 index=[f'簇{i+1}' for i in range(n_clusters)])
        
        result = data_clean.copy()
        result['聚类'] = clusters
        
        return {
            '模型': kmeans,
            '聚类结果': result,
            '聚类中心': centroids,
            '惯性': kmeans.inertia_
        }
    
    @staticmethod
    def hierarchical_clustering(data: pd.DataFrame, n_clusters: int, 
                                 method: str = 'ward') -> Dict[str, Any]:
        from sklearn.cluster import AgglomerativeClustering
        from sklearn.preprocessing import StandardScaler
        from scipy.cluster.hierarchy import linkage, dendrogram
        import matplotlib.pyplot as plt
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_clean)
        
        hierarchical = AgglomerativeClustering(n_clusters=n_clusters, linkage=method)
        clusters = hierarchical.fit_predict(data_scaled)
        
        result = data_clean.copy()
        result['聚类'] = clusters
        
        Z = linkage(data_scaled, method=method)
        
        return {
            '模型': hierarchical,
            '聚类结果': result,
            '链接矩阵': Z
        }
    
    @staticmethod
    def dbscan_clustering(data: pd.DataFrame, eps: float = 0.5, 
                          min_samples: int = 5) -> Dict[str, Any]:
        from sklearn.cluster import DBSCAN
        from sklearn.preprocessing import StandardScaler
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_clean)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(data_scaled)
        
        result = data_clean.copy()
        result['聚类'] = clusters
        
        n_clusters = len(set(clusters)) - (1 if -1 in clusters else 0)
        n_noise = list(clusters).count(-1)
        
        return {
            '模型': dbscan,
            '聚类结果': result,
            '聚类数': n_clusters,
            '噪声点数': n_noise
        }
    
    @staticmethod
    def silhouette_score(data: pd.DataFrame, labels: np.ndarray) -> Dict[str, float]:
        from sklearn.metrics import silhouette_score
        from sklearn.preprocessing import StandardScaler
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_clean)
        
        score = silhouette_score(data_scaled, labels)
        
        return {
            '轮廓系数': score
        }
    
    @staticmethod
    def elbow_method(data: pd.DataFrame, max_clusters: int = 10) -> Dict[str, Any]:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data_clean = data[numeric_cols].dropna()
        
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_clean)
        
        inertias = []
        for k in range(1, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(data_scaled)
            inertias.append(kmeans.inertia_)
        
        return {
            '聚类数': list(range(1, max_clusters + 1)),
            '惯性': inertias
        }
