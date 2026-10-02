from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    page_content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

upload_progress = {}