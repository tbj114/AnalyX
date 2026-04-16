import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class NetworkAnalysis:
    @staticmethod
    def create_network(nodes: List[Optional[List[str]]] = None,
                   edges: Optional[pd.DataFrame] = None,
                   directed: bool = False) -> Dict[str, Any]:
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("NetworkX is required for network analysis. "
                            "Please install with: pip install networkx")
        
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
        
        if nodes is not None:
            G.add_nodes_from(nodes)
        
        if edges is not None:
            if 'weight' in edges.columns:
                for _, row in edges.iterrows():
                    G.add_edge(row.iloc[0], row.iloc[1], weight=row.get('weight', 1))
            else:
                for _, row in edges.iterrows():
                    G.add_edge(row.iloc[0], row.iloc[1])
        
        return {
            '图': G,
            '节点数': G.number_of_nodes(),
            '边数': G.number_of_edges(),
            '有向': directed
        }
    
    @staticmethod
    def network_metrics(graph) -> Dict[str, Any]:
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("NetworkX is required for network analysis. "
                            "Please install with: pip install networkx")
        
        G = graph
        
        metrics = {
            '节点数': G.number_of_nodes(),
            '边数': G.number_of_edges(),
            '平均度': np.mean([d for _, d in G.degree()]),
            '密度': nx.density(G),
            '平均聚类系数': nx.average_clustering(G),
            '连通分量数': nx.number_connected_components(G) if not G.is_directed() else None
        }
        
        if G.number_of_nodes() > 0 and nx.is_connected(G):
            metrics['平均最短路径长度'] = nx.average_shortest_path_length(G)
            metrics['直径'] = nx.diameter(G)
        
        return metrics
    
    @staticmethod
    def centrality_measures(graph) -> Dict[str, Any]:
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("NetworkX is required for network analysis. "
                            "Please install with: pip install networkx")
        
        G = graph
        
        return {
            '度中心性': pd.Series(nx.degree_centrality(G)),
            '接近中心性': pd.Series(nx.closeness_centrality(G)),
            '介数中心性': pd.Series(nx.betweenness_centrality(G)),
            '特征向量中心性': pd.Series(nx.eigenvector_centrality(G, max_iter=1000))
        }
    
    @staticmethod
    def community_detection(graph, method: str = 'louvain') -> Dict[str, Any]:
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("NetworkX is required for network analysis. "
                            "Please install with: pip install networkx")
        
        G = graph
        
        if method == 'louvain':
            try:
                import community as community_louvain
            except ImportError:
                raise ImportError("python-louvain is required for Louvain method. "
                                "Please install with: pip install python-louvain")
            
            partition = community_louvain.best_partition(G)
        elif method == 'greedy':
            partition = nx.algorithms.community.greedy_modularity_communities(G)
            partition = {node: i for i, comm in enumerate(partition) for node in comm}
        else:
            raise ValueError(f"Unknown method: {method}")
        
        communities = pd.Series(partition)
        
        return {
            '社区分配': communities,
            '社区数': communities.nunique()
        }
    
    @staticmethod
    def draw_network(graph, layout: str = 'spring', **kwargs) -> Dict[str, Any]:
        try:
            import networkx as nx
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError("NetworkX and Matplotlib are required for network visualization. "
                            "Please install with: pip install networkx matplotlib")
        
        G = graph
        
        if layout == 'spring':
            pos = nx.spring_layout(G, **kwargs)
        elif layout == 'circular':
            pos = nx.circular_layout(G, **kwargs)
        elif layout == 'kamada_kawai':
            pos = nx.kamada_kawai_layout(G, **kwargs)
        elif layout == 'shell':
            pos = nx.shell_layout(G, **kwargs)
        else:
            pos = nx.spring_layout(G, **kwargs)
        
        return {
            '位置': pos,
            '图': G
        }
