from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title cannot be empty")
    description: Optional[str] = None
    is_completed: bool = False
    priority: str = Field(default="low", description="Priority must be low, medium, or high")

    # Strict Validation for Priority
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v: str) -> str:
        valid_priorities = ['low', 'medium', 'high']
        if v.lower() not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
        return v.lower()

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        # This format ensures timezone awareness (e.g., adds +00:00 or Z)
        json_encoders = {
            datetime: lambda v: v.astimezone().isoformat()
        }