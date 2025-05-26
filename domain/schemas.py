from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    notification_id: int
    message: Optional[str]
    notification_date: datetime
    invitation_id: int
    notification_type: Optional[str]
    notification_state: Optional[str]

    model_config = ConfigDict(from_attributes=True)

class UpdateNotificationStateRequest(BaseModel):
    notification_state_id: int

class SendNotificationRequest(BaseModel):
    message: str
    user_id: int
    notification_type_id: int
    invitation_id: int
    notification_state_id: int
    fcm_token: Optional[str] = None
    fcm_title: Optional[str] = None
    fcm_body: Optional[str] = None
