from pydantic import BaseModel
from typing import List, Optional


# ======================
# Request Model
# ======================
class ChatRequest(BaseModel):
    message: str
    page: Optional[int] = 1
    page_size: Optional[int] = 10


# ======================
# Result Model
# ======================
class EventResult(BaseModel):
    id: Optional[str]
    type: str
    title: str
    poster: Optional[str]
    start_date: Optional[str]
    start_time: Optional[str]
    timezone: Optional[str]
    venue: Optional[str]
    address: Optional[str]
    price: Optional[str]
    source: str
    url: Optional[str]


# ======================
# Pagination Model
# ======================
class Pagination(BaseModel):
    page: int
    page_size: int


# ======================
# Response Model
# ======================
class ChatResponse(BaseModel):
    intent: str
    query: str
    location: str
    total_results: int
    results: List[EventResult]
    pagination: Pagination
