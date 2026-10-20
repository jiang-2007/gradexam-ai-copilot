"""文档加载器：支持 PDF / Word / TXT"""
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings


def load_document(file_path: str):
    """加载单个文档并返回 Document 列表"""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in (".txt", ".md"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"不支持的文件格式: {ext}")

    documents = loader.load()
    return documents


def split_documents(documents):
    """切分文档为 chunk"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", ";", " ", ""],
    )
    return splitter.split_documents(documents)


def load_and_split(file_path: str):
    """一站式：加载 + 切分"""
    docs = load_document(file_path)
    return split_documents(docs)
