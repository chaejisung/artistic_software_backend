from dotenv import load_dotenv
load_dotenv()  

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    KAKAO_CLIENT_ID: str
    KAKAO_CLIENT_SECRET: str
    KAKAO_REDIRECT_URI: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    SECRET_KEY: str
    
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    MONGODB_DB_NAME: Optional[str] = None
    
    URL_ADDRESS: str
    BACKEND_PATH: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
