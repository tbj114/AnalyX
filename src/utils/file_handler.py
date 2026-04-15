import os
import pandas as pd


class FileHandler:
    @staticmethod
    def load_file(file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                df = pd.read_csv(file_path)
            elif ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            elif ext == '.sav':
                import pyreadstat
                df, _ = pyreadstat.read_sav(file_path)
            else:
                raise ValueError('不支持的文件格式')
            return df
        except Exception as e:
            raise e
    
    @staticmethod
    def save_to_file(df, file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                df.to_csv(file_path, index=False)
            elif ext in ['.xlsx', '.xls']:
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False)
        except Exception as e:
            raise e
