from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # === Core AI ===
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # === Event APIs ===
    eventbrite_api_key: str = ""
    serpapi_key: str = ""
    ticketmaster_api_key: Optional[str] = None

    # === Server ===
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"

    # === Vector DB ===
    vector_db_path: str = "./data/chroma_db"
    collection_name: str = "superexpat_knowledge"
    embedding_model: str = "all-MiniLM-L6-v2"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )
    
    def validate_api_keys(self):
        """Check which API keys are configured"""
        issues = []
        
        if not self.eventbrite_api_key:
            issues.append("⚠ EVENTBRITE_API_KEY not set in .env file")
        
        if not self.serpapi_key:
            issues.append("⚠ SERPAPI_KEY not set in .env file")
        
        if issues:
            print("\n" + "="*60)
            print("API KEY CONFIGURATION WARNING")
            print("="*60)
            for issue in issues:
                print(issue)
            print("\nTo fix this:")
            print("1. Copy .env.example to .env")
            print("2. Add your API keys to the .env file")
            print("3. Get API keys from:")
            print("   - Eventbrite: https://www.eventbrite.com/platform/api")
            print("   - SerpAPI: https://serpapi.com/manage-api-key")
            print("="*60 + "\n")
        
        return len(issues) == 0


settings = Settings()

# Validate on startup
settings.validate_api_keys()
