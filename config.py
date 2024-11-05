from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "porcalabs.com"
    DB_USER: str = "u1609838_miftahsebi"
    DB_PASSWORD: str = "Miftah99"
    DB_NAME: str = "u1609838_sebi_db"

settings = Settings()

