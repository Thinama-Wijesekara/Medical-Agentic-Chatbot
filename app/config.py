import os
import certifi
from dotenv import load_dotenv

# --- AUTOMATIC SSL FIX FOR CONDA/PYTHON ENVIRONMENTS ---
ssl_cert = os.environ.get('SSL_CERT_FILE')
if ssl_cert and not os.path.exists(ssl_cert):
    os.environ['SSL_CERT_FILE'] = certifi.where()
elif not ssl_cert:
    os.environ['SSL_CERT_FILE'] = certifi.where()
# --------------------------------------------------------

load_dotenv()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    azure_openai_api_key: str = ''
    azure_openai_endpoint: str = ''
    azure_openai_api_version: str = '2024-10-21'
    azure_embed_deployment: str = 'text-embedding-3-small'
    azure_chat_deployment: str = 'gpt-4.1-mini'
    azure_vision_model: str = 'gpt-4.1-mini'
    pinecone_api_key: str = ''
    tavily_api_key: str = ''
    pinecone_index: str = 'medical-agent-demo'
    api_token: str = ''
    azure_whisper_deployment: str = 'whisper'
    azure_tts_deployment: str = 'tts'
    allowed_origins: str = 'http://localhost:8000,http://127.0.0.1:8000'
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()