from models.models import UserDevices
import logging

logger = logging.getLogger(__name__)

def register_device(db, fcm_token, user_id):
    """
    Busca un dispositivo por la combinación de FCM token y user_id. 
    Si no existe, lo crea. Permite que un mismo fcm_token esté asociado a múltiples user_id.
    """
    
    # Buscar si ya existe esta combinación específica de token y usuario
    device = db.query(UserDevices).filter(
        UserDevices.fcm_token == fcm_token,
        UserDevices.user_id == user_id
    ).first()

    if device:
        # Si ya existe la combinación exacta, simplemente la retornamos
        logger.info(f"Combinación existente encontrada para fcm_token: {fcm_token} y user_id: {user_id}")
        return device
    else:
        # Si no existe la combinación, creamos un nuevo registro
        logger.info(f"Creando nuevo registro para fcm_token: {fcm_token} y user_id: {user_id}")
        new_device = UserDevices(
            user_id=user_id,
            fcm_token=fcm_token
        )
        db.add(new_device)
        db.commit()
        db.refresh(new_device)
        return new_device
