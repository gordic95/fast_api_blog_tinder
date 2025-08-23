from typing import Optional, List
from pydantic import BaseModel, Field



class PostCreate(BaseModel):
    title: str
    content: Optional[str] = None
    categories: Optional[List[int]] = []

class PostListScheme(PostCreate):
    # categories: List["CategoryScheme"]
    pass

