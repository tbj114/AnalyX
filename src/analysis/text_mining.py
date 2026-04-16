import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any


class TextMining:
    @staticmethod
    def tfidf_vectorization(texts: pd.Series, max_features: int = 1000,
                            ngram_range: Tuple[int, int] = (1, 1)) -> Dict[str, Any]:
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        texts_clean = texts.dropna()
        
        tfidf = TfidfVectorizer(max_features=max_features, ngram_range=ngram_range, 
                                 stop_words='english')
        tfidf_matrix = tfidf.fit_transform(texts_clean)
        
        return {
            '向量化器': tfidf,
            'TF-IDF矩阵': tfidf_matrix,
            '特征词': tfidf.get_feature_names_out()
        }
    
    @staticmethod
    def count_vectorization(texts: pd.Series, max_features: int = 1000,
                           ngram_range: Tuple[int, int] = (1, 1)) -> Dict[str, Any]:
        from sklearn.feature_extraction.text import CountVectorizer
        
        texts_clean = texts.dropna()
        
        count = CountVectorizer(max_features=max_features, ngram_range=ngram_range, 
                               stop_words='english')
        count_matrix = count.fit_transform(texts_clean)
        
        return {
            '向量化器': count,
            '词频矩阵': count_matrix,
            '特征词': count.get_feature_names_out()
        }
    
    @staticmethod
    def sentiment_analysis(texts: pd.Series) -> Dict[str, Any]:
        try:
            from textblob import TextBlob
        except ImportError:
            raise ImportError("TextBlob is required for sentiment analysis. "
                            "Please install with: pip install textblob")
        
        texts_clean = texts.dropna()
        
        sentiments = []
        for text in texts_clean:
            blob = TextBlob(str(text))
            sentiments.append({
                '极性': blob.sentiment.polarity,
                '主观性': blob.sentiment.subjectivity
            })
        
        sentiments_df = pd.DataFrame(sentiments, index=texts_clean.index)
        
        return {
            '情感分析结果': sentiments_df,
            '平均极性': sentiments_df['极性'].mean(),
            '平均主观性': sentiments_df['主观性'].mean()
        }
    
    @staticmethod
    def topic_modeling(texts: pd.Series, n_topics: int = 5, 
                       max_features: int = 1000) -> Dict[str, Any]:
        from sklearn.decomposition import LatentDirichletAllocation
        from sklearn.feature_extraction.text import CountVectorizer
        
        texts_clean = texts.dropna()
        
        count = CountVectorizer(max_features=max_features, stop_words='english')
        count_matrix = count.fit_transform(texts_clean)
        
        lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
        lda.fit(count_matrix)
        
        feature_names = count.get_feature_names_out()
        topics = []
        for topic_idx, topic in enumerate(lda.components_):
            top_words = [feature_names[i] for i in topic.argsort()[:-11:-1]]
            topics.append({
                '主题': topic_idx + 1,
                '关键词': top_words
            })
        
        topic_distributions = lda.transform(count_matrix)
        
        return {
            'LDA模型': lda,
            '主题': topics,
            '主题分布': topic_distributions,
            '困惑度': lda.perplexity(count_matrix)
        }
    
    @staticmethod
    def word_cloud(texts: pd.Series, max_words: int = 100) -> Dict[str, Any]:
        try:
            from wordcloud import WordCloud
        except ImportError:
            raise ImportError("wordcloud is required for word cloud generation. "
                            "Please install with: pip install wordcloud")
        
        texts_clean = texts.dropna()
        combined_text = ' '.join(str(text) for text in texts_clean)
        
        wordcloud = WordCloud(max_words=max_words, background_color='white', 
                             width=800, height=400).generate(combined_text)
        
        return {
            '词云对象': wordcloud,
            '词频': wordcloud.words_
        }
    
    @staticmethod
    def keyword_extraction(texts: pd.Series, top_n: int = 10) -> Dict[str, Any]:
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        texts_clean = texts.dropna()
        combined_text = [' '.join(str(text) for text in texts_clean)]
        
        tfidf = TfidfVectorizer(stop_words='english', max_features=top_n * 2)
        tfidf_matrix = tfidf.fit_transform(combined_text)
        
        feature_names = tfidf.get_feature_names_out()
        tfidf_scores = tfidf_matrix.toarray()[0]
        
        keywords = pd.DataFrame({
            '关键词': feature_names,
            'TF-IDF分数': tfidf_scores
        }).sort_values('TF-IDF分数', ascending=False).head(top_n)
        
        return {
            '关键词': keywords
        }
    
    @staticmethod
    def text_similarity(texts: pd.Series, method: str = 'cosine') -> Dict[str, Any]:
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        texts_clean = texts.dropna()
        
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(texts_clean)
        
        if method == 'cosine':
            similarity_matrix = cosine_similarity(tfidf_matrix)
        
        return {
            '相似性矩阵': similarity_matrix,
            '平均相似性': similarity_matrix.mean()
        }
