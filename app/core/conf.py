from pydantic import BaseSettings
from sqlalchemy.sql.type_api import INDEXABLE


class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    API_V1: dict = {"prefix": API_V1_STR}
    PROJECT_NAME: str = "Simplyjet Blog API"
    OPENAPI_URL_PREFIX: str = "/api/v1/openapi.json"
    DEBUG: bool = True
    SECRET_KEY: str = "70bfacfb6cbf80efb37f4bc12aa190c39744dead830a658cf91e3af56c732abf"

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_DATABASE: str = "simplyjet_blog"
    DB_URI: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

    # Security settings
    JWT_SECRET_KEY: str = "c2d7ebbb6274a06756ee717984c9e3195b7f05ee481013154c4c4de7f8333aaa"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRATION_MINUTE: int = 15  # 15 minutes
    JWT_REFRESH_TOKEN_EXPIRATION_MINUTE: int = 60 * 24 * 3  # 3 days

    # Email settings
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48


settings = Settings()
