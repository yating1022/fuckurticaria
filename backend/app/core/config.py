from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str = "10.126.126.4"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "UrticariaDb"

    QWEATHER_API_KEY: str = ""
    QWEATHER_LOCATION_ID: str = "101230206"
    QWEATHER_CITY: str = "厦门集美"
    QWEATHER_API_DOMAIN: str = "api.qweather.com"

    ACCESS_PASSWORD: str = ""
    SECRET_KEY: str = "change-me-to-a-random-string"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?charset=utf8mb4"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
