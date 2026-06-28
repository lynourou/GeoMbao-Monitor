from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "GeoMbao Monitor"

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "foret_mbao"
    DB_USER: str = "postgres"
    DB_PASSWORD: str

    class Config:
        env_file = ".env"


settings = Settings()