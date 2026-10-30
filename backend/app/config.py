import os
from dotenv import load_dotenv

# Load .env from workspace root or current directory
_current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_current_dir, "../../.env"))
load_dotenv(os.path.join(_current_dir, "../.env"))
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Autonomous Government Scheme Crawler Agent"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"

    # LLM Keys & Models (Groq high-speed inference)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
    GROQ_FALLBACK_MODEL: str = os.getenv("GROQ_FALLBACK_MODEL", "qwen/qwen3.8-27b")
    LLM_TIMEOUT_SECONDS: float = float(os.getenv("LLM_TIMEOUT_SECONDS", "10.0"))
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Crawler Settings
    CRAWLER_USER_AGENT: str = "GovSchemeCrawlerAgent/2.0 (Official Indian Welfare Scheme Navigator; citizen-aid)"
    CRAWLER_TIMEOUT_SECONDS: int = 12
    CACHE_TTL_HOURS: int = 48

settings = Settings()
