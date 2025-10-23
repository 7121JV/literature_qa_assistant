import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API配置
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    # 模型路径
    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", "./models/all-MiniLM-L6-v2")

    # 文件路径
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./data/faiss_index")
    PROCESSED_DATA_PATH = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
    RAW_DATA_PATH = "./data/raw"

    # 缓存配置
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

    # 支持的文档格式
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.docx', '.pptx', '.xlsx', '.pdf',
        '.caj', '.enw', '.ris', '.tex', '.jpg', '.png'
    }


settings = Settings()