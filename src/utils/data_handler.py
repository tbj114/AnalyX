import numpy as np
import pandas as pd


class DataHandler:
    @staticmethod
    def create_empty_table(rows=100, cols=100):
        columns = [f'变量{i}' for i in range(1, cols + 1)]
        data = {col: pd.Series(dtype='float64') for col in columns}
        df = pd.DataFrame(data)
        df = df.reindex(range(rows))
        return df
    
    @staticmethod
    def load_sample_data():
        np.random.seed(42)
        n = 100
        df = pd.DataFrame({
            '年龄': np.random.randint(18, 60, n),
            '收入': np.random.normal(8000, 2000, n),
            '满意度': np.random.randint(1, 6, n),
            '工作年限': np.random.randint(0, 30, n),
            '绩效得分': np.random.normal(75, 10, n)
        })
        return df
