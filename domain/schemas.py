from pydantic import BaseModel, ConfigDict
from typing import Optional, List
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

class NotificationStateResponse(BaseModel):
    notification_state_id: int
    name: str

class NotificationTypeResponse(BaseModel):
    notification_type_id: int
    name: str

class NotificationDetailResponse(BaseModel):
    notification_id: int
    message: Optional[str]
    notification_date: datetime
    invitation_id: int
    notification_type_id: int
    notification_state_id: int
    user_id: int

class NotificationByInvitationResponse(BaseModel):
    notification_id: Optional[int]

class DeleteNotificationsResponse(BaseModel):
    deleted_count: int

class SendNotificationResponse(BaseModel):
    notification_id: int
    devices_notified: int
    invalid_tokens: Optional[List[str]] = None
    fcm_errors: Optional[List[dict]] = None
