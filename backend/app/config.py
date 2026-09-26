import os

class Settings:
    PROJECT_NAME: str = "Citizen Rights and Government Scheme Navigator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    @property
    def DATABASE_URL(self) -> str:
        if "DATABASE_URL" in os.environ:
            return os.environ["DATABASE_URL"]
        import socket
        try:
            socket.gethostbyname("minor_postgres")
            return "postgresql+psycopg2://postgres:postgrespassword@minor_postgres:5432/schemes_db"
        except (socket.gaierror, Exception):
            return "postgresql+psycopg2://postgres:postgrespassword@localhost:5432/schemes_db"
    
    # Embedding
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    
    # Groq & LLM Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Hybrid Retrieval Defaults
    DEFAULT_TOP_K: int = 5
    FTS_WEIGHT: float = 0.8
    DENSE_WEIGHT: float = 0.2
    RRF_K: int = 60

settings = Settings()
