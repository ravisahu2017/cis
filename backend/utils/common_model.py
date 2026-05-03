from pydantic import BaseModel, Field
from typing import Optional, Any, List
from datetime import datetime

class HttpBaseResponse(BaseModel):
    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if any")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")

class PaginationResponse(BaseModel):
    total: int = Field(description="Total number of items")
    limit: int = Field(description="Number of items per page")
    offset: int = Field(description="Current offset")
    has_more: bool = Field(description="Whether there are more items")
    items: List[Any] = Field(description="List of items")