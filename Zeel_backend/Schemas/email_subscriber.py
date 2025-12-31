from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailSubscriberBase(BaseModel):
    email: EmailStr
    is_active: bool = True

class EmailSubscriberCreate(EmailSubscriberBase):
    pass

class EmailSubscriberResponse(EmailSubscriberBase):
    id: int
    created_date: datetime
    last_sent_date: Optional[datetime] = None

    class Config:
        from_attributes = True