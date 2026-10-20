"""ChromaDB 向量存储"""
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from config import settings


_embedding = None
_vectorstore = None


def get_embedding():
    global _embedding
    if _embedding is None:
        _embedding = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding


def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        os.makedirs(settings.vector_store_path, exist_ok=True)
        _vectorstore = Chroma(
            persist_directory=settings.vector_store_path,
            embedding_function=get_embedding(),
        )
    return _vectorstore


def add_documents(documents):
    """向向量库添加文档"""
    vs = get_vectorstore()
    vs.add_documents(documents)
    return len(documents)


def similarity_search(query: str, k: int = 4):
    """相似度检索"""
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)
