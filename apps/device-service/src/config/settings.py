from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RobynSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ROBYN_")

    HOST: str = Field("0.0.0.0", min_length=1)
    PORT: int = Field(8082, ge=1, le=65535)


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    URL: str = Field("postgresql+asyncpg://postgres:postgres@localhost:5432/devices_db")


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    BOOTSTRAP_SERVERS: str = Field("localhost:9092")
    COMMANDS_TOPIC: str = Field("device-commands")
    STATUS_TOPIC: str = Field("device-status")
    CONSUMER_GROUP: str = Field("device-service")


class Settings(BaseSettings):
    ROBYN: RobynSettings = Field(default_factory=RobynSettings)
    DATABASE: DatabaseSettings = Field(default_factory=DatabaseSettings)
    KAFKA: KafkaSettings = Field(default_factory=KafkaSettings)


settings = Settings()
