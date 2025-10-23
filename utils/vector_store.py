import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any, Tuple
import pickle

from config.settings import settings


class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer(settings.LOCAL_MODEL_PATH)
        self.index = None
        self.documents = []
        self.bm25_index = None
        self.doc_id_to_index = {}

    def create_index(self, documents: List[Dict[str, Any]]):
        """创建FAISS索引和BM25索引"""
        self.documents = documents

        # 准备文本用于嵌入
        texts = []
        for doc in documents:
            # 组合标题和内容进行嵌入
            text = f"{doc['title']} {doc['content']}"
            texts.append(text)

            # 存储文档ID到索引的映射
            doc_id = len(self.documents) - 1
            self.doc_id_to_index[doc['file_path']] = doc_id

        # 创建FAISS索引
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings.astype('float32'))

        # 创建BM25索引
        tokenized_texts = [self._tokenize(text) for text in texts]
        self.bm25_index = BM25Okapi(tokenized_texts)

        # 保存索引
        self._save_index()

    def hybrid_search(self, query: str, top_k: int = 5,
                      content_filter: str = None) -> List[Tuple[int, float, Dict[str, Any]]]:
        """混合搜索：BM25 + 向量相似度"""

        # BM25搜索
        tokenized_query = self._tokenize(query)
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        bm25_indices = np.argsort(bm25_scores)[::-1][:top_k * 2]

        # 向量搜索
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        vector_scores, vector_indices = self.index.search(
            query_embedding.astype('float32'), top_k * 2
        )
        vector_scores = vector_scores[0]
        vector_indices = vector_indices[0]

        # 合并结果
        combined_scores = {}
        for idx, score in zip(bm25_indices, bm25_scores[bm25_indices]):
            combined_scores[idx] = combined_scores.get(idx, 0) + score * 0.3

        for idx, score in zip(vector_indices, vector_scores):
            combined_scores[idx] = combined_scores.get(idx, 0) + score * 0.7

        # 排序并过滤
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        # 应用内容过滤
        filtered_results = []
        for idx, score in sorted_results[:top_k * 2]:
            doc = self.documents[idx]

            if content_filter:
                if content_filter == "含表格" and "【表格】" not in doc['content']:
                    continue
                if content_filter == "含公式" and "【公式】" not in doc['content']:
                    continue

            filtered_results.append((idx, score, doc))

        return filtered_results[:top_k]

    def _tokenize(self, text: str) -> List[str]:
        """简单的分词函数"""
        return text.lower().split()

    def _save_index(self):
        """保存索引到文件"""
        if not os.path.exists(settings.FAISS_INDEX_PATH):
            os.makedirs(settings.FAISS_INDEX_PATH)

        # 保存FAISS索引
        faiss.write_index(self.index, os.path.join(settings.FAISS_INDEX_PATH, "faiss.index"))

        # 保存文档数据和映射
        with open(os.path.join(settings.FAISS_INDEX_PATH, "documents.pkl"), 'wb') as f:
            pickle.dump({
                'documents': self.documents,
                'doc_id_to_index': self.doc_id_to_index
            }, f)

    def load_index(self):
        """从文件加载索引"""
        try:
            # 加载FAISS索引
            self.index = faiss.read_index(os.path.join(settings.FAISS_INDEX_PATH, "faiss.index"))

            # 加载文档数据
            with open(os.path.join(settings.FAISS_INDEX_PATH, "documents.pkl"), 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.doc_id_to_index = data['doc_id_to_index']

            # 重新创建BM25索引
            texts = [f"{doc['title']} {doc['content']}" for doc in self.documents]
            tokenized_texts = [self._tokenize(text) for text in texts]
            self.bm25_index = BM25Okapi(tokenized_texts)

            print("索引加载成功")
            return True
        except Exception as e:
            print(f"索引加载失败: {e}")
            return False