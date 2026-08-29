from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Disaster Relocation DSS"
    api_prefix: str = "/api"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
