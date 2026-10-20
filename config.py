"""全局配置"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM
    llm_base_url: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
    llm_api_key: str = os.getenv("LLM_API_KEY", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "deepseek-r1:7b")

    # Embedding
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")

    # RAG
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "./data/chroma_db")

    # 全网检索（博查搜索）
    bocha_api_key: str = os.getenv("BOCHA_API_KEY", "")
    bocha_search_url: str = os.getenv("BOCHA_SEARCH_URL", "https://api.bochaai.com/v1/web-search")

    # 飞书
    feishu_app_id: str = os.getenv("FEISHU_APP_ID", "")
    feishu_app_secret: str = os.getenv("FEISHU_APP_SECRET", "")
    feishu_verification_token: str = os.getenv("FEISHU_VERIFICATION_TOKEN", "")
    feishu_encrypt_key: str = os.getenv("FEISHU_ENCRYPT_KEY", "")

    # 服务
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")


settings = Settings()
