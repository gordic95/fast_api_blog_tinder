from typing import Optional
from pydantic import BaseModel

class PostCreate(BaseModel):
    title: str
    content: Optional[str] = None



