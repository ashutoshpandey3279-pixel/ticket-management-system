from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str


class TicketCreate(BaseModel):
    title: str
    description: str
    priority: str
    category: str


class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None


class TicketStatusUpdate(BaseModel):
    status: str