from models.models import UserDevices

def register_or_get_device_use_case(db, fcm_token, user_id=None):
    """
    Busca un dispositivo por FCM token. Si no existe, lo crea.
    """
    device = db.query(UserDevices).filter(UserDevices.fcm_token == fcm_token).first()
    if device:
        # Si existe, opcionalmente actualiza el user_id si es diferente y está presente
        if user_id and device.user_id != user_id:
            device.user_id = user_id
            db.commit()
        return device
    else:
        # Si no existe, lo crea
        new_device = UserDevices(
            user_id=user_id if user_id else 0,
            fcm_token=fcm_token
        )
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device
