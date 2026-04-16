#!/usr/bin/env python3
"""
AnalyX 专业统计数学库 - 主入口模块
"""

from .core import StatsLibrary
from .descriptive import DescriptiveStats
from .hypothesis_tests import HypothesisTests
from .regression import RegressionAnalysis
from .anova import ANOVA
from .nonparametric import NonparametricTests
from .correlation import CorrelationAnalysis
from .factor_analysis import FactorAnalysis
from .cluster_analysis import ClusterAnalysis
from .survival_analysis import SurvivalAnalysis
from .machine_learning import MachineLearning
from .deep_learning import DeepLearning
from .causal_inference import CausalInference
from .bayesian_stats import BayesianStats
from .text_mining import TextMining
from .network_analysis import NetworkAnalysis
from .spatial_analysis import SpatialAnalysis
from .multilevel_models import MultilevelModels

__version__ = "1.0.0"


def get_version():
    return __version__


def print_info():
    print(f"AnalyX 专业统计数学库 v{__version__}")
    print("=" * 50)
    print("可用模块:")
    print("  - StatsLibrary: 数据管理与预处理")
    print("  - DescriptiveStats: 描述性统计")
    print("  - HypothesisTests: 假设检验")
    print("  - RegressionAnalysis: 回归分析")
    print("  - ANOVA: 方差分析")
    print("  - NonparametricTests: 非参数检验")
    print("  - CorrelationAnalysis: 相关分析")
    print("  - FactorAnalysis: 因子分析")
    print("  - ClusterAnalysis: 聚类分析")
    print("  - SurvivalAnalysis: 生存分析")
    print("  - MachineLearning: 机器学习")
    print("  - DeepLearning: 深度学习")
    print("  - CausalInference: 因果推断")
    print("  - BayesianStats: 贝叶斯统计")
    print("  - TextMining: 文本挖掘")
    print("  - NetworkAnalysis: 网络分析")
    print("  - SpatialAnalysis: 空间计量分析")
    print("  - MultilevelModels: 多层线性模型")
    print("=" * 50)


if __name__ == "__main__":
    print_info()
