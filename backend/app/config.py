import os

class Settings:
    app_name = "Disaster Relocation DSS"
    api_prefix = "/api"
    debug = True
    db_path = os.path.join(os.path.dirname(__file__), '..', 'disaster_relocation.db')

settings = Settings()
