from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SafeRoute AI"
    database_url: str = "sqlite:///./saferoute.db"
    tomtom_api_key: str = ""
    tomtom_flow_endpoint: str = "https://api.tomtom.com/traffic/services/4/flowSegmentData/relative/10/json"
    tomtom_incident_endpoint: str = ""
    cors_origins: str = "http://127.0.0.1:5500,http://localhost:5500,http://127.0.0.1:8080,http://localhost:8080"
    request_timeout_seconds: float = 10.0
    model_path: str = "../ml/models/risk_model.joblib"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
