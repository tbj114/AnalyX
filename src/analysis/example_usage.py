import numpy as np
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import StatsLibrary
from descriptive import DescriptiveStats
from hypothesis_tests import HypothesisTests
from regression import RegressionAnalysis
from anova import ANOVA
from nonparametric import NonparametricTests
from correlation import CorrelationAnalysis
from factor_analysis import FactorAnalysis
from cluster_analysis import ClusterAnalysis
from survival_analysis import SurvivalAnalysis
from machine_learning import MachineLearning
from deep_learning import DeepLearning
from causal_inference import CausalInference
from bayesian_stats import BayesianStats
from text_mining import TextMining
from network_analysis import NetworkAnalysis
from spatial_analysis import SpatialAnalysis
from multilevel_models import MultilevelModels


def generate_sample_data():
    np.random.seed(42)
    n = 200
    
    df = pd.DataFrame({
        '年龄': np.random.randint(18, 65, n),
        '收入': np.random.normal(8000, 2000, n),
        '满意度': np.random.randint(1, 6, n),
        '工作年限': np.random.randint(0, 40, n),
        '绩效得分': np.random.normal(75, 10, n),
        '性别': np.random.choice(['男', '女'], n),
        '部门': np.random.choice(['销售', '技术', '市场', '人事'], n),
        '培训': np.random.choice([0, 1], n),
        '离职': np.random.choice([0, 1], n)
    })
    
    df['收入'] = df['收入'].mask(np.random.random(n) < 0.05)
    
    return df


def main():
    print("=" * 60)
    print("AnalyX 专业统计数学库 - 使用示例")
    print("=" * 60)
    
    df = generate_sample_data()
    print("\n1. 示例数据已生成:")
    print(df.head())
    
    stats_lib = StatsLibrary(df)
    print("\n2. 数据管理功能:")
    print(f"   数值列: {stats_lib.get_numeric_columns()}")
    print(f"   分类列: {stats_lib.get_categorical_columns()}")
    
    print("\n3. 描述性统计:")
    desc_stats = DescriptiveStats.summary(df, ['年龄', '收入', '绩效得分'])
    print(desc_stats)
    
    print("\n4. 频数分析:")
    freq = DescriptiveStats.frequency_table(df['部门'])
    print(freq)
    
    print("\n5. 独立样本t检验:")
    male_income = df[df['性别'] == '男']['收入'].dropna()
    female_income = df[df['性别'] == '女']['收入'].dropna()
    t_test = HypothesisTests.independent_samples_t_test(male_income, female_income)
    print(f"   t统计量: {t_test['统计量']:.4f}, p值: {t_test['p值']:.4f}")
    
    print("\n6. 卡方检验:")
    chi2_test = HypothesisTests.chi_square_test(df, '性别', '部门')
    print(f"   卡方统计量: {chi2_test['卡方统计量']:.4f}, p值: {chi2_test['p值']:.4f}")
    
    print("\n7. Pearson相关分析:")
    corr = CorrelationAnalysis.pearson_correlation(df['工作年限'], df['收入'])
    print(f"   相关系数: {corr['Pearson相关系数']:.4f}, p值: {corr['p值']:.4f}")
    
    print("\n8. 简单线性回归:")
    try:
        regression = RegressionAnalysis.simple_linear_regression(df, '收入', '工作年限')
        print(f"   R平方: {regression['R平方']:.4f}")
        print(f"   系数: {regression['系数']}")
    except Exception as e:
        print(f"   回归分析执行失败: {e}")
    
    print("\n9. 单因素方差分析:")
    try:
        anova = ANOVA.one_way_anova(df, '部门', '收入')
        print(f"   F统计量: {anova['F统计量']:.4f}, p值: {anova['p值']:.4f}")
    except Exception as e:
        print(f"   方差分析执行失败: {e}")
    
    print("\n10. K-Means聚类:")
    try:
        clustering = ClusterAnalysis.kmeans_clustering(df[['年龄', '收入', '工作年限']], n_clusters=3)
        print(f"    聚类数: {clustering['聚类结果']['聚类'].nunique()}")
        print(f"    聚类中心:\n{clustering['聚类中心']}")
    except Exception as e:
        print(f"    聚类分析执行失败: {e}")
    
    print("\n11. 机器学习 - 随机森林:")
    try:
        rf = MachineLearning.random_forest(df, '离职', ['年龄', '收入', '工作年限', '绩效得分'], 
                                        classification=True)
        print(f"    准确率: {rf['准确率']:.4f}")
        print(f"    特征重要性:\n{rf['特征重要性']}")
    except Exception as e:
        print(f"    随机森林执行失败: {e}")
    
    print("\n" + "=" * 60)
    print("示例运行完成!")
    print("=" * 60)


if __name__ == '__main__':
    main()
