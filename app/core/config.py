from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "grpc-auth-service"
    APP_ENV: str = "development"
    DEBUG: bool = True

    GRPC_PORT: int = 50051

    MONGO_URI: str
    MONGO_DB: str

    REDIS_URL: str
    RABBITMQ_URL: str

    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OTP_LENGTH: int = 6
    OTP_TTL_SECONDS: int = 120
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RESEND_INTERVAL_SECONDS: int = 60

    SMS_PROVIDER: str = "kavenegar"
    KAVENEGAR_API_KEY: str = ""
    KAVENEGAR_TEMPLATE: str = "verify"

    YEKTASMS_API_KEY: str = ""
    YEKTASMS_SENDER: str = ""

    RABBITMQ_SMS_QUEUE: str = "sms_queue"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
