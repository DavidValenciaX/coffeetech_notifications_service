from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
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

    notification_type = relationship("NotificationTypes")
    state = relationship("NotificationStates")
    devices = relationship("NotificationDevices", back_populates="notification", cascade="all, delete-orphan")

# User Devices
class UserDevices(Base):
    __tablename__ = 'user_devices'
    user_device_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    fcm_token = Column(String(255), nullable=False) 
    devices = relationship("NotificationDevices", back_populates="user_device", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'fcm_token', name='uq_user_fcm_token'),
    )

# Notification Devices
class NotificationDevices(Base):
    __tablename__ = 'notification_devices'
    notification_device_id = Column(Integer, primary_key=True)
    notification_id = Column(Integer, ForeignKey('notifications.notification_id', ondelete="CASCADE"), nullable=False)
    user_device_id = Column(Integer, ForeignKey('user_devices.user_device_id', ondelete="CASCADE"), nullable=False)

    notification = relationship("Notifications", back_populates="devices")
    user_device = relationship("UserDevices", back_populates="devices")

    __table_args__ = (
        UniqueConstraint('notification_id', 'user_device_id', name='uq_notification_user_device'),
    )
