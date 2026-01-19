from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    JWT_SECRET: str

    # Mail
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # ignore any future unused env vars safely
        case_sensitive=False,
    )


settings = Settings()
