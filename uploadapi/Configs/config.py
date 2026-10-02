import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    chunk_size: int = 1000
    chunk_overlap: int = 200
    upload_dir: str = os.path.join(os.getcwd(), "uploads")

    @model_validator(mode="after")
    def _check_chunking(self):
        if self.chunk_size <= 0:
            raise ValueError("CHUNK_SIZE must be > 0")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be >= 0 and < CHUNK_SIZE")
        return self

settings = Settings()
print(settings.upload_dir)
