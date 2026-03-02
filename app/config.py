"""
Configuration for the Query Tagger service.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # App
    app_name: str = "Query Tagger"
    debug: bool = False
    
    # LLM Provider (groq, openai, gemini, grok)
    llm_provider: str = "groq"
    
    # API Keys
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None
    
    # API Base URLs (configurable for proxies/self-hosted)
    groq_api_base_url: str = "https://api.groq.com/openai/v1"
    openai_api_base_url: str = "https://api.openai.com/v1"
    grok_api_base_url: str = "https://api.x.ai/v1"
    
    # Models
    groq_model: str = "llama-3.3-70b-versatile"
    openai_model: str = "gpt-4-turbo-preview"
    gemini_model: str = "gemini-pro"
    grok_model: str = "grok-beta"
    
    # LLM Parameters (for tagging)
    llm_temperature: float = 0.1
    llm_max_tokens: int = 200
    
    # Chat Parameters (higher limits for responses)
    chat_max_tokens: int = 1000
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    timeout: int = 30
    
    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()