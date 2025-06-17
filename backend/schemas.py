from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    title: str
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoOut(TodoBase):
    id: int

    class Config:
        from_attributes = True  # позволяет FastAPI читать данные из ORM-модели

class TodoUpdate(BaseModel):
    completed: Optional[bool]

    class Config:
        from_attributes = True