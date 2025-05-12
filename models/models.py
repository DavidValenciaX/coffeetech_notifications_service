from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Notification States
class NotificationStates(Base):
    __tablename__ = 'notification_states'
    notification_state_id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False, unique=True)
    notifications = relationship("Notifications", back_populates="state")

# Notification Types
class NotificationTypes(Base):
    __tablename__ = 'notification_types'
    notification_type_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    notifications = relationship("Notifications", back_populates="notification_type")

# Notifications
class Notifications(Base):
    __tablename__ = 'notifications'
    notification_id = Column(Integer, primary_key=True)
    message = Column(String(255), nullable=True)
    notification_date = Column(DateTime(timezone=True), nullable=False)
    invitation_id = Column(Integer, nullable=False)
    notification_type_id = Column(Integer, ForeignKey('notification_types.notification_type_id', ondelete="CASCADE"), nullable=False)
    notification_state_id = Column(Integer, ForeignKey('notification_states.notification_state_id'), nullable=False)
    user_id = Column(Integer, nullable=False)

    notification_type = relationship("NotificationTypes")
    state = relationship("NotificationStates")
