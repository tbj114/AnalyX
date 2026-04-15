import os
import pandas as pd


class FileHandler:
    @staticmethod
    def load_file(file_path):
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.csv':
                # Try different encodings to handle Chinese characters
                encodings = ['utf-8', 'gbk', 'utf-8-sig', 'cp936']
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        return df
                    except:
                        continue
                # If all encodings fail, try without encoding specification
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
                # Use utf-8-sig to handle Chinese characters properly
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif ext in ['.xlsx', '.xls']:
                df.to_excel(file_path, index=False)
            else:
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
        except Exception as e:
            raise e
